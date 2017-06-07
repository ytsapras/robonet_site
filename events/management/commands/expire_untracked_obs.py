# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 17:15:02 2017

@author: rstreet
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from events.models import ObsRequest
from sys import exit
from scripts import update_db_2, query_db

class Command(BaseCommand):
    help = ''
        
    def _expire_untracked_obs(self,*args, **options):
        
        obs_set = ObsRequest.objects.all()
        
        for obs in obs_set:
            if obs.track_id == '9999999999':
                obs.request_status = 'CN'
                obs.save()
                print 'Updated obs with tracking ID='+str(obs.track_id)+' to '+str(obs.request_status)
            
    def handle(self,*args, **options):
        self._expire_untracked_obs(*args,**options)
