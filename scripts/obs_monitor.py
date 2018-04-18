# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 15:30:36 2018

@author: rstreet
"""
import os
import sys
from local_conf import get_conf
robonet_site = get_conf('robonet_site')
sys.path.append(robonet_site)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'robonet_site.settings')
from django.core import management
from django.conf import settings
from django.utils import timezone
from django import setup
from events.models import ObsRequest

def get_obs_request_status(start_date,end_date):
    """Function to determine the status of all observation requests within
    a specified time period. 
    
    Inputs:
        :param datetime start_date: Start of observing period
        :param datetime end_date: End of observing period
    """
    
    qs = ObsRequest.objects.all().exclude(request_status = 'CN').\
            filter(timestamp__lte=end_date).filter(time_expire__gt=start_date)
    
    for obs in qs:
        
        print(obs.grp_id+' '+obs.track_id+' '+\
                obs.timestamp.strftime("%Y-%m-%dT%H:%M:%S")+' - '+\
                obs.time_expire.strftime("%Y-%m-%dT%H:%M:%S"))