# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 11:45:15 2018

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

from events.models import ObsRequest

import urllib
import requests
import json
from datetime import datetime
import pytz

def lco_userrequest_query(token,track_id):
    """Method to query for the status of a specific observation request 
    via its tracking ID number.   
    """

    headers = {'Authorization': 'Token ' + token}
    
    url = os.path.join('https://observe.lco.global/api/userrequests/',str(track_id))
    
    response = requests.post(url, headers=headers, timeout=20).json()
        
    return response

def get_subrequests_status(token,track_id):
    """Function to query the LCO API for the status of a specific request"""
    
    api_response = lco_userrequest_query(token,track_id)
    
    states = []
    completed_ts = []
    windows = []
    
    if 'requests' in api_response.keys():
        for subrequest in api_response['requests']:
                        
            states.append(subrequest['state'])
            completed_ts.append(subrequest['completed'])
            tstart = datetime.strptime(subrequest['windows'][0]['start'],"%Y-%m-%dT%H:%M:%SZ")
            tstart = tstart.replace(tzinfo=pytz.UTC)
            tend = datetime.strptime(subrequest['windows'][0]['end'],"%Y-%m-%dT%H:%M:%SZ")
            tend = tend.replace(tzinfo=pytz.UTC)
            windows.append( (tstart, tend) )
            
    return states, completed_ts, windows

def get_status_active_obs_subrequests(token,start_date,end_date,dbg=False):
    """Function to determine the status of all observation requests within
    a specified time period. 
    
    Inputs:
        :param datetime start_date: Start of observing period
        :param datetime end_date: End of observing period
    Outputs:
        :param dict active_obs: Dictionary of matching observations of format:
            { obs.grp_id : {'obsrequest': ObsRequest object, 
                            'sr_states': states of ObsRequest cadence subrequests,
                            'sr_completed_ts': timestamps of subrequest completion, or None,
                            'sr_windows': (start, end) subrequest datetimes}
    """
     
    qs = ObsRequest.objects.all().exclude(request_status = 'CN').\
            filter(timestamp__lte=end_date).filter(time_expire__gt=start_date)
    
    active_obs = {}
    
    for obs in qs:
        
        if dbg:
            print(obs.grp_id+' '+obs.track_id+' '+\
                obs.timestamp.strftime("%Y-%m-%dT%H:%M:%S")+' - '+\
                obs.time_expire.strftime("%Y-%m-%dT%H:%M:%S"))
                
        (states, completed_ts, windows) = get_subrequests_status(token,obs.track_id)
        
        if dbg:
            for i in range(0,len(states),1):
                try:
                    print '-> '+states[i], completed_ts[i].strftime("%Y-%m-%dT%H:%M:%S")
                except AttributeError:
                    print '-> '+states[i], repr(completed_ts[i])
        
        active_obs[str(obs.grp_id)] = {'obsrequest': obs,
                                  'sr_states': states,
                                  'sr_completed_ts': completed_ts,
                                  'sr_windows': windows}
    return active_obs
    


if __name__ == '__main__':
    
    if len(sys.argv) > 1:
        
        track_id = sys.argv[1]
        token = sys.argv[2]
        
    else:
        
        track_id = raw_input('Please enter the tracking ID of the request: ')
        token = raw_input('Please enter your LCO token: ')
    
    response = lco_userrequest_query(token,track_id)
    
    for subrequest in response['requests']:
    
        print subrequest['state'], subrequest['completed']
    