# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-01-25 18:51
from __future__ import unicode_literals

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_auto_20160505_1339'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='anomaly_rank',
            field=models.DecimalField(decimal_places=4, default=Decimal('-1.0'), max_digits=12, verbose_name=b'Anomaly Rank'),
        ),
        migrations.AddField(
            model_name='event',
            name='field',
            field=models.IntegerField(default=-1, verbose_name=b'Field Number'),
        ),
        migrations.AlterField(
            model_name='event',
            name='status',
            field=models.CharField(choices=[(b'NF', b'Not in footprint'), (b'AC', b'active'), (b'MO', b'monitor'), (b'AN', b'anomaly'), (b'EX', b'expired')], default=b'NF', max_length=30, verbose_name=b'Event status'),
        ),
        migrations.AlterField(
            model_name='robonetstatus',
            name='status',
            field=models.CharField(choices=[(b'NF', b'Not in footprint'), (b'AC', b'active'), (b'MO', b'monitor'), (b'AN', b'anomaly'), (b'EX', b'expired')], default=b'NF', max_length=12),
        ),
    ]
