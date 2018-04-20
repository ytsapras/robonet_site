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
   
    test_get_fields_list()
     
    test_plot_req_vs_obs()

def generate_camera_data(camera,grp_id,field,date):
    
    obs = observation_classes.ObsRequest()
    obs.grp_id = grp_id
    obs.which_inst = camera
    obs.field = field

    req_duration_secs = 0.5 * 60.0 * 60.0
    cadence_secs = 1.0 * 60.0 * 60.0
    
    if camera == 'fl12':
        start_date = date
    elif camera == 'fl06':
        start_date = date + timedelta(hours=8.0)
    elif camera == 'fl03':
        start_date = date + timedelta(hours=14.0)
    start_date = start_date.replace(tzinfo=pytz.UTC)

    end_date = start_date + timedelta(seconds=req_duration_secs)
    end_date = end_date.replace(tzinfo=pytz.UTC)
   
    states = []
    completed_times = []
    windows = []
    for i in range(0,6,1):
    
        if i <= 3:
            states.append('COMPLETED')
            ts = datetime.now()
            ts.replace(tzinfo=pytz.UTC)
            completed_times.append(ts.strftime("%Y-%m-%dT%H:%M:%S"))
        else:
            states.append('PENDING')
            completed_times.append('None')
            
        windows.append( (start_date, end_date) )
            
        start_date = end_date + timedelta(seconds=cadence_secs)
        end_date = start_date + timedelta(seconds=req_duration_secs)
        
    return obs, states, completed_times, windows

def get_field_names():
    """Function to generate the list of ROME field IDs"""

    field_list = []
    for i in range(0,21,1):
        if i < 10:
            field_list.append('ROME-FIELD-0'+str(i))
        else:
            field_list.append('ROME-FIELD-'+str(i))
    
    return field_list
    
def generate_test_dataset():
    """Function to generate a realistic dataset for testing purposes"""
    
    active_obs = {}
    
    field_list = get_field_names()
    
    window_start = datetime.strptime('2018-04-20T00:00:00', "%Y-%m-%dT%H:%M:%S")
    window_start = window_start.replace(tzinfo=pytz.UTC)
    
    n_days= 5
    
    for day in range(0,n_days,1):
        
        date = window_start + timedelta(days=day)
        
        for field in field_list:
            
            for camera in ['fl12', 'fl06', 'fl03']:
                
                
                (obs, states, completed_times, windows) = generate_camera_data(camera,
                                                            'test_'+camera+'_'+field+'_'+str(day), 
                                                            field,date)
                
                active_obs[obs.grp_id]  = {'obsrequest': obs, 
                                         'sr_states': states,
                                         'sr_completed_ts': completed_times,
                                         'sr_windows': windows}
        
    return active_obs
    
def test_get_fields_list():
    """Function to test the function which extracts a list of the fields
    being observed"""
    
    field_list = get_field_names()

    active_obs = generate_test_dataset()
    
    fields = obs_monitor.get_fields_list(active_obs)
        
    fields_returned = fields.keys()
    fields_returned.sort()
    
    assert field_list == fields_returned

def test_plot_req_vs_obs():
    """Function to test the generated plot for requested vs observed"""
    
    active_obs = generate_test_dataset()
    
    (script, div) = obs_monitor.plot_req_vs_obs(active_obs,dbg=False)
    
    print script
    
if __name__ == '__main__':
    
    run_tests()
    