# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 10:55:03 2017

@author: rstreet
"""


from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from events.models import Field, ObsRequest
from sys import exit
from scripts import query_db

class Command(BaseCommand):
    help = ''
    
    def add_arguments(self, parser):
        parser.add_argument('field', nargs='+', type=str)
        
    def _fetch_obs_for_field(self,*args, **options):
        field_name = options['field'][0]
        field_id = Field.objects.get(name=field_name).id
        
        print '\nActive obs for '+field_name+':\n'
        active_obs = query_db.get_active_obs()
        for obs in active_obs:
            print obs.grp_id, obs.timestamp, obs.time_expire
        
    def handle(self,*args, **options):
        self._fetch_obs_for_field(*args,**options)
