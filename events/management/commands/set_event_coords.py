# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 13:41:51 2019

@author: rstreet
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from events.models import Event
from sys import exit
from scripts import utilities

class Command(BaseCommand):
    help = 'Sets the status of a specific event'
        
    def handle(self,*args, **options):
        
        events = Event.objects.all()
        
        for e in events:
            (ra, dec) = utilities.sex2decdeg(e.ev_ra,e.ev_dec)
            
            e.ra = ra
            e.dec = dec
            
            print ' -> Setting coordinates of event '+str(e.ra)+', '+str(e.dec)
            e.save()
        