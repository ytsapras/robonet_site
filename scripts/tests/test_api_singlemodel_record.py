# -*- coding: utf-8 -*-
"""
Created on Mon Jun 12 09:45 2017

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
from events.models import Operator, Event
from datetime import datetime, timedelta
import api_tools

def test_api_singlemodel_record():
    """Function to test the recording of a new Single Model 
    by submitting it to the ROME/REA
    database via API. """
    
    params = {'event': '1',\
	      'Tmax':2457916.8491,\
	      'e_Tmax':10.0,\
	      'tau':30.0,\
	      'e_tau':1.0,\
	      'umin':0.1,\
	      'e_umin':0.001,\
	      'modeler':'TESTER',\
	      'last_updated':datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
             }
    config = {'db_user_id': 'ytsapras', \
                'db_pswd': 'xxxx'
                }
    response = api_tools.submit_singlemodel_record(config,params)
    
if __name__ == '__main__':
    test_api_singlemodel_record()
