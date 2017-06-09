# -*- coding: utf-8 -*-
"""
Created on Fri May  5 10:18:16 2017

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

def test_api_data_file():
    """Function to test the recording of a new data file 
    via API to the ROME/REA database. """
    
    params = {'name': 'OGLE-2017-BLG-0620',\
              'datafile': '/data/romerea/data/artemis/data/OOB170620I.dat',\
              'last_mag': 17.2,\
              'tel': 'OGLE 1.3m',
              'filt': 'I',
              'baseline': 22.5,
              'g': 18.45,
              'ndata': 2234,
              'last_obs': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),\
              'last_upd': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
            }
    config = {}
    config['db_user_id'] = raw_input('Please enter DB user ID: ')
    config['db_pswd'] = raw_input('Please enter DB password: ')

    response = api_tools.submit_data_file_record(config,params,testing=True)
    print 'Response: ',response
    
if __name__ == '__main__':
    test_api_data_file()