# -*- coding: utf-8 -*-
"""
Created on Tue Apr 24 12:46:36 2018

@author: rstreet
"""

from os import getcwd, path
from sys import path as systempath
from sys import argv
cwd = getcwd()
systempath.append(path.join(cwd,'../..'))
systempath.append(path.join(cwd,'..'))
import api_tools
from datetime import datetime, timedelta

def test_get_obs_list():
    """Function to test the retrieval of observation sets from the DB
    that match specific parameter sets given."""
    
    tstart = datetime.utcnow() - timedelta(days=10.0)
    tend = datetime.utcnow() + timedelta(days=10.0)
    
    params = {'timestamp': tstart.strftime("%Y-%m-%dT%H:%M:%S"),
              'time_expire': tend.strftime("%Y-%m-%dT%H:%M:%S"),
              'request_status': 'AC'}
              
    config = {}
    
    if len(argv) == 1:
        config['db_token'] = raw_input('Please enter DB token: ')
    else:
        config['db_token'] = argv[1]
        
    config['testing'] = True
    
    (message, obs_list) = api_tools.get_obs_list(config,params,
                                      testing=config['testing'],
                                        verbose=True)
        
    assert type(obs_list) == type([])
    for line in obs_list:
        assert type(line) == type({})

    params = {'timestamp': tstart.strftime("%Y-%m-%dT%H:%M:%S"),
              'time_expire': tend.strftime("%Y-%m-%dT%H:%M:%S"),
              'request_status': 'ALL'}
              
    (message, obs_list) = api_tools.get_obs_list(config,params,
                                      testing=config['testing'],
                                        verbose=True)
        
    assert type(obs_list) == type([])
    for line in obs_list:
        assert type(line) == type({})
    
if __name__ == '__main__':
    
    test_get_obs_list()
    