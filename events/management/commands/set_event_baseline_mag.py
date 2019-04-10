# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 19:14:10 2019

@author: rstreet
"""


from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from events.models import Event
from sys import exit
from os import path
import glob
from scripts import artemis_subscriber
from scripts import log_utilities

class Command(BaseCommand):
    help = 'Sets the status of a specific event'
        
    def handle(self,*args, **options):
        
        config = artemis_subscriber.read_config()
        
        log = artemis_subscriber.init_log(config)

        data_files = glob.glob( path.join(config['data_local_location'],
                                              '???1*I.dat') )
                                              
        for f in data_files:

            short_name = path.basename(f).split('.')[0][1:-1]

            align_file = path.basename(f).split('.')[0][1:-1]+'.align'
            align_file = path.join(config['models_local_location'],align_file)
            
            model_file = align_file.replace('.align','.model')
            
            if path.isfile(model_file):
                artemis_subscriber.sync_data_align_files_with_db(config,f,
                                                                 align_file,log)
        
        log_utilities.end_day_log( log )
        