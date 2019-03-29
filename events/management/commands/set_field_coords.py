# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 21:43:28 2019

@author: rstreet
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from events.models import Field
from astropy.coordinates import SkyCoord
from astropy import units as u

class Command(BaseCommand):
    help = 'Sets the field centre coordinates in decimal degrees'
        
    def handle(self,*args, **options):
        
        field_list = Field.objects.all()
        
        for f in field_list:
            
            if len(f.field_ra) > 0 and len(f.field_dec) > 0:
                c = SkyCoord(f.field_ra+' '+f.field_dec, frame='icrs', unit=(u.hourangle,u.deg))
                
                f.field_ra_decimal = c.ra.value
                f.field_dec_decimal = c.dec.value
                
                print ' -> Setting field coordinates: '+str(f.field_ra_decimal)+\
                                                   ', '+str(f.field_dec_decimal)
                f.save()
        