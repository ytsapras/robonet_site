# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-07-12 22:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_merge_20170629_1649'),
    ]

    operations = [
        migrations.CreateModel(
            name='TapLima',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(verbose_name=b'Date generated')),
                ('priority', models.CharField(choices=[(b'A', b'REA High'), (b'L', b'REA Low'), (b'B', b'REA Post-High'), (b'N', b'None')], default=b'N', max_length=12)),
                ('tsamp', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=6)),
                ('texp', models.IntegerField(blank=True, default=0)),
                ('nexp', models.IntegerField(blank=True, default=1)),
                ('telclass', models.CharField(blank=True, default=b'1m', max_length=12)),
                ('imag', models.DecimalField(blank=True, decimal_places=2, default=22.0, max_digits=6)),
                ('omega', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('err_omega', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('peak_omega', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('blended', models.BooleanField(default=False)),
                ('visibility', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('cost1m', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('passband', models.CharField(blank=True, default=b'SDSS-i', max_length=12)),
                ('ipp', models.DecimalField(blank=True, decimal_places=3, default=1.0, max_digits=10)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.Event')),
            ],
        ),
        migrations.AlterField(
            model_name='datafile',
            name='g',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=8),
        ),
    ]
