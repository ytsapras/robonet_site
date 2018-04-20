# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 16:23:33 2018

@author: rstreet
"""

import sys
import os
cwd = os.getcwd()
sys.path.append(os.path.join(cwd,'..'))
import lco_api_tools
from datetime import datetime, timedelta
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
   
    test_get_subrequests_status(token)
    test_get_status_active_obs_subrequests(token)
 
def test_get_subrequests_status(token):
    
    track_id = 624354
    
    (states, completed_ts, windows) = lco_api_tools.get_subrequests_status(token,track_id)

    for i in range(0,len(states),1):
        print states[i], completed_ts[i], windows[i]

    assert type(states) == type([])
    assert type(completed_ts) == type([])
    assert len(states) > 0

def test_get_status_active_obs_subrequests(token):
    """Function to test the return of active observations between a given date 
    range, with the current status of those requests"""
    
    start_date = datetime.now() - timedelta(seconds=2.0*24.0*60.0*60.0)
    start_date = start_date.replace(tzinfo=pytz.UTC)
    end_date = datetime.now() + timedelta(seconds=2.0*24.0*60.0*60.0)
    end_date = end_date.replace(tzinfo=pytz.UTC)
    
    active_obs = lco_api_tools.get_status_active_obs_subrequests(token,start_date,end_date)
    
    print active_obs
    assert type(active_obs) == type({})
    assert type(active_obs[active_obs.keys()[0]]) == type({})
    for key in ['obsrequest','sr_states','sr_completed_ts','sr_windows']:
        assert key in active_obs[active_obs.keys()[0]].keys()
    for key in active_obs.keys():
        assert type(key) == type('foo')


if __name__ == '__main__':
    
    run_tests()
    