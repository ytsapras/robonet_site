# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 21:55:53 2017

@author: rstreet
"""

from os import getcwd, path, remove, environ
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'..'))
from local_conf import get_conf
robonet_site = get_conf('robonet_site')
systempath.append(robonet_site)
environ.setdefault('DJANGO_SETTINGS_MODULE', 'robonet_site.settings')
from django.core import management
from django.conf import settings
from django.utils import timezone
from django import setup
from datetime import datetime, timedelta
setup()
from events.models import Event, SingleModel
import rome_obs

def test_get_rome_fields():
    rome_fields = rome_obs.get_rome_fields()
    print rome_fields.keys()
    assert len(rome_fields) == 2

def test_get_rome_obs():
    script_config = {'user_id': 'rstreet@lco.global', 'proposal_id': 'KEY2017AB-004'}
    rome = rome_obs.build_rome_obs(script_config,log=None)
    print rome.keys()
    for obs in rome:
        print obs.name
    assert rome < -1