# Generated by Django 2.2.10 on 2020-05-06 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0005_auto_20200506_1316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kpi',
            name='name',
            field=models.CharField(choices=[('BI', 'Бонус Ітел-Ісервіс'), ('BG', 'Бонус Галкомпроект'), ('TA', 'Бонуси Загальні'), ('PR', 'Продуктивність')], default='BI', max_length=2, verbose_name='Показник ефективності'),
        ),
    ]
