# -*- coding: utf-8 -*-
"""
Created on Tue May 30 16:35:28 2017

@author: rstreet
"""


from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from events.models import Event
from scripts import fixes

class Command(BaseCommand):
    args = ''
    help = ''

    def _fix_nf(self,*args,**options):
        fixes.notnf()
            
    def handle(self,*args, **options):
        self._fix_nf(*args,**options)
