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
import api_tools
import log_utilities

def update_subrequest_status(look_back_days=1.0):
    """Function to update the status of all sub-observing requests that 
    derive from the cadence observation requests submitted for ROME/REA.
    
    Inputs:
        :param float look_back_days: Sets the window, from now back in time,
                                     to select observations to be updated.
    """

    config = config_parser.read_config_for_code('update_subrequests')    
    
    log = log_utilities.start_day_log( config, 'update_subrequests' )

    start_date = datetime.now() - timedelta(days=look_back_days)
    start_date = start_date.replace(tzinfo=pytz.UTC)
    end_date = datetime.now()
    end_date = end_date.replace(tzinfo=pytz.UTC)

    log.info('Updating the status of observations between '+\
                start_date.strftime("%Y-%m-%dT%H:%M:%S")+' and '+\
                end_date.strftime("%Y-%m-%dT%H:%M:%S"))
    
    log.info('Querying LCO API for observation sub-request status...')
    
    active_obs = lco_api_tools.get_status_active_obs_subrequests(config['token'],
                                                   start_date,end_date,log=log)
    
    log.info('Returned data for '+str(len(active_obs))+' observation(s)')
    
    for grp_id, obs_dict in active_obs.items():
        
        obs = obs_dict['obsrequest']
        subrequests = obs_dict['subrequests']
        
        log.info(' -> '+obs.grp_id+' has '+str(len(subrequests))+' subrequests:')
        
        for sr in subrequests:
            
            params = {'sr_id': sr.sr_id,
                      'grp_id': obs.grp_id,
                      'track_id': obs.track_id,
                      'window_start': sr.window_start.strftime("%Y-%m-%dT%H:%M:%S"),
                      'window_end': sr.window_end.strftime("%Y-%m-%dT%H:%M:%S"),
                      'status': sr.state}
                        
            if sr.time_executed != None:
                
                params['time_executed'] = sr.time_executed.strftime("%Y-%m-%dT%H:%M:%S")
            
            log.info(repr(params))
            
            message = api_tools.submit_sub_obs_request_record(config,params,
                                                              testing=bool(config['testing']))
                
            log.info(' --> Subrequest '+str(sr.sr_id)+': '+message)
            
    log_utilities.end_day_log( log )
  

if __name__ == '__main__':
    
    update_subrequest_status(look_back_days=1.0)
    