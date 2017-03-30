# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 17:41:27 2017

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
import event_classes

e = event_classes.Lens()
e.name = 'OGLE-2017-BLG-0001'
e.survey_id = 'field 1'
e.ra = '17:18:19.20'
e.dec = '-25:26:27.28'
e.t0 = 2457000.0
e.te = 30.0
e.u0 = 0.1
e.a0 = 10.0
e.i0 = 20.0
e.origin = 'OGLE'
    
def test_get_event_field_id():
    (id_field, rate) = e.get_event_field_id()
    print id_field, rate
    
def test_sync_event_with_DB():
    
    last_updated = datetime.now()    
    
    e.sync_event_with_DB(last_updated)

if __name__ == '__main__':
    test_sync_event_with_DB()
    #test_get_event_field()
    