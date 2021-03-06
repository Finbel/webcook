# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-14 14:50
from __future__ import unicode_literals

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cook_app', '0002_auto_20170313_1518'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userhistory',
            name='comment',
        ),
        migrations.AlterField(
            model_name='ingredientunittocal',
            name='ingredient_unit_to_calories',
            field=models.DecimalField(decimal_places=5, max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))]),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='quantity_per_serving',
            field=models.DecimalField(decimal_places=5, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))]),
        ),
        migrations.AlterField(
            model_name='userhistory',
            name='servings',
            field=models.PositiveIntegerField(),
        ),
    ]
