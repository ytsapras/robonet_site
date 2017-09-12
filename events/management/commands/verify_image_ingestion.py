# -*- coding: utf-8 -*-
"""
Created on Thu Sep  7 16:14:15 2017

@author: rstreet
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from events.models import Image
from sys import exit
from scripts import query_db

class Command(BaseCommand):
    help = ''
        
    def _verify_image_ingestion(self,*args, **options):
        images = Image.objects.all()
        
        remove = True
        
        log = open('image_ingestion.txt','w')
        for image in images:
            qs = Image.objects.filter(image_name = image.image_name).order_by('timestamp').reverse()
            if len(qs) > 1:
                log.write('Found '+str(len(qs))+' hits for image '+image.image_name+'\n')
                for i in range(1,len(qs),1):
                    if remove == True:
                        log.write('Removing '+qs[i].image_name+' '+\
                            qs[i].timestamp.strftime("%Y-%m-%dT%H:%M:%S")+\
                            ' '+qs[i].quality+'\n')
                        qs[i].delete()
                log.write('-> Keep '+qs[0].timestamp.strftime("%Y-%m-%dT%H:%M:%S")+'\n')
            else:
                log.write('Found single entry for image '+image.image_name+\
                    ', timestamp '+image.timestamp.strftime("%Y-%m-%dT%H:%M:%S")+\
                    ', quality: '+image.quality+'\n')
        log.close()
        
    def handle(self,*args, **options):
        self._verify_image_ingestion(*args,**options)
