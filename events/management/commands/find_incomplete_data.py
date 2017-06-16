# -*- coding: utf-8 -*-
"""
Created on Fri Jun 16 14:26:42 2017

@author: rstreet
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from events.models import DataFile
from sys import exit
from scripts import query_db

class Command(BaseCommand):
    help = ''
        
    def add_arguments(self, parser):
        parser.add_argument('delete', nargs='+', type=str)
        
    def _find_incomplete_data(self,*args, **options):
        data_files = DataFile.objects.all()
        for data in data_files:
            if data.baseline == 0.0:
                if options['delete'][0] == 'delete':
                    print 'Removing incomplete data entry: '+data.datafile+\
                        ', g='+str(data.g)+', ibase='+str(data.baseline)
                    data.delete()
                else:
                    print 'Found incomplete data entry: '+data.datafile+\
                        ', g='+str(data.g)+', ibase='+str(data.baseline)
                        
    def handle(self,*args, **options):
        self._find_incomplete_data(*args,**options)
