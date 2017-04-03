# -*- coding: utf-8 -*-
"""
Created on Sun Apr  2 10:28:53 2017

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
import rea_obs

def test_build_rea_obs():
    config = {'user_id': 'tester@lco.global',
              'lco_access': 'XXXX', 
              'proposal_id': 'TEST'}
    obs_requests = rea_obs.build_rea_obs(config)
    assert len(obs_requests) > 0