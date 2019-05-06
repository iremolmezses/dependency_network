from django.db import models
from rest_framework_recursive.fields import RecursiveField


class DependencyNetwork(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    aircraft_type = models.CharField(unique=True, db_index=True, null=False, blank=False, max_length=20)
    description = models.CharField(max_length=200)


class Task(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    dependency_network = models.ForeignKey(DependencyNetwork, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    dependencies = RecursiveField(allow_null=True, allow_empty=True, many=True)
    dependents = RecursiveField(allow_null=True, allow_empty=True, many=True)


class Dependency(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=False, related_name="task")
    depends_on_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=False, related_name="depends_on_task")