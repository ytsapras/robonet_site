# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 15:56:00 2017

@author: rstreet
"""
from sys import argv, exit
from sys import path as systempath
from os import path, getcwd
import config_parser
import rome_obs
import rea_obs
import query_db
import update_db_2
import log_utilities
from exceptions import IOError
from observation_classes import get_request_desc
import validation
import socket
import get_errors

def obs_control():
    """Observation Control Software for the LCO Network
    
    This package is responsible for submitting the observations for the
    ROME and REA microlensing observing programs.
    """

    version = 'obs_control_0.93'    
    
    script_config = read_config()
    script_config = parse_args(script_config)
    
    log = log_utilities.start_day_log( script_config, 'obs_control', version=version )
    log.info('Obscontrol running in ' + script_config['MODE'] + ' mode')
    if str(script_config['simulate']).lower() == 'true':
        log.info('*** SIMULATION MODE ***')
    
    set_lock( script_config, log )

    update_db_2.expire_old_obs(log=log)

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
    1st argument= -rome will trigger the ROME observation strategy
    
    """
    
    script_config['selected_field'] = None
    script_config['MODE'] = 'REA'
    if len(argv) > 1:
        if '-rome' in argv:
            script_config['MODE'] = 'ROME'
        for a in argv:
            if '-field=' in a:
                script_config['selected_field'] = a.split('=')[-1]
    
    return script_config
    
def read_config():
    """Function to read the XML configuration file for Obs_Control"""
    
    host_name = socket.gethostname()
    if 'rachel' in str(host_name).lower() or 'tuc.noao.edu' in str(host_name).lower():
        config_file_path = path.join('/Users/rstreet/.robonet_site/obscontrol_config.xml')
    else:
        config_file_path = '/var/www/robonetsite/configs/obscontrol_config.xml'
    if path.isfile(config_file_path) == False:
        raise IOError('Cannot find configuration file, looking for:'+config_file_path)
    script_config = config_parser.read_config(config_file_path)
    
    return script_config

def set_lock(script_config,log):
    """Function to check for the existance of a lockfile, issue an error 
    warning if one is found and set the lock if not"""
    
    code = 'obs_control_'+str(script_config['MODE']).lower()
    lock_state = log_utilities.lock( script_config, 'check', log )
    if lock_state == 'clashing_lock':
        get_errors.update_err(code, 'WARNING: persistent lockfile')
        log_utilities.end_day_log( log )
        exit()
    else:
        get_errors.update_err(code, 'Status OK')
    lock_state = log_utilities.lock( script_config, 'lock', log )

def rm_duplicate_obs(obs_request_list, active_obs,log=None,debug=False):
    """Function to compare the list of observations to be requested with the
    Django QuerySet of those that have already been submitted. 
    Any duplicated observations are removed from the list of observations
    to be submitted.     
    """
    
    if log != None:
        log.info('Checking for active observations duplicated by new requests')
        
    obs_requests_final = []
    for obs in obs_request_list:
        if debug==True: 
            print obs.name, obs.filters, obs.request_type
        if len(active_obs) > 0:
            matching_request = False
            for active_req in active_obs:
                if debug==True: 
                    print active_req.field.name, active_req.which_filter,\
                        active_req.request_type
                if active_req.field.name == obs.name and \
                    active_req.which_filter in obs.filters and \
                    active_req.request_type == obs.request_type and\
                    active_req.which_inst == obs.instrument:
                    matching_request = True
                    
                    if log != None:
                        log.info(obs.group_id + ': Found existing active ' + \
                                get_request_desc(active_req.request_type) + \
                                ' observation for ' + active_req.field.name + \
                                ' with instrument ' + active_req.which_inst + \
                                ' with filter ' + active_req.which_filter + 
                                ', not submitting duplicate')
            if matching_request == False:
                obs_requests_final.append(obs)
                if log != None:
                    log.info(obs.group_id + ': No existing active ' + \
                        get_request_desc(obs.request_type) + ' request for ' + obs.name + \
                        ' with instrument ' + obs.instrument + \
                        ' with filter in ' + ' '.join(obs.filters) +  \
                        '; observation will be queued')
        else:
            if log != None:
                log.info(obs.group_id + ': No existing active ' + \
                    get_request_desc(obs.request_type) + ' request for ' + obs.name + \
                    ' with instrument ' + obs.instrument + \
                    ' with filter in ' + ' '.join(obs.filters) + \
                    '; observation will be queued')
            obs_requests_final.append(obs)

    if log != None:
        log.info('Finalized list of '+str(len(obs_requests_final))+\
                    ' observation requests to be submitted:')
        for obs in obs_requests_final:
            log.info(obs.summary())
        log.info('\n')
        
    return obs_requests_final

def submit_obs_requests(script_config,obs_requests,log=None):
    """Function to submit a list of observations requests"""
    
    if log != None: 
        log.info('Submitting observation requests')
            
    submit_status = []
    obsrecord = log_utilities.start_obs_record( script_config )
    
    if log != None: 
        log.info('Starting loop over observations:')
            
    for obs in obs_requests:
        if log != None:
            log.info('Building '+obs.group_id)
            
        ur = obs.build_cadence_request( log=log, debug=True )
        
        if log != None: 
            log.info(obs.group_id + ': Built json request')
        
        stat = obs.submit_request(ur, script_config, log=log)
        submit_status.append(stat)
        
        if log != None: 
            log.info('    => Status: ' + repr(obs.submit_status) + \
                                ': ' + repr(obs.submit_response))
        obsrecord.write( obs.obs_record( script_config ) )
        
        if str(script_config['simulate']).lower() == 'false':
            for i in range(0,len(obs.exposure_times),1):
                params = {'field_name':obs.name, 't_sample': (obs.cadence*60.0), \
                        'exptime':int(obs.exposure_times[i]), \
                        'timestamp': obs.ts_submit, 'time_expire': obs.ts_expire, \
                        'pfrm_on': obs.pfrm,'onem_on': obs.onem, 'twom_on': obs.twom, \
                        'request_type': obs.request_type, 'which_filter':obs.filters[i],\
                        'which_site':obs.site,\
                        'which_inst':obs.instrument, 'grp_id':obs.group_id, \
                        'track_id':obs.track_id, 'req_id':obs.req_id, \
                        'n_exp':obs.exposure_counts[i]}
                
                if obs.submit_status == 'add_OK':
                    req_status = 'AC'
                else:
                    req_status = 'CN'
                    
                (status, msg) = validation.check_obs_request(params)
                if log != None: 
                    log.info('    => Validation result: ' + repr(status) + ' ' + msg)
                
                
                status = update_db_2.add_request(obs.name, (obs.cadence*60.0), \
                    int(obs.exposure_times[i]), timestamp=obs.ts_submit, \
                    time_expire=obs.ts_expire, \
                    pfrm_on=obs.pfrm, onem_on=obs.onem, twom_on=obs.twom, \
                    request_type=obs.request_type, which_site=obs.site,\
                    which_filter=obs.filters[i],which_inst=obs.instrument, \
                    grp_id=obs.group_id, track_id=obs.track_id, req_id=obs.req_id,\
                    n_exp=obs.exposure_counts[i],\
                    request_status=req_status)
                    
                if log != None: 
                    log.info('    => Updated DB with status ' + repr(status))
    obsrecord.close()

    if log != None: 
        log.info('Finished requesting observations')
        log.info('\n')
    
    return submit_status
    
if __name__ == '__main__':
    obs_control()