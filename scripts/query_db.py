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


def get_active_obs(debug=False):
    """Function to extract a list of the currently-active observations 
    requests from the database"""

    qs = ObsRequest.objects.filter(
                    time_expire__gt = datetime.utcnow() 
                    ).exclude(
                    timestamp__lte = datetime.utcnow()
                    )
    
    if debug == True:
        for q in qs:
            print q.field, q.request_type, q.timestamp, q.time_expire
    return qs

if __name__ == '__main__':
    get_active_obs(debug=True)