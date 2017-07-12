# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 11:31:48 2017

@author: rstreet
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from events.models import EventName, Event
from sys import exit

class Command(BaseCommand):
    help = ''
        
    def _remove_old_events(self,*args, **options):
        
        moa_events = EventName.objects.all().filter(name__contains='MOA-2008')
        ogle_events = EventName.objects.all().filter(name__contains='OGLE-2008')
        
        for event in moa_events:
            Event.objects.filter(id=event.event_id).delete()
            print('Removed event '+event.name+', ID='+str(event.event_id))
        
        for event in ogle_events:
            Event.objects.filter(id=event.event_id).delete()
            print('Removed event '+event.name+', ID='+str(event.event_id))
            
    def handle(self,*args, **options):
        self._remove_old_events(*args,**options)
        