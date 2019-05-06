# Generated by Django 2.2.1 on 2019-05-05 11:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DependencyNetwork',
            fields=[
                ('id', models.AutoField(editable=False, primary_key=True, serialize=False)),
                ('aircraft_type', models.CharField(db_index=True, max_length=20, unique=True)),
                ('description', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=200)),
                ('dependency_network', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dependencynetwork.DependencyNetwork')),
            ],
        ),
        migrations.CreateModel(
            name='Dependency',
            fields=[
                ('id', models.AutoField(editable=False, primary_key=True, serialize=False)),
                ('depends_on_task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='depends_on_task', to='dependencynetwork.Task')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task', to='dependencynetwork.Task')),
            ],
        ),
    ]
