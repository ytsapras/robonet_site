# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 18:39:09 2017

@author: rstreet
"""

import query_db
import observation_classes
import utilities
from rome_fields_dict import field_dict
import observing_tools
import copy
import obs_conditions_tolerances
        
def build_rea_obs(script_config,log=None,tap_list=None):
    """Function to define the observations to be taken for the REA
    microlensing program, based on the targets extracted from the database
    as recommended by TAP"""
    
    if tap_list == None:
        
        tap_list = query_db.get_tap_list(log=log)
        
    (default_obs_sequence, tolerances) = rea_obs_sequence()
    
    rea_obs = []

    for s in range(0,len(default_obs_sequence['sites']),1):

        site_code = default_obs_sequence['sites'][s]
        
        (site_obs_sequence, tolerances) = rea_obs_sequence(site_code)
            
        if log != None:
                log.info('Building observation requests for site '+site_code+ ':')

        for target in tap_list:
            
            rome_field=field_dict[str(target.field)]
            
            (site_obs_sequence, tolerances) = rea_obs_sequence(site_code)
            
            site_obs_sequence['filters'] = [ str(target.passband) ]
            
            (ts_submit, ts_expire) = observation_classes.get_obs_dates(site_obs_sequence['TTL_'+str(target.priority)+'_days'])

            if log!=None:
                log.info('Site observing sequence: '+repr(site_obs_sequence))
            
            target_obs_sequence = observing_tools.review_filters_for_observing_conditions(site_obs_sequence,rome_field,
                                                                                   ts_submit, ts_expire, tolerances,
                                                                                   log=log)
            
            if log!=None:
                log.info('Target observing sequence: '+repr(target_obs_sequence))
                
            if len(target_obs_sequence['filters']) > 0:
                
                obs = observation_classes.ObsRequest()
                
                obs.name = str(target.field)               
                obs.ra = rome_field[2]
                obs.dec = rome_field[3]
                obs.site = target_obs_sequence['sites'][0]
                obs.observatory= target_obs_sequence['domes'][0]
                obs.tel = target_obs_sequence['tels'][0]
                obs.instrument = target_obs_sequence['instruments'][0]
                obs.instrument_class = '1M0-SCICAM-SINISTRO'
                obs.set_aperture_class()
                obs.moon_sep_min = target_obs_sequence['moon_sep_min']
                obs.filters = [ str(target.passband) ]
                obs.exposure_times = [ float(target.texp) ]
                obs.exposure_counts = [ int(target.nexp) ]
                obs.cadence = float(target.tsamp)
                obs.jitter = target_obs_sequence['jitter_hrs']
                obs.priority = float(target.ipp)
                obs.ttl = target_obs_sequence['TTL_'+str(target.priority)+'_days']
                obs.user_id = script_config['user_id']
                obs.proposal_id = script_config['proposal_id']
                obs.token = script_config['token']
                obs.focus_offset = [ 0.0 ]
                #obs.request_type = str(target.priority)
                obs.request_type = 'M'
                obs.req_origin = 'obscontrol'
                obs.get_group_id()
                
                rea_obs.append(obs)
                
                if log != None:
                    log.info(obs.summary())
                
            else:
                
                if log != None:
                    log.info('WARNING: No observations possible')
                    
        if log != None:
            log.info('\n')
        
    return rea_obs
    
def rea_obs_sequence(site_code=None):
    """Function to define the observation sequence to be taken for all ROME 
    survey pointings"""
    
    obs_sequence = {
                    'filters':   [ [ 'SDSS-i'],[ 'SDSS-i'],[ 'SDSS-i'] ],
                    'defocus':  [ 0.0, 0.0, 0.0 ],
                    'sites':        ['lsc', 'cpt', 'coj'],
                    'domes':        ['doma', 'domc', 'doma'],
                    'tels':         [ '1m0', '1m0', '1m0' ],
                    'instruments':  ['fl15', 'fl06', 'fl12'],
                    'moon_sep_min': [ 30.0, 30.0, 30.0 ],
                    'TTL_N_days':  1.0,
                    'TTL_A_days': 0.5,
                    'TTL_L_days': 1.0,
                    'TTL_B_days': 2.0,
                    'jitter_hrs': 1.0,
                    }

    tolerances = obs_conditions_tolerances.get_obs_tolerances()
    
    if site_code != None:
        
        s = obs_sequence['sites'].index(site_code)
        
        site_obs_sequence = {}
        
        for key, value in obs_sequence.items():
            
            if type(value) == type([]):
                
                if type(value[s]) == type([]):
                    
                    site_obs_sequence[key] = value[s]
                    
                else:
                
                    site_obs_sequence[key] = [ value[s] ]
                    
            else:
                
                site_obs_sequence[key] = value
        
        return site_obs_sequence, tolerances
        
    else:
        
        return obs_sequence, tolerances

def get_rea_tsamp(priority):
    """Function to return the sampling rate in decimal hours defined by 
    the REA strategy, for a given priority.
    """
    
    tsamp_strategy = {  'A': 0.25,           # REA High
                        'L': 1.0,            # REA Low
                        'B': 1.0,            # REA Post-High
                        'N': 0.0,            # None
                    }
    
    if priority in tsamp_strategy.keys():
        
        return tsamp_strategy[priority]
        
    else:
        
        return 0.0

def build_rea_hi_request(script_config, field, exptime, t_sample, log=None):
    """Function to compose a triggered observation in REA-HI mode for a 
    specific field"""
    
    (default_obs_sequence, tolerances) = rea_obs_sequence()
    
    if log != None:
        log.info(' -> Received default_obs_sequence')
        
    rea_obs = []

    for s in range(0,len(default_obs_sequence['sites']),1):
        
        site_code = default_obs_sequence['sites'][s]
        
        if log != None:
            log.info(' -> Preparing observations for site '+site_code)
            
        (site_obs_sequence, tolerances) = rea_obs_sequence(site_code)

        site_obs_sequence['filters'] = [ 'SDSS-i' ]
            
        (ts_submit, ts_expire) = observation_classes.get_obs_dates(1.0)
        
        rome_field=field_dict[field.name]
        
        target_obs_sequence = observing_tools.review_filters_for_observing_conditions(site_obs_sequence,rome_field,
                                                                               ts_submit, ts_expire, tolerances,
                                                                               log=log)
        
        if log != None:
            log.info(' -> Derived target_obs_sequence')
        
        obs = observation_classes.ObsRequest()
        
        obs.name = str(field.name)               
        obs.ra = field.field_ra
        obs.dec = field.field_dec
        obs.site = target_obs_sequence['sites'][0]
        obs.observatory= target_obs_sequence['domes'][0]
        obs.tel = target_obs_sequence['tels'][0]
        obs.instrument = target_obs_sequence['instruments'][0]
        obs.instrument_class = '1M0-SCICAM-SINISTRO'
        obs.set_aperture_class()
        obs.moon_sep_min = target_obs_sequence['moon_sep_min']
        obs.filters = [ 'SDSS-i' ]
        obs.exposure_times = [ exptime ]
        obs.exposure_counts = [ 1 ]
        obs.cadence = float(t_sample)
        obs.jitter = target_obs_sequence['jitter_hrs']
        obs.priority = 1.1
        obs.ttl = 1.0
        obs.user_id = script_config['user_id']
        obs.proposal_id = script_config['proposal_id']
        obs.token = script_config['token']
        obs.focus_offset = [ 0.0 ]
        #obs.request_type = str(target.priority)
        obs.request_type = 'A'
        obs.req_origin = 'www'
        obs.get_group_id()
        
        rea_obs.append(obs)
        
        if log != None:
            log.info(' -> Completed obs request for site '+site_code)
            
    return rea_obs