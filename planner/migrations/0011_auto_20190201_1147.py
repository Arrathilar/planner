# Generated by Django 2.0.6 on 2019-02-01 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0010_auto_20190126_1336'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='birthday',
            field=models.DateField(blank=True, null=True, verbose_name='День народження'),
        ),
    ]
