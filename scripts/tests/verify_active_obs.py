# -*- coding: utf-8 -*-
"""
Created on Sat Apr  1 13:57:18 2017

@author: rstreet
"""

from os import getcwd, path, remove, environ
from sys import path as systempath
import socket
host_name = socket.gethostname()
if 'einstein' in host_name:
   cwd = '/var/www/robonetsite/scripts/tests'
else:
    cwd = getcwd()
systempath.append(path.join(cwd,'..'))
from local_conf import get_conf
robonet_site = get_conf('robonet_site')
systempath.append(robonet_site)
environ.setdefault('DJANGO_SETTINGS_MODULE', 'robonet_site.settings')
from django.core import management
from django.conf import settings
from django.utils import timezone
from django import setup
from datetime import datetime, timedelta
setup()
import obs_control, log_utilities
from events.models import ObsRequest, Field
import query_db

def list_active_obs():

    print 'Current UTC: ',timezone.now()
    
    active_obs = query_db.get_active_obs()

    print 'Found '+str(len(active_obs))+' active observation requests'
    
    for obs in active_obs:
        print ' '.join([obs.grp_id, obs.field.name,\
                        'submitted=',obs.timestamp.strftime('%Y-%m-%dT%H:%M:%S'), \
                        'expires=',obs.time_expire.strftime('%Y-%m-%dT%H:%M:%S'),\
                        'status=',obs.request_status])

if __name__ == '__main__':
    list_active_obs()