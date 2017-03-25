# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 18:50:24 2017

@author: rstreet
"""
import os
import sys
from local_conf import get_conf
robonet_site = get_conf('robonet_site')
sys.path.append(robonet_site)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'robonet_site.settings')
from django.core import management
from django.conf import settings
from django.utils import timezone
from django import setup
from datetime import datetime, timedelta
setup()

from events.models import ObsRequest, Tap, Event
from observation_classes import get_request_desc

def get_active_obs(log=None):
    """Function to extract a list of the currently-active observations 
    requests from the database"""
        
    qs = ObsRequest.objects.filter(
                    time_expire__gt = datetime.utcnow() 
                    ).exclude(
                    timestamp__lte = datetime.utcnow()
                    )
    
    if log != None:
        log.info('\n')
        log.info('Queried DB for list of active observations:')
        for q in qs:
            log.info(' '.join([q.field.name,\
                        get_request_desc(q.request_type), \
                        'submitted=',q.timestamp.strftime('%Y-%m-%dT%H:%M:%S'), \
                        'expires=',q.time_expire.strftime('%Y-%m-%dT%H:%M:%S')]))
        if len(qs) == 0:
            log.info('DB returned no currently-active observation requests')
        log.info('\n')
                        
    return qs

def get_rea_targets(log=None):
    """Function to query the DB for a list of targets recommended for 
    observation under the REA strategy."""
    
    qs = Tap.objects.filter(omega__gte=6.0).order_by('timestamp').reverse()
    print qs
    for q in qs:
        print q.event.ev_ra, q.tsamp,q.priority
    
    if log != None:
        log.info('\n')
        log.info('Queried DB for list of current REA targets:')
        for q in qs:
            log.info(' '.join([q.event.field.name,\
                        'priority=',q.priority, \
                        't_sample=',str(q.tsamp)]))
        log.info('\n')
                        
    return qs

if __name__ == '__main__':
    get_rea_targets()