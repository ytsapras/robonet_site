# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 15:56:00 2017

@author: rstreet
"""
from sys import argv, exit
from os import path
import config_parser
import rome_obs
import rea_obs
import query_db
import update_db_2
import log_utilities
from exceptions import IOError
from observation_classes import get_request_desc
import validation

def obs_control():
    """Observation Control Software for the LCO Network
    
    This package is responsible for submitting the observations for the
    ROME and REA microlensing observing programs.
    """
    
    script_config = read_config()
    script_config = parse_args(script_config)
    
    log = log_utilities.start_day_log( script_config, 'obs_control' )
    log.info('Obscontrol running in ' + script_config['MODE'] + ' mode')
    
    lock_state = log_utilities.lock( script_config, 'check', log )
    if lock_state == 'clashing_lock':
        log_utilities.end_day_log( log )
        exit()
    lock_state = log_utilities.lock( script_config, 'lock', log )

    active_obs = query_db.get_active_obs(log=log)
    
    if script_config['MODE'] == 'ROME':
        obs_requests = rome_obs.build_rome_obs(script_config,log=log)
    else:
        obs_requests = rea_obs.build_rea_obs(script_config,log=log)
    
    obs_requests = rm_duplicate_obs(obs_requests,active_obs,log=log)

    submit_status = submit_obs_requests(script_config,obs_requests,log=log)
    
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
    else:
        script_config['MODE'] = 'REA'
    return script_config
    
def read_config():
    """Function to read the XML configuration file for Obs_Control"""
    
    config_file_path = path.join(path.expanduser('~'),
                                 '.robonet_site', 'obscontrol_config.xml')
    if path.isfile(config_file_path) == False:
        raise IOError('Cannot find configuration file, looking for:'+config_file_path)
    script_config = config_parser.read_config(config_file_path)
    
    return script_config

def rm_duplicate_obs(obs_request_list, active_obs,log=None):
    """Function to compare the list of observations to be requested with the
    Django QuerySet of those that have already been submitted. 
    Any duplicated observations are removed from the list of observations
    to be submitted.     
    """
    
    if log != None:
        log.info('Checking for active observations duplicated by new requests')
        
    obs_requests_final = []
    for obs in obs_request_list:
        for active_req in active_obs:
            if active_req.field.name == obs.name and \
                active_req.which_filter in obs.filters and \
                    active_req.request_type == obs.request_type:
                
                if log != None:
                    log.info(obs.group_id + ': Found existing active ' + \
                            get_request_desc(active_req.request_type) + \
                            ' observation for ' + active_req.field.name + \
                            ' with filter ' + active_req.which_filter + \
                            ', not submitting duplicate')
                
        else:
            log.info(obs.group_id + ': No existing active ' + \
                    get_request_desc(obs.request_type) + ' request for ' + obs.name + \
                    ' with filter in ' + ' '.join(obs.filters) + \
                    '; observation will be queued')
            obs_requests_final.append(obs)
                    
    if log != None:
        log.info('\n')
        
    return obs_requests_final

def submit_obs_requests(script_config,obs_requests,log=None):
    """Function to submit a list of observations requests"""
    
    if log != None: 
        log.info('Submitting observation requests')
            
    submit_status = []
    obsrecord = log_utilities.start_obs_record( script_config )
    for obs in obs_requests:
        obs.build_json_request( script_config, log=log, debug=False )
        if log != None: 
            log.info(obs.group_id + ': Built json request')
        
        stat = obs.submit_request(script_config, log=log, debug=False)
        submit_status.append(stat)
        
        if log != None: 
            log.info('    => Status: ' + repr(obs.submit_status) + \
                                ': ' + repr(obs.submit_response))
        obsrecord.write( obs.obs_record( script_config ) )

        for i in range(0,len(obs.exposure_times),1):
            params = {'field_name':obs.name, 't_sample': (obs.cadence*60.0), \
                    'exptime':int(obs.exposure_times[i]), \
                    'timestamp': obs.ts_submit, 'time_expire': obs.ts_expire, \
                    'pfrm_on': obs.pfrm,'onem_on': obs.onem, 'twom_on': obs.twom, \
                    'request_type': obs.request_type, 'which_filter':obs.filters[i],\
                    'which_inst':obs.instrument, 'grp_id':obs.group_id, \
                    'track_id':obs.track_id, 'req_id':obs.req_id, \
                    'n_exp':obs.exposure_counts[i]}
                    
            (status, msg) = validation.check_obs_request(params)
            if log != None: 
                log.info('    => Validation result: ' + repr(status) + ' ' + msg)
            
            status = update_db_2.add_request(obs.name, (obs.cadence*60.0), \
                int(obs.exposure_times[i]), timestamp=obs.ts_submit, \
                time_expire=obs.ts_expire, \
                pfrm_on=obs.pfrm, onem_on=obs.onem, twom_on=obs.twom, \
                request_type=obs.request_type, \
                which_filter=obs.filters[i],which_inst=obs.instrument, \
                grp_id=obs.group_id, track_id=obs.track_id, req_id=obs.req_id,\
                n_exp=obs.exposure_counts[i])
                
            if log != None: 
                log.info('    => Updated DB with status ' + repr(status))
    obsrecord.close()

    if log != None: 
        log.info('Finished requesting observations')
        log.info('\n')
    
    return submit_status
    
if __name__ == '__main__':
    obs_control()