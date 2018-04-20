# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 09:38:09 2018

@author: rstreet
"""
import os
import sys
cwd = os.getcwd()
sys.path.append(os.path.join(cwd,'..'))
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

from datetime import datetime, timedelta
import pytz
import obs_monitor
import lco_api_tools
import config_parser

def update_subrequest_status(look_back_days=1.0):
    """Function to update the status of all sub-observing requests that 
    derive from the cadence observation requests submitted for ROME/REA.
    
    Inputs:
        :param float look_back_days: Sets the window, from now back in time,
                                     to select observations to be updated.
    """

    config = config_parser.read_config_for_code('setup')    

    start_date = datetime.now() - timedelta(days=look_back_days)
    start_date = start_date.replace(tzinfo=pytz.UTC)
    end_date = datetime.now()
    end_date = end_date.replace(tzinfo=pytz.UTC)
    
    active_obs = lco_api_tools.get_status_active_obs_subrequests(config['token'],
                                                   start_date,end_date)
    
    
    # Submit the updated status information to the DB
    
    