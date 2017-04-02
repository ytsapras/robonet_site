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
from events.models import Event, SingleModel
import query_db
import utilities

def test_get_active_obs():
    
    qs = query_db.get_active_obs()
    
    assert qs.count() > 0
    if len(qs) > 0:
        assert hasattr(qs[0],'field') and hasattr(qs[0],'request_type')

def test_get_tap_list():
    
    qs = query_db.get_tap_list()
    
    assert qs.count() > 0
    
def test_get_event():
    
    known_events = Event.objects.all()
    e = known_events[0]
    event = query_db.get_event(e.pk)
    assert hasattr(event,'ev_ra') and hasattr(event,'ev_dec')

def test_get_event_names():
    
    event_id = 460
    qs = query_db.get_event_names(event_id)
    assert qs.count() >= 1
    

def test_get_last_single_model():
    
    known_events = Event.objects.all()
    e = known_events[5]
    event = query_db.get_event(e.pk)
    
    model = query_db.get_last_single_model(event=event)
    assert hasattr(model,'Tmax') and hasattr(model,'umin')
    
    model = query_db.get_last_single_model(event=event, modeler='pyLIMA')
    assert hasattr(model,'Tmax') and hasattr(model,'umin')
    