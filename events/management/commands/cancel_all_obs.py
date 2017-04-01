# -*- coding: utf-8 -*-
"""
Created on Sat Apr  1 13:08:01 2017

@author: rstreet
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from events.models import ObsRequest

class Command(BaseCommand):
    args = ''
    help = ''
    
    def _cancel_all_obs(self):
        obs_list = ObsRequest.objects.all()
        for obs in obs_list:
            obs.request_status = 'CN'
            obs.save()
            
    def handle(self,*args, **options):
        self._cancel_all_obs()
