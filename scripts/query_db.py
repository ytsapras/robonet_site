# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 18:50:24 2017

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
from datetime import datetime, timedelta
setup()

from events.models import ObsRequest
from observation_classes import get_request_desc

def get_active_obs(log=None):
    """Function to extract a list of the currently-active observations 
    requests from the database"""
        
    qs = ObsRequest.objects.filter(
                    time_expire__gt = datetime.utcnow() 
                    ).exclude(
                    timestamp__lte = datetime.utcnow()
                    )
    
    if log != None:
        log.info('\n')
        log.info('Queried DB for list of active observations:')
        for q in qs:
            log.info(' '.join([q.field.name,\
                        parse_req_type(q.request_type), \
                        'submitted=',q.timestamp.strftime('%Y-%m-%dT%H:%M:%S'), \
                        'expires=',q.time_expire.strftime('%Y-%m-%dT%H:%M:%S')]))
        log.info('\n')
                        
    return qs

if __name__ == '__main__':
    get_active_obs(debug=True)