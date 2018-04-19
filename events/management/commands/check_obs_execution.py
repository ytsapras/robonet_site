# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 11:34:05 2018

@author: rstreet
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from events.models import Field, ObsRequest
from sys import exit
from scripts import lco_api_tools

class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        parser.add_argument('token', nargs='+', type=str)
            
    def _fetch_obs_tracking_ids(self,*args, **options):
        
        token = options['token'][0]
        
        qs = ObsRequest.objects.exclude(request_status='CN')

        unique_obs = {}
        
        for obs in qs:
            
            if obs.track_id not in unique_obs.keys():
                
                unique_obs[str(int(obs.track_id))] = obs

        f = open('obs_execution.log','w')
        f.write('# Group_id  track_id  TS_submit  Site   n_subrequests  n_subrequests_successful\n')

        id_list = unique_obs.keys()
        id_list.sort()
        
        for track_id in id_list:
            
            obs = unique_obs[track_id]
            
            (states, completed_ts, windows) = lco_api_tools.get_subrequests_status(token,track_id)
            
            n_success = 0
            for entry in completed_ts:
                if entry != None:
                    n_success += 1
            
            f.write(obs.grp_id+' '+track_id+' '+obs.timestamp.strftime("%Y-%m-%dT%H:%M:%S")+' '+\
                    obs.which_inst+' '+str(len(states))+' '+str(n_success)+'\n')
            f.flush()
            
        f.close()
        
    def handle(self,*args, **options):
        self._fetch_obs_tracking_ids(*args,**options)
