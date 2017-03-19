# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-13 14:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cook_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredientunittocal',
            name='initialized',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='ingredientunittocal',
            name='ingredient_unit_to_calories',
            field=models.DecimalField(decimal_places=5, max_digits=10, null=True),
        ),
    ]