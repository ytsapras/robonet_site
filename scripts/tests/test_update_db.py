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
from events.models import Field, Event, Tap
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
    site = 'cpt'
    status = update_db_2.add_request(field.name, t_sample, \
                exptime, timestamp=timezone.now(), time_expire=ts_expire, \
                pfrm_on = pfrm, onem_on=onem, twom_on=twom, request_type=request_type, \
                which_site=site, which_filter=f,which_inst=i, grp_id=group_id, \
                track_id=track_id, req_id=request_id,n_exp=n_exp)
    assert status == True

def test_coords_exist():
    """Function to verify that the function coords_exist correctly 
    finds an object in the DB by its coordinates"""
    
    name = 'OGLE-2017-BLG-1066'
    ra = '17:45:05.34'
    dec = '-32:52:27.40'
    
    event = query_db.get_event_by_position(ra,dec)
    assert event != None
    
    coordinates_known = update_db_2.coords_exist(ra, dec)
    assert coordinates_known[0] == True
    assert coordinates_known[1] == ra
    assert coordinates_known[2] == dec

def test_add_datafile_via_api():
    """Function to check that the function to add a data file to the DB
    correctly parses the parameters given."""
    
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
              'last_hjd': 2457880.9999,
              'last_upd': last_upd,
            }
            
    (status,message) = update_db_2.add_datafile_via_api(params)
    print status, message

def test_expire_old_obs():
    """Function to test the function that expires observations from the DB
    that have exceeded their expiry date"""
    
    update_db_2.expire_old_obs()
    qs = query_db.get_old_active_obs()
    assert len(qs) == 0

def test_update_image():
    """Function to test the function to update the parameters of an existing 
    image"""
    
    image_name = 'coj1m011-fl12-20170726-0119-e91.fits'
    date_obs = datetime.strptime('2017-07-26T13:44:42',"%Y-%m-%dT%H:%M:%S")
    tel='LCOGT SSO A m'
    inst='fl12'
    filt='SDSS-g'
    grp_id='ROME20170719T22.44993187'
    track_id='0000460168'
    req_id='0001232641'
    quality = 'Bad seeing'
    status = update_db_2.update_image(image_name, date_obs, tel=tel, 
                inst=inst,filt=filt, grp_id=grp_id, track_id=track_id, 
                req_id='', quality=quality)
    assert status == True

    image_name = 'foo.fits'
    status = update_db_2.update_image(image_name, date_obs, tel=tel, 
                inst=inst,filt=filt, grp_id=grp_id, track_id=track_id, 
                req_id='', quality=quality)
    assert status == False

def test_add_sub_request():
    
    sr_id = '1477711'
    request_grp_id='ROME20180412T16.93534273'
    request_track_id = '624354'
    window_start = datetime.strptime('2018-04-20T15:30:00',"%Y-%m-%dT%H:%M:%S")
    window_start = window_start.replace(tzinfo=pytz.UTC)
    window_end = datetime.strptime('2018-04-20T16:00:00',"%Y-%m-%dT%H:%M:%S")
    window_end = window_end.replace(tzinfo=pytz.UTC)
    status = 'PENDING'
    time_executed = None
    
    (submit_ok, message) = update_db_2.add_sub_request(sr_id,
                                            request_grp_id, request_track_id,
                                            window_start, window_end, 
                                            status, time_executed)
    print message
    assert submit_ok == False
    
    (submit_ok, message) = update_db_2.add_sub_request(sr_id,
                                            request_grp_id, request_track_id,
                                            window_start, window_end, 
                                            status, time_executed)
    print message
    assert submit_ok == False
    assert 'Subrequest already exists' in message

def test_update_sub_request():
    
    sr_id = '1477711'
    request_grp_id='ROME20180412T16.93534273'
    request_track_id = '624354'
    window_start = datetime.strptime('2018-04-20T15:30:00',"%Y-%m-%dT%H:%M:%S")
    window_start = window_start.replace(tzinfo=pytz.UTC)
    window_end = datetime.strptime('2018-04-20T16:00:00',"%Y-%m-%dT%H:%M:%S")
    window_end = window_end.replace(tzinfo=pytz.UTC)
    status = 'PENDING'
    time_executed = None
    
    (submit_ok, message) = update_db_2.add_sub_request(sr_id,
                                            request_grp_id, request_track_id,
                                            window_start, window_end, 
                                            status, time_executed)
    assert submit_ok == False
    
    time_executed = datetime.strptime('2018-04-20T15:15:00',"%Y-%m-%dT%H:%M:%S")
    time_executed = time_executed.replace(tzinfo=pytz.UTC)
    
    (submit_ok, message) = update_db_2.update_sub_request(sr_id,
                                            request_grp_id, request_track_id,
                                            window_start, window_end, 
                                            status, time_executed)
    print message
    assert submit_ok == True
    assert 'Subrequest updated' in message

def test_update_tap_status():
    
    event_pk = '3344'
    qs = Event.objects.filter(pk=event_pk)
    event = qs[0]
    priority = 'A'
    
    (submit_ok, message) = update_db_2.update_tap_status(event, priority)

    print submit_ok, message
    assert submit_ok == True
    assert 'TAP status updated' in message


def test_update_event_status():
    
    event_pk = '3372'
    qs = Event.objects.filter(pk=event_pk)
    event = qs[0]
    status = 'AN'
    
    (submit_ok, message) = update_db_2.update_event_status(event, status)

    print submit_ok, message
    assert submit_ok == True
    assert 'event status updated' in message
    
if __name__ == '__main__':
   test_update_event_status()