# -*- coding: utf-8 -*-
"""
Created on Wed Jun 7 09:45 2017

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
from events.models import Field, Operator
from datetime import datetime, timedelta
import api_tools

def test_api_event_record():
    """Function to test the recording of a new event 
    by submitting it to the ROME/REA
    database via API. """
    
    params = {'field': '21',\
              'operator': '1',\
              'ev_ra': '18:00:00',\
	      'ev_dec': '-30:00:00',\
	      'status':'NF',\
	      'anomaly_rank': -1.0,\
	      'year': '2017'
             }
    config = {'db_user_id': 'ytsapras', \
                'db_pswd': 'xxxx'
                }
    response = api_tools.submit_event_record(config,params)
    
if __name__ == '__main__':
    test_api_event_record()
