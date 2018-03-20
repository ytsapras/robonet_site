# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 11:45:15 2018

@author: rstreet
"""

import sys
import os
import urllib
import requests
import json

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
    
    if 'requests' in api_response.keys():
        for subrequest in api_response['requests']:
            
            states.append(subrequest['state'])
            completed_ts.append(subrequest['completed'])
    
    return states, completed_ts
        
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
    