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
import log_utilities

def test_get_rome_fields():
    
    rome_fields = rome_obs.get_rome_fields()

    assert len(rome_fields) == 20

    f = 'ROME-FIELD-02'

    rome_fields = rome_obs.get_rome_fields(selected_field=f)

    assert len(rome_fields) == 1
    assert rome_fields.keys()[0] == f
    
def test_get_rome_obs():
    
    script_config = {'user_id': 'tester@lco.global', 
                     'proposal_id': 'TEST',
                     'token': 'XXX',
                     'selected_field': None,
                     'log_directory': '.',
                     'log_root_name': 'test_rome_obs'
    
                 }
    log = log_utilities.start_day_log( script_config, 'test_rome_obs' )
    
    rome_field_obs = rome_obs.build_rome_obs(script_config,log=log)
    
    assert len(rome_field_obs) == 60
    
    log_utilities.end_day_log(log)
    

if __name__ == '__main__':
    
    test_get_rome_fields()
    test_get_rome_obs()
    