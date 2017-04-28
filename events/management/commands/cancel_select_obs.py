# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 20:42:19 2017

@author: rstreet
"""

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
    
    def add_arguments(self, parser):
        parser.add_argument('file_path', nargs='+', type=str)
        
    def _cancel_select_obs(self,*args,**options):
        file_path = options['file_path'][0]
        file_lines = open(file_path,'r').readlines()
        obs_id_list = []
        for item in file_lines:
            obs_id_list.append( item.replace('\n','') )
            
        obs_list = ObsRequest.objects.all()
        
        for obs in obs_list:
            if obs.grp_id in obs_id_list:
                obs.request_status = 'CN'
                obs.save()
            
    def handle(self,*args, **options):
        self._cancel_select_obs(*args,**options)
