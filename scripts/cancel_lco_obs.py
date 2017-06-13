# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 14:48:11 2017

@author: rstreet
"""


from sys import exit, argv
from os import path
import observation_classes

def cancel_obs_in_network_scheduler():
    """Function to cancel a list of observation requests within the LCO network
    scheduler, through the Valhalla portal"""
    
    (obs_list,token) = get_obs_list()
    
    for trackid in obs_list:
        obs = observation_classes.ObsRequest()
        obs.track_id = trackid
        obs.token = token
        status = obs.cancel_request()
        print obs.track_id, status
        
def get_obs_list():
    """Function to read in a list of observation request IDs"""
    
    obs_list = []
    if len(argv) > 1:
        filename = argv[1]
        token = argv[2]
    else:
        filename = raw_input('Please enter the path to a list of observations to be cancelled: ')
        token = raw_input('Please enter LCO token: ')
    
    if path.isfile(filename) == True:
        file_lines = open(filename, 'r').readlines()
        for line in file_lines:
            trackid = line.replace('\n','').split()[1]
            obs_list.append(trackid)
    return obs_list, token

if __name__ == '__main__':
    cancel_obs_in_network_scheduler()