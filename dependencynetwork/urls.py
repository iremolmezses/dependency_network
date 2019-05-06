from django.conf.urls import url
from django.http import HttpResponseNotAllowed

from . import views


def method_dispatch(**table):
    def invalid_method(request, *args, **kwargs):
        return HttpResponseNotAllowed(table.keys())

    def d(request, *args, **kwargs):
        handler = table.get(request.method, invalid_method)
        return handler(request, *args, **kwargs)
    return d


urlpatterns = [
    url(
        r'^dependency-network/(?P<aircraft_type>[A-Za-z0-9_ ]+)$',
        method_dispatch(GET=views.get_dependency_network,
                        PUT=views.delete_update_dependency_network,
                        DELETE=views.delete_update_dependency_network),
        name='get_delete_update_dependency_network'
    ),
    url(
        r'^dependency-network$',
        method_dispatch(GET=views.get_all_dependency_networks,
                        POST=views.create_dependency_network),
        name='get_create_dependency_networks'
    ),
    url(
        r'^task/(?P<aircraft_type>[A-Za-z0-9_ ]+)/(?P<name>[A-Za-z_ ]+)$',
        method_dispatch(GET=views.get_task,
                        PUT=views.delete_update_task,
                        DELETE=views.delete_update_task),
        name='get_delete_update_task'
    ),
    url(
        r'^task$',
        method_dispatch(POST=views.create_single_task),
        name='get_create_task'
    ),
    url(
        r'^tasks$',
        method_dispatch(POST=views.create_tasks),
        name='create_batch_tasks'
    ),
    url(
        r'^dependency/(?P<aircraft_type>[A-Za-z0-9_ ]+)$',
        method_dispatch(POST=views.create_delete_dependency,
                        DELETE=views.create_delete_dependency),
        name='create_delete_dependency'
    ),
]