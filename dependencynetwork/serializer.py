from rest_framework import serializers

from .models import *


class DependencyNetworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DependencyNetwork
        fields = ('id', 'aircraft_type', 'description')


class TaskSerializer(serializers.ModelSerializer):
    dependents = RecursiveField(allow_null=True, allow_empty=True, many=True)

    class Meta:
        model = Task
        fields = ('id', 'name', 'description', 'dependents')

    def create(self, validated_data):
        if not validated_data.get('dependency_network_id'):
            validated_data['dependency_network_id'] = self.initial_data['dependency_network_id']

        return super(TaskSerializer, self).create(validated_data)


class DependencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Dependency
        fields = ('id', 'task', 'depends_on_task')
