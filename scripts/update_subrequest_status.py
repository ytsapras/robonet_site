# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 09:38:09 2018

@author: rstreet
"""
import os
import sys
cwd = os.getcwd()
sys.path.append(os.path.join(cwd,'..'))
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
        
    params = {'timestamp': start_date.strftime("%Y-%m-%dT%H:%M:%S"),
              'time_expire': end_date.strftime("%Y-%m-%dT%H:%M:%S"),
              'request_status': 'AC'}
              
    obs_list = api_tools.get_obs_list(config,params,testing=bool(config['testing'])
    
    log.info('Database reports '+str(len(obs_list))+' observation(s) within this timeframe')
    
    active_obs = lco_api_tools.get_status_active_obs_subrequests(obs_list,
                                                                 config['token'],
                                                                 start_date,
                                                                 end_date,
                                                                 log=log)
    
    log.info('Returned data for '+str(len(active_obs))+' observation(s)')
    
    for grp_id, obs_dict in active_obs.items():
        
        obs = obs_dict['obsrequest']
        subrequests = obs_dict['subrequests']
        
        log.info(' -> '+obs['grp_id']+' has '+str(len(subrequests))+' subrequests:')
        
        for sr in subrequests:
            
            params = {'sr_id': sr.sr_id,
                      'grp_id': obs['grp_id'],
                      'track_id': obs['track_id'],
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
    
    update_subrequest_status(look_back_days=5.0)
    