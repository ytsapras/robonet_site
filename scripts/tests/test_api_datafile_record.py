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

def test_api_datafile_record():
    """Function to test the recording of a new ARTEMiS DataFile 
    request (submitted to the LCO network) by submitting it to the ROME/REA
    database via API. """
    
    params = {'event': '1',\
              'datafile': '/test/path/datafile.dat',\
              'last_upd': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),\
	      'last_hjd':2455000.00,\
	      'last_mag':22.0,\
	      'ndata':10,\
	      'tel':'LCOGT SAAO A 1m',\
	      'inst':'SAAO 1.0m CCD camera',\
	      'filt':'SDSS-i',\
	      'baseline':22.0,\
	      'g':0.0
             }
    config = {'db_user_id': 'ytsapras', \
                'db_pswd': 'xxxx'
                }
    response = api_tools.submit_datafile_record(config,params)
    
if __name__ == '__main__':
    test_api_datafile_record()
