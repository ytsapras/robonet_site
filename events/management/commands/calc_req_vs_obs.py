# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 13:15:42 2017

@author: rstreet
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from events.models import ObsRequest, Image
from sys import exit
from scripts import query_db

class Command(BaseCommand):
    help = ''
        
    def _calc_req_vs_obs(self,*args, **options):
        
        log = open('req_vs_obs.txt','w')
        
        obs_requests = ObsRequest.objects.all().exclude(request_status = 'CN')
        
        log.write(str(len(obs_requests))+' obs requests in the database\n')
        
        images = Image.objects.all()
        
        log.write(str(len(images))+' images in the database\n')
        
        obs_grp_ids = {}
        for i,obs in enumerate(obs_requests):
            
            if obs.grp_id not in obs_grp_ids:
                
                obs_grp_ids[obs.grp_id] = []
        
        log.write('Found '+str(len(obs_grp_ids))+\
                    ' unique observation request groups\n')
        
        image_names = []
        for im in images:
            
            if im.image_name not in image_names:
                
                image_names.append(im.image_name)
        
        log.write('Found '+str(len(image_names))+\
                    ' unique image names\n')
                    
        log.write('\n')
        
        unknowns = []
        for image in images:
            
            if image.grp_id in obs_grp_ids.keys():
                
                obslist = obs_grp_ids[image.grp_id]
                
                if image.image_name not in obslist:
                    obslist.append(image.image_name)
                
                obs_grp_ids[image.grp_id] = obslist
            
            else:
                
                if image.image_name not in unknowns:
                    unknowns.append(image.image_name)
                
                log.write('Image '+image.image_name+' has unknown group ID '+\
                        str(image.grp_id)+'\n')

        log.write('\n')
        
        no_obs = 0
        obs_taken = 0
        image_count = 0
        for obs,obslist in obs_grp_ids.items():
            
            if len(obslist) == 0:
                
                no_obs += 1
            
            else:
            
                obs_taken += 1
                
                image_count += len(obslist)
                
                log.write('Acquired '+str(len(obslist))+' images for '+obs+'\n')
            
        log.write('\nFound '+str(no_obs)+' requests without any observations made '+\
                str( (float(no_obs)/float(len(obs_grp_ids)))*100.0 ) +'% of total\n')
        log.write('\nFound '+str(obs_taken)+' requests where observations were made '+\
                str( (float(obs_taken)/float(len(obs_grp_ids)))*100.0 ) +'% of total\n')
        log.write('\n'+str(image_count)+' images obtained as a result\n')
        log.write('\nFound '+str(len(unknowns))+' unidentified observations made '+\
                str( (float(len(unknowns))/float(len(obs_grp_ids)))*100.0 ) +'% of total\n')
        
        log.close()
        
    def handle(self,*args, **options):
        self._calc_req_vs_obs(*args,**options)
