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

def run_tests():
    """Function to run the suite of tests.  Since access to LCO's API 
    requires a user token, these tests require this token as input and so
    don't conform to the usual pytest format.
    """
    
    if len(sys.argv) > 1:
        
        token = sys.argv[1]
        
    else:
        
        token = raw_input('Please enter your LCO API token: ')
   
    
    test_get_status_active_obs_subrequests(token)
 

def test_get_status_active_obs_subrequests(token):
    """Function to test the return of active observations between a given date 
    range, with the current status of those requests"""
    
    start_date = datetime.now() - timedelta(seconds=2.0*24.0*60.0*60.0)
    start_date = start_date.replace(tzinfo=pytz.UTC)
    end_date = datetime.now() + timedelta(seconds=2.0*24.0*60.0*60.0)
    end_date = end_date.replace(tzinfo=pytz.UTC)
    
    active_obs = obs_monitor.get_status_active_obs_subrequests(token,start_date,end_date)
    
    assert type(active_obs) == type({})
    assert type(active_obs[active_obs.keys()[0]]) == type({})
    for key in ['obsrequest','sr_states','sr_completed_ts','sr_windows']:
        assert key in active_obs[active_obs.keys()[0]].keys()

if __name__ == '__main__':
    
    run_tests()
    