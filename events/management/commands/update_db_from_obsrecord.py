# -*- coding: utf-8 -*-
"""
Created on Tue May  7 11:17:26 2019

@author: rstreet
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from events.models import ObsRequest, Field
from sys import exit
from scripts import utilities
from scripts import update_db_2
from os import path
from datetime import datetime
import pytz
import time

class Command(BaseCommand):
    help = ''
            
    def add_arguments(self, parser):
        parser.add_argument('obsrecord_file', nargs='+', type=str)
        
    def _update_db_from_obsrecord(self,*args, **options):
        
        if path.isfile(options['obsrecord_file'][0]):
            
            file_lines = open(options['obsrecord_file'][0],'r').readlines()
            
            obs_list = []
            for line in file_lines:
                
                if line[0:1] != '#':
                    entries = line.replace('\n','').split()
                    record = ObsRecord(entries)
                    
                    print(record.summary())
                    
                    qs = ObsRequest.objects.filter(grp_id=record.grp_id, 
                                                   which_filter=record.which_filter)
                    
                    if len(qs) == 0:
                        obs = record.build_obs_object()
                        obs_list.append(obs)
                        print(' -> Added to observation list')
            
            print('Total of '+str(len(obs_list))+' observations to ingest')
            
            if len(obs_list) > 0:
                ObsRequest.objects.bulk_create(obs_list)
                
                print('Completed ingest')
                
    def handle(self,*args, **options):
        self._update_db_from_obsrecord(*args,**options)

# Sampling interval in min, cadence in hours
# Tel needs to be one of pfrm_on, onem_on, twom_on
# Request type needs to be 'A':'REA High - 20 min cadence',
#		    'M':'REA Low - 60 min cadence', 
#		    'L':'ROME Standard - every 7 hours'
      
class ObsRecord():
    
    def __init__(self, entries=[]):
        
        self.params = ['grp_id','track_id','req_id','which_site',
                       'pfrm_on', 'onem_on', 'twom_on',
                       'which_inst', 'field','request_type',
                       'which_filter', 'exptime',
                       'n_exp', 't_sample', 'timestamp', 'time_expire',                           
                       'request_status']
                           
        for par in self.params:
            setattr(self,par,None)
    
        if len(entries) > 0:
            self.grp_id = entries[0]
            self.track_id = entries[1]
            self.req_id = entries[2]
            self.which_site = entries[3]
            self.which_inst = entries[6]
            self.which_filter = entries[11]
            self.n_exp = int(float(entries[13]))
            self.field = entries[7]
            
            if '1m0' in entries[5]:
                self.onem_on = True
                self.pfrm_on = False
                self.twom_on = False
            elif '2m0' in entries[5]:
                self.onem_on = False
                self.pfrm_on = False
                self.twom_on = True
            elif '0m4' in entries[5]:
                self.onem_on = False
                self.pfrm_on = True
                self.twom_on = False
            
            if 'ROME' in entries[0]:
                self.request_type = 'L'
            else:
                self.request_type = 'M'
            
            self.t_sample = float(entries[14])*60
            self.exptime = int(float(entries[12]))
            self.timestamp = datetime.strptime(entries[16],"%Y-%m-%dT%H:%M:%S")
            self.timestamp = self.timestamp.replace(tzinfo=pytz.UTC)
            self.time_expire = datetime.strptime(entries[17],"%Y-%m-%dT%H:%M:%S")
            self.time_expire = self.time_expire.replace(tzinfo=pytz.UTC)
            self.request_status = 'AC'
    
    def summary(self):
        
        output = ''
        for key in self.params:
            output += ' '+str(getattr(self,key))
        return output
    
    def build_obs_object(self):
        
        field = Field.objects.get(name=self.field)
        #field_object = Field.objects.get(id=field.id)
        
        obs = ObsRequest(field=field, 
                         t_sample=self.t_sample, 
                         exptime=self.exptime,
                         timestamp=self.timestamp, 
                         time_expire=self.time_expire,
                         pfrm_on= self.pfrm_on, 
                         onem_on= self.onem_on, 
                         twom_on=self.twom_on, 
                         request_type=self.request_type, 
                         which_site=self.which_site, 
			       which_filter=self.which_filter,
			       which_inst=self.which_inst, 
                         grp_id=self.grp_id, 
                         track_id=self.track_id,
			       req_id=self.req_id, 
                          n_exp=self.n_exp, 
                          request_status=self.request_status)
                          
        return obs
        
    def save_to_db(self):
        
        print('Submitting observation with parameters: ')
        print(self.summary())
        
        status = update_db_2.add_request(self.field, self.t_sample, \
                    self.exptime, timestamp=self.timestamp, \
                    time_expire=self.time_expire, \
                    pfrm_on=self.pfrm_on, onem_on=self.onem_on, twom_on=self.twom_on, \
                    request_type=self.request_type, 
                    which_site=self.which_site,\
                    which_filter=self.which_filter, 
                    which_inst=self.which_inst, \
                    grp_id=self.grp_id, 
                    track_id=self.track_id, 
                    req_id=self.req_id,\
                    n_exp=self.n_exp,
                    request_status=self.request_status)
        
        print(self.grp_id+' submitted to DB with status '+repr(status))
        