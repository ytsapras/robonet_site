# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 14:03:37 2017

@author: rstreet
"""

from os import getcwd, path, remove, environ
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'../..'))
systempath.append(path.join(cwd,'..'))
from local_conf import get_conf
robonet_site = get_conf('robonet_site')
systempath.append(robonet_site)
environ.setdefault('DJANGO_SETTINGS_MODULE', 'robonet_site.settings')
from django.core import management
from django.conf import settings
from django.utils import timezone
from django import setup
setup()
from events.models import Field
from datetime import datetime, timedelta
import pytz
import api_tools

def test_api_obs_record():
    """Function to test the recording of a new observation 
    request (submitted to the LCO network) by submitting it to the ROME/REA
    database via API. """
    
    params = {'field': '1',\
              't_sample': 333.3,\
              'exptime': 999,\
              'timestamp': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),\
              'time_expire': (datetime.utcnow() + timedelta(days=1.0)).strftime("%Y-%m-%dT%H:%M:%S")
            }
    config = {}
    config['db_user_id'] = raw_input('Please enter DB user ID: ')
    config['db_pswd'] = raw_input('Please enter DB password: ')
    response = api_tools.submit_obs_request_record(config,params)

def test_api_sub_obs_record():
    """Function to test the API to add a new SubObsRequest record to the DB"""
    
    window_start = datetime.strptime('2018-04-20T15:30:00',"%Y-%m-%dT%H:%M:%S")
    window_start = window_start.replace(tzinfo=pytz.UTC)
    window_end = datetime.strptime('2018-04-20T16:00:00',"%Y-%m-%dT%H:%M:%S")
    window_end = window_end.replace(tzinfo=pytz.UTC)
    time_executed = datetime.strptime('2018-04-20T15:45:00',"%Y-%m-%dT%H:%M:%S")
    time_executed = time_executed.replace(tzinfo=pytz.UTC)
    
    params = {'sr_id': '1477711',
              'grp_id': 'ROME20180412T16.93534273',
              'track_id': '624354',
              'window_start': window_start.strftime("%Y-%m-%dT%H:%M:%S"),
              'window_end': window_end.strftime("%Y-%m-%dT%H:%M:%S"),
              'status': 'PENDING'}

    config = {}
    config['db_token'] = raw_input('Please give DB token: ')

    response = api_tools.submit_sub_obs_request_record(config,params,testing=True,
                                                       verbose=False)
        
    assert 'Subrequest successfully added to database' in response
    
    params = {'sr_id': '1477711',
              'grp_id': 'ROME20180412T16.93534273',
              'track_id': '624354',
              'window_start': window_start.strftime("%Y-%m-%dT%H:%M:%S"),
              'window_end': window_end.strftime("%Y-%m-%dT%H:%M:%S"),
              'status': 'PENDING',
              'time_executed': time_executed.strftime("%Y-%m-%dT%H:%M:%S")}

    response = api_tools.submit_sub_obs_request_record(config,params,testing=True,
                                                       verbose=False)
        
    assert 'Subrequest updated' in response
   
    
if __name__ == '__main__':
    
    #test_api_obs_record()
    test_api_sub_obs_record()
    