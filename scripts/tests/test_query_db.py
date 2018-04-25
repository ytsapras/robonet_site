# -*- coding: utf-8 -*-
"""
Created on Sun Mar 19 12:23:44 2017

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
import pytz
setup()
from events.models import Event, EventName, SingleModel
import query_db
import utilities

def test_get_active_obs():
    
    qs = query_db.get_active_obs()
    
    assert qs.count > 0
    if len(qs) > 0:
        assert hasattr(qs[0],'field') and hasattr(qs[0],'request_type')

def test_select_obs_by_date():
    
    tstart = datetime.strptime('2018-04-16T00:00:00','%Y-%m-%dT%H:%M:%S')
    tstart = tstart.replace(tzinfo=pytz.UTC)
    tend = datetime.strptime('2018-04-24T00:00:00','%Y-%m-%dT%H:%M:%S')
    tend = tend.replace(tzinfo=pytz.UTC)
    
    criteria = { 'timestamp': tstart,
                 'time_expire': tend,
                 'request_status': 'AC'}

    qs = query_db.select_obs_by_date(criteria)
    
    assert qs.count > 0
    if len(qs) > 0:
        assert hasattr(qs[0],'field') and hasattr(qs[0],'request_type')
        
     
def test_get_old_active_obs():

    qs = query_db.get_old_active_obs()
    
    assert qs.count > 0
    if len(qs) > 0:
        assert hasattr(qs[0],'field') and hasattr(qs[0],'request_type')
    
def test_get_tap_list():
    
    qs = query_db.get_tap_list()
    
    assert qs.count > 0
    
def test_get_event():
    
    known_events = Event.objects.all()
    e = known_events[0]
    event = query_db.get_event(e.pk)
    assert hasattr(event,'ev_ra') and hasattr(event,'ev_dec')

def test_get_event_names():
    
    event_id = 1010
    qs = query_db.get_event_names(event_id)
    assert qs.count >= 1
    

def test_get_event_name_list():
    
    event_id = 1010
    names = query_db.get_event_name_list(event_id)
    assert len(names) >= 1
    
def test_get_last_single_model():
    
    event_name = 'MOA-2008-BLG-0006'
    event_id = EventName.objects.get(name=event_name).event_id
    event = Event.objects.get(id=event_id)
    
    model = query_db.get_last_single_model(event=event)
    assert hasattr(model,'Tmax') and hasattr(model,'umin')
    
    model = query_db.get_last_single_model(event=event, modeler='ARTEMiS')
    assert hasattr(model,'Tmax') and hasattr(model,'umin')
    
def test_get_field_id():
    
    event_name = 'MOA-2008-BLG-0006'
    ra = '17:52:39.22'
    dec = '-28:54:02.94'
    in_field = 'ROME-FIELD-03'
    
    (id_field,rate) = query_db.get_event_field_id(ra,dec)
    
    assert id_field == in_field
    
def test_get_coords_in_degs():
    
    ra_str = '17:52:39.22'
    dec_str = '-28:54:02.94'
    ra_deg = 268.1634166666667
    dec_deg = -28.900816666666664
    
    # Test that sexigesimal coordinates are properly converted:
    (test_ra_deg, test_dec_deg) = query_db.get_coords_in_degrees(ra_str,dec_str)
    
    assert test_ra_deg == ra_deg
    assert test_dec_deg == dec_deg
    
    # Test that coordinates already in degrees are not converted:
    (test_ra_deg, test_dec_deg) = query_db.get_coords_in_degrees(ra_deg,dec_deg)
    
    assert test_ra_deg == ra_deg
    assert test_dec_deg == dec_deg

def test_get_event_by_name():
    
    event_name = 'MOA-2008-BLG-0006'
    ra = '17:52:39.22'
    dec = '-28:54:02.94'
    (event,message) = query_db.get_event_by_name(event_name)
    assert event.ev_ra == ra
    assert event.ev_dec == dec
    
def test_get_events_within_radius():
    
    ra = '17:52:39.22'
    dec = '-28:54:02.94'
    radius = 2.0
    events_list = query_db.get_events_within_radius(ra, dec, radius)
    assert len(events_list) == 1
    
    ra = '17:58:27.51'
    dec = '-29:20:30.38'
    radius = 4.0
    events_list = query_db.get_events_within_radius(ra, dec, radius)
    assert len(events_list) == 1
    
def test_get_image_rejection_statistics():
    
    stats = query_db.get_image_rejection_statistics()
    d = {'Accepted': 0}    
    assert type(stats) == type(d)
    assert 'Accepted' in stats.keys()
    assert len(stats) > 1
    
def test_check_image_in_db():
    
    status = query_db.check_image_in_db('cpt1m010-fl16-20170403-0197-e91.fits')
    assert status == True
    status = query_db.check_image_in_db('cpt1m010-foo-20170403-bar-e91.fits')
    assert status == False

def test_get_subrequests_for_obsrequest():

    obs_grp_id = 'REALO20180422T20.59241671'
    
    qs = query_db.get_subrequests_for_obsrequest(obs_grp_id)
    
    assert len(qs) > 0

        
if __name__ == '__main__':
    
    test_get_subrequests_for_obsrequest()
    