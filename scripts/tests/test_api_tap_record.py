# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 14:03:37 2017

@author: ytsapras
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
from events.models import Field, Event
from datetime import datetime, timedelta
import api_tools

def test_api_tap_record():
    """Function to test the recording of a new TAP 
    request (submitted to the LCO network) by submitting it to the ROME/REA
    database via API. """
    
    params = {'event': '1',\
              'priority': 333.3,\
              'tsamp': 999,\
	      'texp':10,\
	      'priority':'L',\
	      'nexp':1,\
	      'telclass':'1m',\
	      'imag':22.0,\
	      'omega':0.1,\
	      'err_omega':0.1,\
	      'peak_omega':0.1,\
	      'blended':False,\
	      'visibility':3.0,\
	      'cost1m':1.0,\
	      'passband':'SDSS-i',\
	      'ipp':0.5,\
              'timestamp': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
            }
    config = {'db_user_id': 'ytsapras', \
                'db_pswd': 'xxxx'
                }
    response = api_tools.submit_tap_record(config,params)
    
if __name__ == '__main__':
    test_api_tap_record()
