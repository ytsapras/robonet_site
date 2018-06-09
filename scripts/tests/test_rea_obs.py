# -*- coding: utf-8 -*-
"""
Created on Sun Apr  2 10:28:53 2017

@author: rstreet
"""
from os import getcwd, path, remove, environ
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'..'))
from local_conf import get_conf
robonet_site = get_conf('robonet_site')
systempath.append(robonet_site)
environ.setdefault('DJANGO_SETTINGS_MODULE', 'robonet_site.settings')
from django.core import management
from django.conf import settings
from django.utils import timezone
from django import setup
from datetime import datetime, timedelta
setup()
from events.models import Event, SingleModel
import rea_obs
import log_utilities
import observation_classes

class TestField():
    """Class describing a field object used for code testing only"""
    
    def __init__(self,**kwargs):
        self.name = kwargs['name']
        self.field = kwargs['field']
        self.ra = kwargs['ra']
        self.dec = kwargs['dec']
        self.priority = kwargs['priority']
        self.passband = kwargs['passband']
        self.texp = kwargs['texp']
        self.nexp = kwargs['nexp']
        self.tsamp = kwargs['tsamp']
        self.ipp = kwargs['ipp']

class TestDBField():
    """Class describing a field object as produced by the DB Field table"""
    
    def __init__(self,**kwargs):
        self.name = kwargs['name']
        self.field_ra = kwargs['field_ra']
        self.field_dec = kwargs['field_dec']
        
def test_build_rea_obs():
    
    config = {'user_id': 'tester@lco.global',
              'token': 'XXXX', 
              'proposal_id': 'TEST',
              'log_directory': '.',
              'log_root_name': 'test_rea_obs'}

    test_target = { 'name':'OGLE-2018-BLG-XXXX', 
                    'field':'ROME-FIELD-01', 
                    'ra':267.835895375 , 'dec':-30.0608178195,
                    'priority':'N', 'passband':'SDSS-i',
                    'texp':30.0, 'nexp':1,
                    'tsamp': 30.0, 'ipp': 1.05
                  }
                           
    tap_list = [ TestField(**test_target) ]
    
    log = log_utilities.start_day_log( config, 'test_rea_obs' )
    
    obs_requests = rea_obs.build_rea_obs(config,log=log,tap_list=tap_list)

    assert len(obs_requests) > 0
    
    log_utilities.end_day_log(log)

def test_build_rea_hi_request():
    """Function to test the construction of REA-HI mode observation
    requests triggered from the online interface"""
    
    exptime = 30.0
    tsample = 0.25

    config = {'user_id': 'tester@lco.global',
              'token': 'XXXX', 
              'proposal_id': 'TEST',
              'log_directory': '.',
              'log_root_name': 'test_rea_obs'}
              
    test_target = { 'name':'ROME-FIELD-01', 
                    'field_ra':267.835895375 , 'field_dec':-30.0608178195}

    field = TestDBField(**test_target)
    
    obs_requests = rea_obs.build_rea_hi_request(config, field, exptime, tsample)
    
    for obs in obs_requests:
        print obs.summary()
    
    assert type(obs_requests) == type([])
    assert len(obs_requests) == 3
    for obs in obs_requests:
        assert type(obs) == type(observation_classes.ObsRequest())
        assert obs.exposure_times[0] == exptime
        assert obs.name == test_target['name']
        assert obs.cadence == tsample

if __name__ == '__main__':
    
    test_build_rea_obs()
    test_build_rea_hi_request()