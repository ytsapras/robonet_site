# -*- coding: utf-8 -*-
"""
Created on Sat Apr  1 11:13:44 2017

@author: rstreet
"""

from os import getcwd, path, remove, environ
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'..'))
import observation_classes, log_utilities
import socket

def test_obs_build():
    
    config = get_test_config()
    log = log_utilities.start_day_log( config, 'test_obs' )
    
    obs = get_test_obs_request()
    log.info(obs.summary())
    
    ur = obs.build_cadence_request( log=log, debug=True )
    status = obs.submit_request( ur, config, log=log )
    
    log_utilities.end_day_log( log )

def get_test_config():
    
    host_name = socket.gethostname()
    if 'rachel' in host_name:
        logdir = '/Users/rstreet/ROMEREA/Logs/2017'
    else:
        logdir = '/var/www/robonetsite/logs/2017'
    
    config = {'log_root_name': 'test_obs',
              'log_directory': logdir,
              'token': '94294335fe4d91ef714bd89a051139b22ab15ed8',
              'simulate': 'False'
              }
    return config
        
def get_test_obs_request():
    
    obs = observation_classes.ObsRequest()
    obs.name = 'ROME-FIELD-01'
    obs.ra = '17:51:20.6149'
    obs.dec = '-30:03:38.9442'
    obs.site = 'lsc'
    obs.observatory= 'doma'
    obs.tel = '1m0'
    obs.instrument = 'fl15'
    obs.instrument_class = '1M0-SCICAM-SINISTRO'
    obs.set_aperture_class()
    obs.filters = [ 'SDSS-g', 'SDSS-r', 'SDSS-i' ]
    obs.exposure_times = [ 300.0, 300.0, 300.0 ]
    obs.exposure_counts = [ 1, 1, 1 ]
    obs.cadence = 4.0
    obs.jitter = 1.0
    obs.priority = 1.0
    obs.ttl = 7.0
    obs.user_id = 'foo@lco.global'
    obs.pswd = 'bar'
    obs.proposal_id = 'wibble'
    obs.focus_offset = [ 0.0, 0.0, 0.0 ]
    obs.request_type = 'L'
    obs.req_origin = 'obscontrol'
    obs.get_group_id()
    
    return obs


if __name__ == '__main__':
    test_obs_build()