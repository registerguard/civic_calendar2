# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-05 00:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('civic_calendar2', '0004_entity_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entity',
            name='slug',
            field=models.SlugField(blank=True, max_length=100),
        ),
    ]
