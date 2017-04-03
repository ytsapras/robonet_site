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

from events.models import ObsRequest, Tap, Event, SingleModel
from events.models import EventName
from observation_classes import get_request_desc
from event_classes import TapEvent

def get_active_obs(log=None):
    """Function to extract a list of the currently-active observations 
    requests from the database"""
    
    now = timezone.now()
    qs = ObsRequest.objects.filter(
                    time_expire__gt = now,
                    timestamp__lte = now,
                    request_status='AC'
                    )
    
    if log != None:
        log.info('\n')
        log.info('Queried DB for list of active observations:')
        if qs.count() == 0:
            log.info('DB returned no currently-active observation requests')
        else:
            for q in qs:
                log.info(' '.join([q.grp_id, q.field.name,\
                            get_request_desc(q.request_type), \
                            'submitted=',q.timestamp.strftime('%Y-%m-%dT%H:%M:%S'), \
                            'expires=',q.time_expire.strftime('%Y-%m-%dT%H:%M:%S'),\
                            'status=',q.request_status]))
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

def get_tap_list(log=None):
    """Function to query the DB and return the list of targets recommended 
    for REA-mode observations by TAP, and the details of those 
    observations"""
    
    tap_list = []
    qs = Event.objects.filter(status='MO')
    for q in qs:
        names = get_event_names(q.pk)
        name = ''
        for n in names:
            if len(name) == 0:
                name += n.name
            else:  
                name += '/' + n.name
        target = TapEvent()
        target.event_id = q.pk
        target.names = name
        target.field = q.field
        target.ev_ra = q.ev_ra
        target.ev_dec = q.ev_dec
        target.tap_status = q.status
        
        tap_entry = Tap.objects.filter(event=q.pk)[0]
        target.priority = tap_entry.priority
        target.tsamp = float(tap_entry.tsamp)
        target.texp = float(tap_entry.texp)
        target.nexp = int(tap_entry.nexp)
        target.telclass = tap_entry.telclass+'0'
        target.omega = tap_entry.omega
        target.passband = tap_entry.passband
        target.ipp = float(tap_entry.ipp)
        tap_list.append(target)
        
    if log != None:
        log.info('\n')
        log.info('Queried DB for list of current TAP list:')
        for target in tap_list:
            log.info(target.summary())
        log.info('\n')
                        
    return tap_list

def target_field(ev_ra,ev_dec):
    """Function to identify the field a given target lies in"""
    

def get_last_single_model(event,modeler=None,log=None):
    """Function to return the last model submitted to the DB by the 
    modeler given
    Inputs:
        events    Event object
        modeler   String       Name of originator of model
    """
    
    if modeler==None:
        qs = SingleModel.objects.filter(event=event).order_by('last_updated')
    else:
        qs = SingleModel.objects.filter(
                                        event=event
                                        ).filter(
                                        modeler=modeler
                                        ).order_by('last_updated')
    for q in qs:
        print q.modeler, q.last_updated
    
    try:    
        model = qs[0]
    except IndexError:
        model = None
        
    if log != None:
        log.info('\n')
        log.info('Queried DB for last single-lens model for this event:')
        log.info(' '.join([model.modeler,\
                        't_0='+str(model.Tmax),'t_E='+str(model.tau),\
                        'u_0='+str(model.umin)]))
        log.info('\n')
   
    return model

def get_event(event_pk):
    """Function to extract an event object from the DB based on its 
    primary key)
    Inputs:
            event_pk    int    Primary key of known event in DB
    """
    
    qs = Event.objects.get(pk=event_pk)
    return qs

def get_event_names(event_id):
    """Function to extract the names of a target, given its position
    on sky, with RA and Dec in decimal degrees"""
    
    qs = EventName.objects.filter(event_id=event_id)
    return qs
    
if __name__ == '__main__':
    get_rea_targets()