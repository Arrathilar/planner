# Generated by Django 2.1.7 on 2019-08-21 18:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0012_auto_20190226_1144'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contractor',
            name='project_types',
        ),
    ]
