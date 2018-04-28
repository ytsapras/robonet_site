# -*- coding: utf-8 -*-
"""
Created on Tue Apr 24 12:46:36 2018

@author: rstreet
"""

from os import getcwd, path
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'../..'))
systempath.append(path.join(cwd,'..'))
import api_tools
from datetime import datetime, timedelta

def test_get_obs_list():
    """Function to test the retrieval of observation sets from the DB
    that match specific parameter sets given."""
    
    tstart = datetime.utcnow() - timedelta(days=4.0)
    tend = datetime.utcnow()
    
    params = {'timestamp': tstart.strftime("%Y-%m-%dT%H:%M:%S"),
              'time_expire': tend.strftime("%Y-%m-%dT%H:%M:%S"),
              'request_status': 'AC'}
              
    config = {}
    config['db_user_id'] = raw_input('Please enter DB user ID: ')
    config['db_pswd'] = raw_input('Please enter DB password: ')
    config['testing'] = 'False'
    
    obs_list = api_tools.get_obs_list(config,params)

    assert type(obs_list) == type([])
    for line in obs_list:
        assert type(line) == type({})

if __name__ == '__main__':
    
    test_get_obs_list()
    