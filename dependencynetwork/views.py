from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .utils import *
from .serializer import *
from .models import *


@api_view(['GET'])
def get_all_dependency_networks(request):
    networks = DependencyNetwork.objects.all()
    serializer = DependencyNetworkSerializer(networks, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_dependency_network(request, aircraft_type):
    try:
        dependency_network = DependencyNetwork.objects.get(aircraft_type=aircraft_type)
        all_tasks = Task.objects.filter(dependency_network_id=dependency_network.id)
        dependency_entries = Dependency.objects.filter(id__in=list(t.id for t in all_tasks))
        root_tasks = list(all_tasks.exclude(id__in=list(d.task_id for d in dependency_entries)))
        data = []
        for root_task in root_tasks:
            assign_dependents_recursively(root_task)
            data.append(root_task)
        serializer = TaskSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except DependencyNetwork.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE', 'PUT'])
@authentication_classes((SessionAuthentication, BasicAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def delete_update_dependency_network(request, aircraft_type):
    try:
        dependency_network = DependencyNetwork.objects.get(aircraft_type=aircraft_type)
    except DependencyNetwork.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = DependencyNetworkSerializer(dependency_network, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        dependency_network.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@authentication_classes((SessionAuthentication, BasicAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def create_dependency_network(request):
    serializer = DependencyNetworkSerializer(data=request.data)
    if serializer.is_valid():
        try:
            dependency_network = DependencyNetwork.objects.get(aircraft_type=request.data['aircraft_type'])
            # if a dependency network with given name exists, return bad request
            if dependency_network:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except DependencyNetwork.DoesNotExist:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_task(request, aircraft_type, name):
    try:
        dependency_network = DependencyNetwork.objects.get(aircraft_type=aircraft_type)
        task = Task.objects.get(dependency_network_id=dependency_network.id, name=name)
        assign_dependencies_recursively(task)
        assign_dependents_recursively(task)

        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except (DependencyNetwork.DoesNotExist, Task.DoesNotExist):
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE', 'PUT'])
@authentication_classes((SessionAuthentication, BasicAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def delete_update_task(request, aircraft_type, name):
    try:
        dependency_network = DependencyNetwork.objects.get(aircraft_type=aircraft_type)
        task = Task.objects.get(dependency_network_id=dependency_network.id, name=name)
    except (DependencyNetwork.DoesNotExist, Task.DoesNotExist):
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        data = {'dependency_network_id': task.dependency_network_id,
                'name': request.data.get('name', None),
                'description': request.data.get('description', None),
                'dependents': [],
                'dependencies': []}
        serializer = TaskSerializer(data=data)

        if serializer.is_valid():
            data.pop('dependents')
            data.pop('dependencies')
            task = Task.objects.create(**data)

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@authentication_classes((SessionAuthentication, BasicAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def create_single_task(request):
    task = create_task(request.data)
    return Response(status=status.HTTP_201_CREATED) if task else Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes((SessionAuthentication, BasicAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def create_tasks(request):
    main_task = request.data.get('task', None)
    network_id = main_task.get('dependency_network_id', None)
    parent_tasks = request.data.get('dependencies', None)
    children_tasks = request.data.get('dependents', None)

    if parent_tasks and not all(pt.get('dependency_network_id', None) == network_id for pt in parent_tasks):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    if children_tasks and not all(ct.get('dependency_network_id', None) == network_id for ct in children_tasks):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # if so far so good, let's create
    task = create_task(main_task)
    if not task:
        Response(status=status.HTTP_400_BAD_REQUEST)
    partial_failure = False
    if parent_tasks:
        for parent_task in parent_tasks:
            pt = create_task(parent_task)
            if not pt:
                partial_failure = True
            else:
                task_id = pt.id if isinstance(pt, Task) else pt.get('id')
                Dependency.objects.create(task_id=task.id, depends_on_task_id=task_id)
    if children_tasks:
        for children_task in children_tasks:
            ct = create_task(children_task)
            if not ct:
                partial_failure = True
            else:
                task_id = ct.id if isinstance(ct, Task) else ct.get('id')
                Dependency.objects.create(task_id=task_id, depends_on_task_id=task.id)
    return Response(status=status.HTTP_201_CREATED) if not partial_failure else Response(
        status=status.HTTP_206_PARTIAL_CONTENT)


def create_task(data):
    dependency_network_id = data.get('dependency_network_id', None)
    try:
        DependencyNetwork.objects.get(id=dependency_network_id)
        task = Task.objects.get(dependency_network_id=dependency_network_id,
                                name=data['name'])
        # if a task with given data exists, return task
        if task:
            return task
        # if given dependency network not exists, return bad request
    except DependencyNetwork.DoesNotExist:
        return None
    except Task.DoesNotExist:
        pass

    if not data.get('dependents', None):
        data['dependents'] = []
    if not data.get('dependencies', None):
        data['dependencies'] = []

    serializer = TaskSerializer(data=data)
    if serializer.is_valid():
        task = Task.objects.create(dependency_network_id=data['dependency_network_id'],
                                   name=data['name'],
                                   description=data['description'])
        return task
    return None


@api_view(['POST', 'DELETE'])
@authentication_classes((SessionAuthentication, BasicAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def create_delete_dependency(request, aircraft_type):
    try:
        dependency_network = DependencyNetwork.objects.get(aircraft_type=aircraft_type)
        child_task = Task.objects.get(dependency_network_id=dependency_network.id,
                                      name=request.data.get('task'))
        parent_task = Task.objects.get(dependency_network_id=dependency_network.id,
                                       name=request.data.get("depends_on_task"))
    except (Task.DoesNotExist, DependencyNetwork.DoesNotExist):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'POST':
        Dependency.objects.create(task_id=child_task.id, depends_on_task_id=parent_task.id)
        return Response(status=status.HTTP_201_CREATED)
    elif request.method == 'DELETE':
        try:
            dependency = Dependency.objects.get(task_id=child_task.id,
                                                depends_on_task_id=parent_task.id)
            dependency.delete()
            return Response(status=status.HTTP_200_OK)
        except Dependency.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
