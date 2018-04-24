# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 11:45:15 2018

@author: rstreet
"""
import os
import sys
cwd = os.getcwd()
sys.path.append(os.path.join(cwd,'..'))
import urllib
import requests
import json
from datetime import datetime, timedelta
import pytz
import observation_classes

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
    
    subrequests = []
    
    if 'requests' in api_response.keys():
        
        for subrequest in api_response['requests']:
            
            sr = observation_classes.SubObsRequest()
            
            sr.sr_id = subrequest['id']
            sr.request_grp_id = api_response['group_id']
            sr.request_track_id = api_response['id']
            sr.state = subrequest['state']
                        
            if 'None' in str(subrequest['completed']):
                sr.time_executed = None
            else:
                sr.time_executed = datetime.strptime(subrequest['completed'],"%Y-%m-%dT%H:%M:%S.%fZ")

            tstart = datetime.strptime(subrequest['windows'][0]['start'],"%Y-%m-%dT%H:%M:%SZ")
            tstart = tstart.replace(tzinfo=pytz.UTC)
            sr.window_start = tstart            

            tend = datetime.strptime(subrequest['windows'][0]['end'],"%Y-%m-%dT%H:%M:%SZ")
            tend = tend.replace(tzinfo=pytz.UTC)
            sr.window_end = tend
            
            subrequests.append(sr)
            
    return subrequests

def get_status_active_obs_subrequests(obs_list,token,
                                      start_date,end_date,dbg=False,log=None):
    """Function to determine the status of all observation requests within
    a specified time period. 
    
    Inputs:
        :param list obs_list: List of observations to be queried, each entry is a
                dictionary with the keys:
                {obs_pk, obs_grp_id, obs_track_id, timestamp, time_expire, status}
        :param str token: LCO API token
        :param datetime start_date: Start of observing period
        :param datetime end_date: End of observing period
    Outputs:
        :param dict active_obs: Dictionary of matching observations of format:
            { obs.grp_id : {'obsrequest': ObsRequest object, 
                            'sr_states': states of ObsRequest cadence subrequests,
                            'sr_completed_ts': timestamps of subrequest completion, or None,
                            'sr_windows': (start, end) subrequest datetimes}
    """
     
    if log!=None:
        
        log.info('Identified '+str(len(obs_list))+\
        ' database entries, including duplicates for multi-filter observations, within date range '+\
        start_date.strftime("%Y-%m-%dT%H:%M:%S")+' to '+end_date.strftime("%Y-%m-%dT%H:%M:%S"))
        
    active_obs = {}
    
    for obs in obs_list:
        
        if obs['grp_id'] not in active_obs.keys():
            
            if dbg:
                print(obs['grp_id']+' '+obs['track_id']+' '+\
                    obs['timestamp'].strftime("%Y-%m-%dT%H:%M:%S")+' - '+\
                    obs['time_expire'].strftime("%Y-%m-%dT%H:%M:%S")+' '+\
                    obs['status'])
            
            if log!=None:
                
                log.info('-> '+obs['grp_id']+' '+obs['track_id']+' '+\
                    obs['timestamp'].strftime("%Y-%m-%dT%H:%M:%S")+' - '+\
                    obs['time_expire'].strftime("%Y-%m-%dT%H:%M:%S")+' '+\
                    obs['status'])
                    
            subrequests = get_subrequests_status(token,obs['track_id'])
            
            if dbg:
                
                for sr in subrequests:
                    
                    print sr.summary()
            
            if log!=None:
                
                for sr in subrequests:
                    
                    log.info('-> '+sr.summary())
            
                
            active_obs[str(obs['grp_id'])] = {'obsrequest': obs,
                                           'subrequests': subrequests}
    
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
    