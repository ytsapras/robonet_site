# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 16:54:32 2017

@author: rstreet
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from events.models import Event, EventName, SingleModel
from sys import exit
from scripts import update_db_2

class Command(BaseCommand):
    help = ''
    
    def add_arguments(self, parser):
        parser.add_argument('eventname', nargs='+', type=str)
        
    def _fetch_models_for_event(self,*args, **options):
        event_name = options['eventname'][0]
        
        if update_db_2.check_exists(event_name)==True:
            event_id = EventName.objects.get(name=event_name).event_id
            event = Event.objects.get(id=event_id)
            models = SingleModel.objects.filter(event=event)
            for m in models:
                print m.modeler, m.tau, m.Tmax, m.umin,m.last_updated
        else:
            print 'Event name not recognized by DB'
            
    def handle(self,*args, **options):
        self._fetch_models_for_event(*args,**options)
