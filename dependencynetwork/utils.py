from dependencynetwork.models import *


def assign_dependents_recursively(task):
    try:
        task.dependencies = []
        task.dependents = []
        dependency_entries = list(Dependency.objects.filter(depends_on_task_id=task.id))
        if dependency_entries:
            for dependency_entry in dependency_entries:
                dependent_task = dependency_entry.task
                assign_dependents_recursively(dependent_task)
                task.dependents.append(dependent_task)
    except Dependency.DoesNotExist:
        task.dependents = list()


def assign_dependencies_recursively(task):
    try:
        task.dependencies = []
        task.dependents = []
        dependency_entries = list(Dependency.objects.filter(task_id=task.id))
        if dependency_entries:
            for dependency_entry in dependency_entries:
                parent_task = dependency_entry.depends_on_task
                assign_dependencies_recursively(parent_task)
                task.dependencies.append(parent_task)

    except Dependency.DoesNotExist:
        task.dependencies = list()
