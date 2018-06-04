# -*- coding: utf-8 -*-
"""
Created on Sun Apr  2 09:34:30 2017

@author: rstreet
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from events.models import ObsRequest
from scripts import query_db

class Command(BaseCommand):
    args = ''
    help = ''
    
    def _fetch_tap_list(self):
        tap_list = query_db.get_tap_list()
        for target in tap_list:
            print target.summary()
            
    def handle(self,*args, **options):
        self._fetch_tap_list()
