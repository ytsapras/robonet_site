# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 18:50:24 2017

@author: rstreet
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from events.models import ObsRequest
from datetime import datetime

class Command(BaseCommand):
    args = ''
    help = ''
    
    def _get_active_obs(self):
        """Function to extract a list of the currently-active observations 
        requests from the database"""
    
        qs = ObsRequest.objects.filter(
                        time_expire__gt = datetime.utcnow() 
                        ).exclude(
                        timestamp__lte = datetime.utcnow()
                        )
        print qs
        return qs
    
    def handle(self,*args,**options):
        self._get_active_obs()