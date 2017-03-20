# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 10:06:31 2017

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
import update_db_2

def test_add_request():
    """Test the submission of new observation requests to the database"""
    
    field_name = 'TEST'
    t_sample = 60.0
    exptime = 300.0
    n_exp = 1
    ts_submit = timezone.now()
    ts_expire = ts_submit + timedelta(hours=24)
    pfrm = False
    onem = True
    twom = False
    request_type = 'L'
    f = 'gp'
    i = 'fl16'
    group_id = 'TEST1'
    track_id = '0000012345'
    request_id = '000000123456'
    status = update_db_2.add_request(field_name, t_sample, exptime, n_exp=n_exp, \
                timestamp=ts_submit,time_expire=ts_expire, pfrm_on = pfrm,\
                onem_on=onem, twom_on=twom, request_type=request_type, \
                which_filter=f,which_inst=i, grp_id=group_id, \
                track_id=track_id, req_id=request_id)
    assert status == True
        