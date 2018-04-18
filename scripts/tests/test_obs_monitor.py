# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 15:39:33 2018

@author: rstreet
"""

import os
import sys
cwd = os.getcwd()
sys.path.append(os.path.join(cwd,'..'))
from local_conf import get_conf
robonet_site = get_conf('robonet_site')
sys.path.append(robonet_site)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'robonet_site.settings')
from django.core import management
from django.conf import settings
from django.utils import timezone
from django import setup
from datetime import datetime, timedelta
setup()

import obs_monitor
import pytz

def test_get_obs_request_status():
    """Function to test the return of active observations between a given date 
    range, with the current status of those requests"""
    
    start_date = datetime.now() - timedelta(seconds=2.0*24.0*60.0*60.0)
    start_date = start_date.replace(tzinfo=pytz.UTC)
    end_date = datetime.now() + timedelta(seconds=2.0*24.0*60.0*60.0)
    end_date = end_date.replace(tzinfo=pytz.UTC)
    
    obs_monitor.get_obs_request_status(start_date,end_date)
    

if __name__ == '__main__':
    
    test_get_obs_request_status()
    