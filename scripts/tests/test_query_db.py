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
setup()
from events.models import Event, EventName, SingleModel
import query_db
import utilities

def test_get_active_obs():
    
    qs = query_db.get_active_obs()
    
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
    
    event_id = 460
    qs = query_db.get_event_names(event_id)
    assert qs.count >= 1
    

def test_get_last_single_model():
    
    event_name = 'OGLE-2012-BLG-0970'
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
    