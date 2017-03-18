# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 15:56:00 2017

@author: rstreet
"""
from sys import argv
import rome_obs
import rea_obs
import query_db
import update_db_2
import log_utilities

def obs_control():
    """Observation Control Software for the LCO Network
    
    This package is responsible for submitting the observations for the
    ROME and REA microlensing observing programs.
    """
    
    script_config = read_config()
    script_config = parse_args(script_config)
    
    log = log_utilities.start_day_log( script_config, 'obs_control' )
    log.info('Obs_control running in ' + script_config['MODE'] + ' mode')
    
    lock_state = log_utilities.lock( script_config, 'check', log )
    lock_state = log_utilities.lock( script_config, 'lock', log )

    active_obs = query_db.get_active_obs()
    
    if script_config['MODE'] == 'ROME':
        obs_requests = build_rome_obs(script_config,log=log)
    else:
        obs_requests = build_rea_obs(script_config,log=log)
    
    obs_requests = rm_duplicate_obs(obs_requests,active_obs,log=log)

    submit_obs_requests(script_config,obs_requests,log=log)
    
    log.info('Obs_Control: finished requesting observations')
    lock_state = log_utilities.lock( script_config, 'unlock', log )
    log_utilities.end_day_log( log )

def parse_args(script_config):
    """Function to check for commandline arguments to Obs_Control.
    Default [no arguments] will revert to REA strategy.
    Alternatively specify -rome to trigger the ROME observation strategy
    """
    
    if len(argv) > 1:
        if argv[1] == '-rome':
            script_config['MODE'] = 'ROME'
        else:
            script_config['MODE'] = 'REA'
    return script_config
    
def read_config():
    """Function to read the XML configuration file for Obs_Control"""
    
    config_file_path = path.join(path.expanduser('~'),
                                 '.robonet_site', 'obscontrol_config.xml')
    script_config = config_parser.read_config(config_file_path)
    return script_config

def rm_duplicate_obs(obs_requests, active_obs):
    """Function to compare the list of observations to be requested with the
    Django QuerySet of those that have already been submitted. 
    Any duplicated observations are removed from the list of observations
    to be submitted.     
    """
    
    for obs in obs_requests:
        for active_req in active_obs:
            if active_req.name == obs.name and \
                active_req.filters == obs.filters and \
                    active_req.req_type == obs.req_type:
                i = obs_request.index(obs)
                req = obs_request.pop(i)
    return obs_requests

def submit_obs_requests(script_config,obs_requests,log=None):
    """Function to submit a list of observations requests"""
    
    obsrecord = log_utilities.start_obs_record( script_config )
    for obs in obs_request:
        obs.build_json_request( script_config, log=log, debug=False )
        log.info('Built observation request ' + field.group_id)
        
        obs.submit_request(script_config, log=log, debug=False)
        log.info('    => Status: ' + repr(obs.submit_status) + \
                                ': ' + repr(obs.submit_response))
        obsrecord.write( field.obs_record( script_config ) )
        
        for i in range(0,len(obs.exposure_times),1):
            status = update_db_2.add_request(obs.name, (obs.cadence*60.0), \
            obs.exptime[i], obs.exposure_counts[i], timestamp=obs.ts_submit \
                time_expire=obs.ts_expire, pfrm_on = obs.pfrm, \
                onem_on=obs.onem, twom_on=obs.twom, request_type=obs.req_type, \
                which_filter=obs.filters[i], which_inst=obs.instrument, \
                grp_id=obs.group_id, track_id='', req_id='')
            log.info('    => Updated DB with status ' + repr(status))
    obsrecord.close()
    
if __name__ == '__main__':
    obs_control()