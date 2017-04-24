# -*- coding: utf-8 -*-
"""
Created on Fri Apr 21 09:49:08 2017

@author: rstreet
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from events.models import Event, EventName, SingleModel
from sys import exit
from scripts import update_db_2, query_db

class Command(BaseCommand):
    help = ''
    
    def add_arguments(self, parser):
        parser.add_argument('eventname', nargs='+', type=str)
        parser.add_argument('ra', nargs='+', type=str)
        parser.add_argument('dec', nargs='+', type=str)
        
    def _check_event_in_db(self,*args, **options):
        event_name = str(options['eventname'][0]).split('=')[-1]
        ra = str(options['ra'][0]).split('=')[-1]
        dec = str(options['dec'][0]).split('=')[-1]
        
        got_name = False
        got_coords = False
        
        print 'Searching for event name: '+repr(event_name)+\
            ' at location '+repr(ra)+' '+repr(dec)
                
        if update_db_2.check_exists(event_name)==True:
            got_name = True
            event_id = EventName.objects.get(name=event_name).event_id
            event = Event.objects.get(id=event_id)
            print ' -> Event in DB with ID '+str(event_id)+\
                ' and location '+str(event.ev_ra)+' '+str(event.ev_dec)
        else:
            print ' -> Event name not recognized by DB'
            
        (id_field, rate) = query_db.get_event_field_id(ra,dec)
        print ' -> Field check results: '+str(id_field)+\
                        ' contains event at sky location '+\
                        str(ra)+' '+str(dec)
        
        event = query_db.get_event_by_position(ra,dec)
        print ' -> Searched for event by position and found: '+repr(event)
        if event != None:
            got_coords = True
        
        eventnames = EventName.objects.filter(event=event.id)
        print ' -> Object known under event names:'
        for evname in eventnames:
            print ' --> '+str(evname.name)
        
        if got_name == True and got_coords == False:
            print '\nWARNING: EventName entry without a corresponding Event entry in DB'
        elif got_name == False and got_coords == True:
            print '\nWARNING: Event entry with a corresponding EventName entry in DB'
        
        
    def handle(self,*args, **options):
        self._check_event_in_db(*args,**options)
