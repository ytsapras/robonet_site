# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='robonet_request',
            name='request_type',
            field=models.CharField(default=b'M', max_length=12, choices=[(b'T', b'ToO'), (b'M', b'Monitor'), (b'S', b'Single')]),
        ),
    ]
