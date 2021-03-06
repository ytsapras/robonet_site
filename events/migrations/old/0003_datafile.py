# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-24 07:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_auto_20170524_0701'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datafile', models.CharField(max_length=1000)),
                ('last_upd', models.DateTimeField(verbose_name=b'date last updated')),
                ('last_hjd', models.DecimalField(decimal_places=8, max_digits=20)),
                ('last_mag', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tel', models.CharField(blank=True, default=b'', max_length=50)),
                ('inst', models.CharField(blank=True, default=b'', max_length=50)),
                ('filt', models.CharField(blank=True, default=b'', max_length=50)),
                ('baseline', models.DecimalField(blank=True, decimal_places=2, default=22.0, max_digits=6)),
                ('g', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=6)),
                ('ndata', models.IntegerField()),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.Event')),
            ],
        ),
    ]
