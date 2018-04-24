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
import observation_classes

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

    test_sr = observation_classes.SubObsRequest()
    
    subrequests = lco_api_tools.get_subrequests_status(token,track_id)

    assert type(subrequests) == type([])
    for item in subrequests:
        assert type(item) == type(test_sr)

def test_get_status_active_obs_subrequests(token):
    """Function to test the return of active observations between a given date 
    range, with the current status of those requests"""
    
    test_sr = observation_classes.SubObsRequest()
    
    start_date = datetime.now() - timedelta(seconds=2.0*24.0*60.0*60.0)
    start_date = start_date.replace(tzinfo=pytz.UTC)
    end_date = datetime.now() + timedelta(seconds=2.0*24.0*60.0*60.0)
    end_date = end_date.replace(tzinfo=pytz.UTC)
    
    obs_list = [
                {'pk':16880, 'grp_id': 'REALO20180422T20.59162096', 'track_id': '633617', 
                 'timestamp': datetime(2018, 4, 22, 20, 45, 29), 
                 'time_expire': datetime(2018, 4, 23, 20, 45, 29), 
                 'status': 'AC'}, 
                 {'pk': 16881, 'grp_id': 'REALO20180422T20.59207874', 'track_id': '633618', 
                  'timestamp': datetime(2018, 4, 22, 20, 45, 31), 
                  'time_expire': datetime(2018, 4, 23, 20, 45, 31), 
                  'status': 'AC'}             
                ]
                
    active_obs = lco_api_tools.get_status_active_obs_subrequests(obs_list,token,start_date,end_date)
        
    assert type(active_obs) == type({})
    for grp_id, item in active_obs.items():
        assert type(grp_id) == type('foo')
        assert type(item) == type({})
        assert 'obsrequest' in item.keys()
        assert 'subrequests' in item.keys()
        
        for sr in item['subrequests']:
            assert type(sr) == type(test_sr)


if __name__ == '__main__':
    
    run_tests()
    