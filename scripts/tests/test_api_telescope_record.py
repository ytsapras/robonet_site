# -*- coding: utf-8 -*-
"""
Created on Mon May 22 18:29 2017

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

def test_api_telescope_record():
    """Function to test the recording of a new telescope 
    by submitting it to the ROME/REA
    database via API. """
    
    params = {'operator': '1',\
              'name':'NewTelescope',\
	      'aperture':1.2,\
	      'latitude':-30.32,\
	      'longitude':70.29,\
	      'altitude':1000.0,\
	      'site':'WhoKnows'}
    
    config = {'db_user_id': 'ytsapras', \
                'db_pswd': 'xxxx'}
    
    response = api_tools.submit_telescope_record(config,params)
    
if __name__ == '__main__':
    test_api_telescope_record()
