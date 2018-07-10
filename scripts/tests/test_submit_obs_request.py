# -*- coding: utf-8 -*-
"""
Created on Sat Jul  7 16:39:01 2018

@author: rstreet
"""

from os import path, getcwd
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'..'))
import submit_obs_request
import observation_classes

def test_build_obs():
    """Function to test the build_obs_request function of submit_obs_request"""
    
    test_obs = observation_classes.ObsRequest()
    
    obs_file = path.join(getcwd(),'../../data/example_obs_file.txt')
    
    obs = submit_obs_request.build_obs_request(obs_config, obs_file)
        
    assert type(obs) == type(test_obs)
    
    keys = [ 'name', 'group_id', 'ra', 'dec', 'site', 'observatory', 'tel', 
             'instrument', 'instrument_class', 'filters', 'group_type', 
             'exposure_times', 'exposure_counts', 'cadence', 'jitter', 
             'priority', 'ts_submit', 'ts_expire', 'airmass_limit', 
             'moon_sep_min', 'user_id', 'token', 'proposal_id' ]
    
    for key in keys:
        
        assert getattr(obs,key) != None
    
    assert type(obs.filters) == type([])
    assert type(obs.exposure_times) == type([])
    assert type(obs.exposure_counts) == type([])
    


if __name__ == '__main__':
    
    test_build_obs()
    