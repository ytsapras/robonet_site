# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 15:21:11 2017

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
import obs_control
from events.models import ObsRequest, Field
import observation_classes

def test_rm_duplicate_obs():
    
    ts_submit = timezone.now()
    ts_expire = ts_submit + timedelta(hours=24.0)
    field = Field(name='test_field')
    aobs = ObsRequest(field=field, t_sample=60.0, exptime=60.0, \
                               timestamp=ts_submit, time_expire=ts_expire, \
                               pfrm_on=False, onem_on=True, twom_on=False, \
		               request_type='L', which_filter='SDSS-i', \
			       which_inst='fl16', grp_id='ROME_test', \
                          track_id='0000012345',req_id='00012345', n_exp=1)
    active_obs = [ aobs ]
    
    robs = observation_classes.ObsRequest()
    robs.name = 'test_field'
    robs.filters = [ 'SDSS-g', 'SDSS-r', 'SDSS-i' ]
    robs.request_type = 'L'
    obs_requests = [ robs ]
    
    obs_requests = obs_control.rm_duplicate_obs(obs_requests, active_obs)
    
    assert len(obs_requests) == 0

    