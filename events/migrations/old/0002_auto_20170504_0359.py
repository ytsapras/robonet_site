# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-04 03:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='shiftx',
        ),
        migrations.RemoveField(
            model_name='image',
            name='shifty',
        ),
    ]
