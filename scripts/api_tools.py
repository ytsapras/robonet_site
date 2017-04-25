# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 13:47:12 2017

@author: rstreet
"""

import httplib
import urllib
import json
import requests
from os import path

def submit_obs_request_record(config,params):
    """Function to submit a record of a new observation to the database 
    using the API record_obs_request endpoint
    Required parameters:
        config    dict    script configuration parameters
        params    dict    observation request parameters, including
                    field       str
                    t_sample    float
                    exptime     int
                    timestamp   string
                    time_expire string
    """
    
    end_point = 'record_obs_request'
    
    response = talk_to_db(params,end_point,\
                            config['db_user_id'],config['db_pswd'],
                            testing=True)

def talk_to_db(data,end_point,user_id,pswd,testing=False):
    """Method to communicate with various APIs of the ROME/REA database. 
    Required arguments are:
        data       dict     parameters of the submission
        end_point  string   URL suffix of the form to submit to
        user_id    string   User ID login for database
        pswd       string   User password login for database
    
    E.g. if submitting to URL:
        http://robonet.lco.global/db/record_obs_request/
    end_point = 'record_obs_request
    
    Optional arguments:
        testing    boolean            Switch to localhost URL for testing
                                        Def=False for operations
    """
    if testing == True:
        host_url = 'http://127.0.0.1:8000/db'
        login_url = 'http://127.0.0.1:8000/db/login/'
    else:
        host_url = 'http://robonet.lco.global/db'
        login_url = 'http://robonet.lco.global/db/login/'
        
    url = path.join(host_url,end_point)
    if url[-1:] != '/':
        url = url + '/'
    print 'End point URL:',url
    
    
    client = requests.session()
    response = client.get(login_url)
    print 'Started session with response: ',response.text
    
    auth_details = {'username': user_id, 'password': pswd, 'csrfmiddlewaretoken': client.cookies['csrftoken']}
    headers = { 'Referer': url, 'X-CSRFToken': client.cookies['csrftoken'],}
    
    response = client.post(login_url, headers=headers, data=auth_details)
    print response.text
    print 'Completed submission'
    