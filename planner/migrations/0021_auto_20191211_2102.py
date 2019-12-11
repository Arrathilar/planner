# Generated by Django 2.2.8 on 2019-12-11 19:02

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0020_auto_20191210_1133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='execution',
            name='exec_status',
            field=models.CharField(choices=[('IW', 'В черзі'), ('IP', 'Виконується'), ('OC', 'На перевірці'), ('HD', 'Виконано')], default='IW', max_length=2, verbose_name='Статус виконання'),
        ),
        migrations.AlterField(
            model_name='execution',
            name='part',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(150)], verbose_name='Частка'),
        ),
    ]
