# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 14:03:37 2017

@author: rstreet
"""

from os import getcwd, path, remove, environ
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
from events.models import Field
from datetime import datetime, timedelta
import api_tools

def test_api_obs_record():
    """Function to test the recording of a new observation 
    request (submitted to the LCO network) by submitting it to the ROME/REA
    database via API. """
    
    params = {'field': '1',\
              't_sample': 333.3,\
              'exptime': 999,\
              'timestamp': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),\
              'time_expire': (datetime.utcnow() + timedelta(days=1.0)).strftime("%Y-%m-%dT%H:%M:%S")
            }
    config = {'db_user_id': 'rstreet', \
                'db_pswd': 'xxxx'
                }
    response = api_tools.submit_obs_request_record(config,params)
    
if __name__ == '__main__':
    test_api_obs_record()
