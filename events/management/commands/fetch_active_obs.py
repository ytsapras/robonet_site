# -*- coding: utf-8 -*-
"""
Created on Sat Apr  1 15:19:41 2017

@author: rstreet
"""


from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from events.models import ObsRequest
from scripts import query_db

class Command(BaseCommand):
    args = ''
    help = ''
    
    def _fetch_active_obs(self):
        qs = query_db.get_active_obs()
        for q in qs:
            print ' '.join([q.grp_id, q.field.name,\
                        'submitted=',q.timestamp.strftime('%Y-%m-%dT%H:%M:%S'), \
                        'expires=',q.time_expire.strftime('%Y-%m-%dT%H:%M:%S'),\
                        'status=',q.request_status])
            
    def handle(self,*args, **options):
        self._fetch_active_obs()
