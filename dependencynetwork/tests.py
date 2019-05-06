from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.utils import json

from .serializer import DependencyNetworkSerializer
from .models import *


class ApiTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.username = 'test_user'
        self.user = User.objects.create_user(username='test_user',
                                             email='test_user@example.com',
                                             password='F4kePaSsw0rd')
        Token.objects.create(user=self.user)
        super(ApiTest, self).setUp()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user.auth_token.key)

        dependency_network_1 = DependencyNetwork.objects.create(
            aircraft_type="Boeing 777",
            description="dependency network of Boeing 777 tasks")
        dependency_network_2 = DependencyNetwork.objects.create(
            aircraft_type="Airbus A380",
            description="dependency network of Airbus A380 tasks")
        ado = Task.objects.create(
            dependency_network=dependency_network_1, name='ADO', description='ADO')
        Task.objects.create(
            dependency_network=dependency_network_2, name='ADO', description='ADO')
        deboarding = Task.objects.create(
            dependency_network=dependency_network_1, name='deboarding',
            description='some deboarding instructions here for Boeing 777, do this do that...')
        offload_catering = Task.objects.create(
            dependency_network=dependency_network_1, name='offload catering',
            description='some catering instructions here for Boeing 777, do this do that...')
        cleaning = Task.objects.create(
            dependency_network=dependency_network_1, name='cleaning',
            description='some cleaning instructions here for Boeing 777, do this do that...')
        unloading = Task.objects.create(
            dependency_network=dependency_network_1, name='unloading',
            description='some unloading instructions for Boeing 777, do this do that...')
        security_check = Task.objects.create(
            dependency_network=dependency_network_1, name='security check',
            description='some security check instructions here for Boeing 777, do this do that...')
        cabin_check = Task.objects.create(
            dependency_network=dependency_network_1, name='cabin check',
            description='some cabin check instructions here for Boeing 777, do this do that...')
        boarding = Task.objects.create(
            dependency_network=dependency_network_1, name='boarding',
            description='some boarding instructions for Boeing 777, do this do that...')
        adc = Task.objects.create(
            dependency_network=dependency_network_1, name='ADC', description='ADC')

        Dependency.objects.create(task=deboarding, depends_on_task=ado)
        Dependency.objects.create(task=unloading, depends_on_task=ado)
        Dependency.objects.create(task=offload_catering, depends_on_task=deboarding)
        Dependency.objects.create(task=cleaning, depends_on_task=deboarding)
        Dependency.objects.create(task=boarding, depends_on_task=security_check)
        Dependency.objects.create(task=boarding, depends_on_task=cabin_check)
        Dependency.objects.create(task=adc, depends_on_task=boarding)

    def test_get_all_dependency_networks(self):
        # get API response
        response = self.client.get(reverse('get_create_dependency_networks'))
        # get data from db
        dependencynetworks = DependencyNetwork.objects.all()
        serializer = DependencyNetworkSerializer(dependencynetworks, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['aircraft_type'], 'Boeing 777')
        self.assertEqual(response.data[1]['aircraft_type'], 'Airbus A380')

    def test_get_existing_dependency_network_by_type(self):
        response = self.client.get(
            reverse('get_delete_update_dependency_network', kwargs={'aircraft_type': 'Boeing 777'}))
        network = DependencyNetwork.objects.get(aircraft_type='Boeing 777')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_get_non_existing_dependency_network_by_type(self):
        response = self.client.get(
            reverse('get_delete_update_dependency_network', kwargs={'aircraft_type': 'Boeing 666'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_existing_dependency_network_by_type(self):
        # create a dummy, to-be-deleted network first; so the rest of the test cases won't be affected
        DependencyNetwork.objects.create(
            aircraft_type="Boeing 666", description="dependency network of Boeing 666 tasks")
        response = self.client.delete(
            reverse('get_delete_update_dependency_network', kwargs={'aircraft_type': 'Boeing 666'}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_non_existing_dependency_network_by_type(self):
        response = self.client.delete(
            reverse('get_delete_update_dependency_network', kwargs={'aircraft_type': 'Boeing 666'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_existing_dependency_network_by_type_with_valid_data(self):
        # create a dummy, to-be-deleted network first; so the rest of the test cases won't be affected
        DependencyNetwork.objects.create(
            aircraft_type="Boeing 666", description="dependency network of Boeing 666 tasks")
        valid_payload = {
            'aircraft_type': 'Boeing 737',
            'description': 'dependency network of Boeing 737 tasks',
        }
        response = self.client.put(
            reverse('get_delete_update_dependency_network', kwargs={'aircraft_type': 'Boeing 666'}),
            data=json.dumps(valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        network = DependencyNetwork.objects.get(aircraft_type='Boeing 737')
        serializer = DependencyNetworkSerializer(network)
        self.assertIsNotNone(serializer.data)
        self.assertEqual(serializer.data['description'], 'dependency network of Boeing 737 tasks')
        network.delete()

    def test_update_existing_dependency_network_by_type_with_invalid_data(self):
        # create a dummy, to-be-deleted network first; so the rest of the test cases won't be affected
        DependencyNetwork.objects.create(
            aircraft_type="Boeing 666", description="dependency network of Boeing 666 tasks")
        invalid_payload = {
            'aircraft_type': '',
            'description': 'dependency network of unknown aircraft tasks',
        }
        response = self.client.put(
            reverse('get_delete_update_dependency_network', kwargs={'aircraft_type': 'Boeing 666'}),
            data=json.dumps(invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        network = DependencyNetwork.objects.get(aircraft_type='Boeing 666')
        serializer = DependencyNetworkSerializer(network)
        self.assertIsNotNone(serializer.data)  # because it couldn't be updated
        network.delete()

    def test_update_non_existing_dependency_network_by_type(self):
        response = self.client.put(
            reverse('get_delete_update_dependency_network', kwargs={'aircraft_type': 'Boeing 666'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_single_dependency_network(self):
        # dependency network of Boeing 777 already exists (see setup)
        payload = {
            'aircraft_type': 'Boeing 777',
            'description': 'description',
        }
        response = self.client.post(
            reverse('get_create_dependency_networks'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_dependency_network_with_invalid_payload(self):
        invalid_payload = {
            'aircraft_type': '',
            'description': 'description',
        }
        response = self.client.post(
            reverse('get_create_dependency_networks'),
            data=json.dumps(invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_dependency_network_with_valid_payload(self):
        valid_payload = {
            'aircraft_type': 'Boeing 666',
            'description': 'description',
        }
        response = self.client.post(
            reverse('get_create_dependency_networks'),
            data=json.dumps(valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        network = DependencyNetwork.objects.get(aircraft_type='Boeing 666')
        serializer = DependencyNetworkSerializer(network)
        self.assertIsNotNone(serializer.data)  # because created
        network.delete()

    def test_get_non_existing_task_by_type_and_name(self):
        response = self.client.get(
            reverse('get_delete_update_task', kwargs={'aircraft_type': 'Boeing 777', 'name': 'sleep'}))
        # dependency network of Boeing 777 has many tasks but sleeping is not one of them
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_existing_task_by_type_and_name(self):
        response = self.client.get(
            reverse('get_delete_update_task', kwargs={'aircraft_type': 'Boeing 777', 'name': 'boarding'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'],
                         'some boarding instructions for Boeing 777, do this do that...')
        self.assertEqual(len(response.data['dependents']), 1)
        self.assertEqual(response.data['dependents'][0]['name'], 'ADC')

    def test_delete_non_existing_task_by_type_and_name(self):
        response = self.client.delete(
            reverse('get_delete_update_task', kwargs={'aircraft_type': 'Boeing 777',
                                                      'name': 'sleep'}))
        # dependency network of Boeing 777 has many tasks but sleeping is not one of them
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_existing_task_by_type_and_name(self):
        # create a dummy, to-be-deleted task first; so the rest of the test cases won't be affected
        self.assertEqual(len(Task.objects.filter(dependency_network_id=1)), 9)
        Task.objects.create(dependency_network_id=1, name='sleep', description="sleep as all other people working")
        self.assertEqual(len(Task.objects.filter(dependency_network_id=1)), 10)
        response = self.client.delete(
            reverse('get_delete_update_task', kwargs={'aircraft_type': 'Boeing 777',
                                                      'name': 'sleep'}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(Task.objects.filter(dependency_network_id=1)), 9)

    def test_update_non_existing_task_by_type_and_name(self):
        valid_payload = {
            'name': 'do something useful',
            'description': 'instructions',
        }
        response = self.client.put(
            reverse('get_delete_update_task', kwargs={'aircraft_type': 'Boeing 777', 'name': 'sleep'}),
            data=json.dumps(valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_existing_task_by_type_and_name_with_valid_data(self):
        # create a dummy, to-be-deleted task first; so the rest of the test cases won't be affected
        network = DependencyNetwork.objects.get(aircraft_type='Boeing 777')
        Task.objects.create(dependency_network=network,
                            name='sleep',
                            description="sleep as all other people working")

        valid_payload = {
            'name': 'do something useful',
            'description': 'instructions for something useful'
        }
        response = self.client.put(
            reverse('get_delete_update_task', kwargs={'aircraft_type': 'Boeing 777', 'name': 'sleep'}),
            data=json.dumps(valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task = Task.objects.get(name='do something useful')
        self.assertIsNotNone(task)
        self.assertEqual(task.description, 'instructions for something useful')
        task.delete()

    def test_update_existing_task_by_type_and_name_with_invalid_data(self):
        # create a dummy, to-be-deleted task first; so the rest of the test cases won't be affected
        Task.objects.create(dependency_network_id=1, name='sleep', description="sleep as all other people working")

        invalid_payload = {
            'name': '',
            'description': '',
        }
        response = self.client.put(
            reverse('get_delete_update_task', kwargs={'aircraft_type': 'Boeing 777', 'name': 'sleep'}),
            data=json.dumps(invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        task = Task.objects.get(name='sleep')
        self.assertIsNotNone(task)  # because not updated
        self.assertEqual(task.description, 'sleep as all other people working')
        task.delete()

    def test_create_single_task_with_invalid_payload(self):
        invalid_payload = {
            'dependency_network_id': 1,
            'name': '',
            'description': 'invalid',
        }
        response = self.client.post(
            reverse('get_create_task'),
            data=json.dumps(invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_single_task_with_valid_payload(self):
        valid_payload = {
            'dependency_network_id': 1,
            'name': 'x',
            'description': 'instructions for x task',
        }
        response = self.client.post(
            reverse('get_create_task'),
            data=json.dumps(valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(name='x')
        self.assertIsNotNone(task)
        self.assertEqual(task.description, 'instructions for x task')
        task.delete()

    def test_create_multiple_tasks_with_valid_payload(self):
        valid_payload = {
            'task': {
                'dependency_network_id': 1,
                'name': 'new task',
                'description': 'instructions for new task'
            },
            'dependencies': [
                {
                    'dependency_network_id': 1,
                    'name': 'ancestor 1',
                    'description': 'instructions for ancestor 1 task'
                },
                {
                    'dependency_network_id': 1,
                    'name': 'ancestor 2',
                    'description': 'instructions for ancestor 2 task'
                }
            ],
            'dependents': [
                {
                    'dependency_network_id': 1,
                    'name': 'successor 1',
                    'description': 'instructions for successor 1 task'
                },
                {
                    'dependency_network_id': 1,
                    'name': 'successor 2',
                    'description': 'instructions for successor 2 task'
                }
            ]
        }
        response = self.client.post(
            reverse('create_batch_tasks'),
            data=json.dumps(valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        main_task = Task.objects.get(name='new task')
        self.assertIsNotNone(main_task)
        self.assertEqual(main_task.description, 'instructions for new task')
        depency1 = list(Dependency.objects.filter(task_id=main_task.id))
        self.assertEqual(len(depency1), 2)
        self.assertEqual(depency1[0].depends_on_task.name, 'ancestor 1')
        self.assertEqual(depency1[1].depends_on_task.name, 'ancestor 2')

        ancestor1 = Task.objects.get(name='ancestor 1')
        self.assertIsNotNone(ancestor1)
        self.assertEqual(ancestor1.description, 'instructions for ancestor 1 task')

        ancestor2 = Task.objects.get(name='ancestor 2')
        self.assertIsNotNone(ancestor2)
        self.assertEqual(ancestor2.description, 'instructions for ancestor 2 task')

        successor1 = Task.objects.get(name='successor 1')
        self.assertIsNotNone(successor1)
        self.assertEqual(successor1.description, 'instructions for successor 1 task')
        depency2 = list(Dependency.objects.filter(task_id=successor1.id))
        self.assertEqual(len(depency2), 1)
        self.assertEqual(depency2[0].depends_on_task.name, 'new task')

        successor2 = Task.objects.get(name='successor 2')
        self.assertIsNotNone(successor2)
        self.assertEqual(successor2.description, 'instructions for successor 2 task')
        depency3 = list(Dependency.objects.filter(task_id=successor2.id))
        self.assertEqual(len(depency3), 1)
        self.assertEqual(depency3[0].depends_on_task.name, 'new task')

        main_task.delete()
        ancestor1.delete()
        ancestor2.delete()
        successor1.delete()
        successor2.delete()

    def test_create_dependency_with_valid_payload(self):
        # create a dummy, to-be-deleted task first; so the rest of the test cases won't be affected
        task1 = Task.objects.create(dependency_network_id=1, name='sleep',
                                    description="sleep as all other people working")
        task2 = Task.objects.create(dependency_network_id=1, name='dream',
                                    description="dream as all other people working")
        valid_payload = {
            'task': 'dream',
            'depends_on_task': 'sleep',
        }
        response = self.client.post(
            reverse('create_delete_dependency', kwargs={'aircraft_type': 'Boeing 777'}),
            data=json.dumps(valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        dependency = Dependency.objects.get(task_id=task2.id, depends_on_task_id=task1.id)
        self.assertIsNotNone(dependency)
        task1.delete()
        task2.delete()

    def test_create_dependency_with_invalid_payload(self):
        invalid_payload = {
            'task': '',
            'depends_on_task': '',
        }
        response = self.client.post(
            reverse('create_delete_dependency', kwargs={'aircraft_type': 'Boeing 777'}),
            data=json.dumps(invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_existing_dependency(self):
        # create a dummy, to-be-deleted task first; so the rest of the test cases won't be affected
        task1 = Task.objects.create(dependency_network_id=1, name='sleep',
                                    description="sleep as all other people working")
        task2 = Task.objects.create(dependency_network_id=1, name='dream',
                                    description="dream as all other people working")
        Dependency.objects.create(task_id=task2.id, depends_on_task_id=task1.id)

        valid_payload = {
            'task': 'dream',
            'depends_on_task': 'sleep',
        }
        response = self.client.delete(
            reverse('create_delete_dependency', kwargs={'aircraft_type': 'Boeing 777'}),
            data=json.dumps(valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dependency = Dependency.objects.filter(task_id=task2.id, depends_on_task_id=task1.id)
        self.assertEqual(len(dependency), 0)

    def test_delete_non_existing_dependency(self):
        invalid_payload = {
            'task': '',
            'depends_on_task': '',
        }
        response = self.client.post(
            reverse('create_delete_dependency', kwargs={'aircraft_type': 'Boeing 777'}),
            data=json.dumps(invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
