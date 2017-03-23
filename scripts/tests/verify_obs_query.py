# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 22:57:31 2017

@author: rstreet
"""

from os import getcwd, path
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'..'))
import observation_classes
import obs_control
from sys import argv

def test_get_request_numbers(trackid):
    
    config = obs_control.read_config()
    config = obs_control.parse_args(config)
    
    obs = observation_classes.ObsRequest()
    obs.track_id = trackid
    obs.get_request_numbers(config,log=None)
    if len(obs.req_id) > 0:
        print('Observation request with tracking ID '+str(trackid)+' has associated request IDs:')
        print obs.req_id
        
    else:
        print('No request IDs returned for observation tracking number '+str(trackid))
        
if __name__ == '__main__':
    if len(argv) == 1:    
        trackid = raw_input('Please enter the tracking ID of a submitted observation request:')
    else:
        trackid = argv[1]
    test_get_request_numbers(trackid)