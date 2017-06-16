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
from events.models import Field
from datetime import datetime, timedelta
import api_tools

def test_api_operator_record():
    """Function to test the recording of a new operator 
    by submitting it to the ROME/REA
    database via API. """
    
    params = {'name': 'NEWOPERATOR'}
    config = {'db_user_id': 'ytsapras', \
                'db_pswd': 'xxxx'
                }
    response = api_tools.submit_operator_record(config,params)
    
if __name__ == '__main__':
    test_api_operator_record()
