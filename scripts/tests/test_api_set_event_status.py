# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 10:18:18 2019

@author: rstreet
"""

from os import getcwd, path, remove, environ
from sys import argv
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'../..'))
systempath.append(path.join(cwd,'..'))
from local_conf import get_conf
robonet_site = get_conf('robonet_site')
systempath.append(robonet_site)
environ.setdefault('DJANGO_SETTINGS_MODULE', 'robonet_site.settings')
from django.core import management
from django.conf import settings
from django.utils import timezone
from django import setup
setup()
from events.models import Field, Event
from datetime import datetime, timedelta
import api_tools

def test_api_set_event_status():
    """Function to test the API to change the event status in the ROME/REA
    database."""
    
    config = get_config()
    
    params = {'event_name': 'OGLE-2019-BLG-0385',
              'status': 'AN'}
                
    response = api_tools.submit_event_status(config, params, 
                                             testing=True, verbose=True)
    
    assert 'event status updated' in response
    
def get_config():
    
    config = {}
    
    if len(argv) > 1:
        
        config['db_token'] = argv[1]
        
    else:
        
        config['db_token'] = raw_input('Please enter your ROME/REA database token: ')
    
    return config
    
if __name__ == '__main__':
    
    test_api_set_event_status()
    