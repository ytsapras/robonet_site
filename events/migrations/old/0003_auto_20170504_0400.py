# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-04 04:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_auto_20170504_0359'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='shiftx',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='shifty',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
