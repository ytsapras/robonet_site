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
import update_db_2, query_db
from events.models import Field
import api_tools
import pytz

def test_add_request():
    """Test the submission of new observation requests to the database"""
    
    field = Field(name='ROME-FIELD-01')
    t_sample = 60.0
    exptime = 300
    n_exp = 1
    ts_submit = timezone.now()
    ts_expire = ts_submit + timedelta(hours=24)
    pfrm = False
    onem = True
    twom = False
    request_type = 'L'
    f = 'SDSS-g'
    i = 'fl16'
    group_id = 'TEST1'
    track_id = '0000012345'
    request_id = '000000123456'
    status = update_db_2.add_request(field.name, t_sample, \
                exptime, timestamp=timezone.now(), time_expire=ts_expire, \
                pfrm_on = pfrm, onem_on=onem, twom_on=twom, request_type=request_type, \
                which_filter=f,which_inst=i, grp_id=group_id, \
                track_id=track_id, req_id=request_id,n_exp=n_exp)
    assert status == True

def test_coords_exist():
    """Function to verify that the function coords_exist correctly 
    finds an object in the DB by its coordinates"""
    
    name = 'OGLE-2012-BLG-0970'
    ra = '17:54:51.78'
    dec = '-28:18:40.10'
    
    event = query_db.get_event_by_position(ra,dec)
    assert event != None
    
    coordinates_known = update_db_2.coords_exist(ra, dec)
    assert coordinates_known[0] == True
    assert coordinates_known[1] == ra
    assert coordinates_known[2] == dec

def test_add_datafile_via_api():
    """Function to check that the function to add a data file to the DB
    correctly parses the parameters given."""
    
    last_obs = datetime.utcnow()
    last_obs = last_obs.replace(tzinfo=pytz.UTC)
    last_obs = last_obs.strftime("%Y-%m-%dT%H:%M:%S")
    
    last_upd = datetime.utcnow()
    last_upd = last_upd.replace(tzinfo=pytz.UTC)
    last_upd = last_upd.strftime("%Y-%m-%dT%H:%M:%S")
    
    params = {'event_name': 'OGLE-2017-BLG-0620',
              'datafile': '/data/romerea/data/artemis/data/OOB170620I.dat',
              'last_mag': 17.2,
              'tel': 'OGLE 1.3m',
              'filt': 'I',
              'baseline': 22.5,
              'g': 18.45,
              'ndata': 2234,
              'last_obs': last_obs,
              'last_upd': last_upd,
            }
            
    (status,message) = update_db_2.add_datafile_via_api(params)
    print status, message

if __name__ == '__main__':
    test_add_datafile_via_api()