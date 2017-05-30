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

################################################################################
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
    
    message = talk_to_db(params,end_point,\
                            config['db_user_id'],config['db_pswd'],
                            testing=True)

def submit_data_file_record(config,params,testing=False):
    """Function to submit a record of a new observation to the database 
    using the API record_obs_request endpoint
    Required parameters:
        config    dict    script configuration parameters
        params    dict    observation request parameters, including
                    event_name  str   Name of the event
                    datafile    str   Path to the data
                    tel         str   Name of the telescope
                    filt        str   Name of the filter used
                    last_mag    float Last measured magnitude
                    last_upd    datetime Last updated time stamp
                    last_obs    datetime of last observation
                    baseline    float Event's baseline magnitude
                    g           float ARTEMiS' fitted blend parameter
                    ndata       int   Number of datapoints
    """
    
    end_point = 'record_data_file'
    
    message = talk_to_db(params,end_point,\
                            config['db_user_id'],config['db_pswd'],
                            testing=testing)
    return message
    
################################################################################
def submit_operator_record(config,params):
    """Function to submit a record of a new operator to the database 
    using the API record_operator endpoint
    Required parameters:
        config    dict    script configuration parameters
        params    dict    operator parameters, including
                    name       str
    """
    
    end_point = 'add_operator'
    
    response = talk_to_db(params,end_point,\
                            config['db_user_id'],config['db_pswd'],
                            testing=True)

################################################################################
def submit_telescope_record(config,params):
    """Function to submit a record of a new telescope to the database 
    using the API record_operator endpoint
    Required parameters:
        config    dict    script configuration parameters
        params    dict    telescope parameters, including
                    operator str
                    telescope_name str
                    aperture float
                    latitude float
                    longitude float
                    altitude float
                    site str
    """
    
    end_point = 'add_telescope'
    
    response = talk_to_db(params,end_point,\
                            config['db_user_id'],config['db_pswd'],
                            testing=True)

################################################################################
def talk_to_db(data,end_point,user_id,pswd,testing=False,verbose=False):
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
        verbose    boolean            Switch for additional debugging output
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
    
    if verbose==True:
        print 'End point URL:',url
    
    
    client = requests.session()
    response = client.get(login_url)
    if verbose == True:
        print 'Started session with response: ',response.text
    
    auth_details = {'username': user_id, 'password': pswd}
    headers = { 'Referer': url, 'X-CSRFToken': client.cookies['csrftoken'],}
    
    response = client.post(login_url, headers=headers, data=auth_details)
    if verbose==True:
        print response.text
        print 'Completed login'
    
    response = client.get(url)
    headers = { 'Referer': url, 'X-CSRFToken': client.cookies['csrftoken'],}
    response = client.post(url, headers=headers, data=data)
    if verbose==True:
        print response.text
        print 'Completed successfully'
    
    message = 'OK'
    for line in response.text.split('\n'):
        if 'DBREPLY' in line:
            message = line.lstrip().replace('<h5>','').replace('</h5>','')
            message = message.replace('DBREPLY: ','')
    
    return message
