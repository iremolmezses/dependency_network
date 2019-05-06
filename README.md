# Dependency Network API

Limitation: Due to limited time, couldn't put effort on frontend

1 - Start with making virtual environment using below commands:
python3 -m venv env
source env/bin/activate

2 - install below dependencies
pip install django==2.0.3
pip install djangorestframework 
pip install djangorestframework_recursive

3 - make sure all 25 tests are passing

4- run python manage.py runserver

endpoints:
username->admin, password->5tr0ngPaSsw0rd

* http://127.0.0.1:8000/dependency-network : GET=to view all defined dependency network / post: to create new dependency network

sample json for creation:
{ "aircraft_type":"Boeing 777", "description":"dependency network of Boeing 777 tasks" }

* http://127.0.0.1:8000/dependency/{aircraft_type}
i.e -> http://127.0.0.1:8000/dependency-network/Boeing%20777 : GET=to view the dependency network of Boeing 777, PUT=to update the dependency network of Boeing 777, DELETE: to delete the dependency network of Boeing 777

** dependents are shown, dependencies left blank intentionally for simplicity! Otherwise it might recurse up&down nonstop **

sample json for update:
{ "aircraft_type":"Boeing 737", "description":"dependency network of Boeing 737 tasks" }

* http://127.0.0.1:8000/dependency/{aircraft_type}/{task_name}
i.e -> http://127.0.0.1:8000/task/Boeing%20777/deboarding : GET=to view specified task with relations, PUT=to update the specified task with relations, DELETE: to delete the specified task with relations

sample json for update (dependency_network_id=1 is Boeing 777):
{"dependency_network_id": 1, "name": "renamed task", "description": "and changed the instructions"}

* http://127.0.0.1:8000/task: POST: to create new task

sample json for creation (dependency_network_id=1 is Boeing 777):
{"dependency_network_id": 1, "name": "new task","description": "instructions for new task"}

* http://127.0.0.1:8000/dependency/{aircraft_type}
-> http://127.0.0.1:8000/dependency/Boeing%20777: POST= create dependency between 2 provided task for Boeing 777, DELETE=create dependency between 2 provided task for Boeing 777

sample json for creation/deletion (dependency_network_id=1 is Boeing 777):
{"dependency_network_id": 1, "task": "predecessor task", "depends_on_task": "antecessor task"}
