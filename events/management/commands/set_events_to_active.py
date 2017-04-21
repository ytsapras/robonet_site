# -*- coding: utf-8 -*-
"""
Created on Fri Apr 21 15:15:03 2017

@author: rstreet
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from events.models import Event, EventName
from sys import exit
from scripts import update_db_2, query_db

class Command(BaseCommand):
    help = ''
        
    def _set_events_to_active(self,*args, **options):
        
        events_in_footprint = Event.objects.all().filter(field__lte=20)
        
        for event in events_in_footprint:
            eventnames = EventName.objects.filter(event=event.id)
            name_str = ''
            for name in eventnames:
                name_str += name.name+'/'
            name_str = name_str[:-1]
            
            (id_field,rate) = query_db.get_event_field_id(event.ev_ra,event.ev_dec)
            print name_str, event.field, event.year, event.ev_ra, event.ev_dec, event.status, event.year, id_field
            
            if '2017' in name_str and event.status != 'AC':
                print ' -> Resetting status of event '+str(event.id)+', currently: '+str(event.status)
                event.status='AC'
                event.save()
                event = Event.objects.filter(id=event.id)[0]
                print ' -> Now: '+str(event.status)
                
        print '\nNumber of events in ROMEREA footprint: '+str(events_in_footprint.count())
        
    def handle(self,*args, **options):
        self._set_events_to_active(*args,**options)
