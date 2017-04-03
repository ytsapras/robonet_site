# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 18:39:09 2017

@author: rstreet
"""

import query_db
import observation_classes
import utilities
from rome_fields_dict import field_dict

def build_rea_obs(script_config,log=None):
    """Function to define the observations to be taken for the REA
    microlensing program, based on the targets extracted from the database
    as recommended by TAP"""
    
    tap_list = query_db.get_tap_list(log=log)
    obs_sequence = rea_obs_sequence()
    
    rea_obs = []
    for s in range(0,len(obs_sequence['sites']),1):
        if log != None:
                log.info('Building observation requests for site ' + \
                        obs_sequence['sites'][s] + ':')
        for target in tap_list:
            obs = observation_classes.ObsRequest()
            obs.name = str(target.field)
            rome_field=field_dict[str(target.field)]
            obs.ra = rome_field[2]
            obs.dec = rome_field[3]
            obs.site = obs_sequence['sites'][s]
            obs.observatory= obs_sequence['domes'][s]
            obs.tel = obs_sequence['tels'][s]
            obs.instrument = obs_sequence['instruments'][s]
            obs.instrument_class = '1M0-SCICAM-SINISTRO'
            obs.set_aperture_class()
            obs.filters = [ str(target.passband) ]
            obs.exposure_times = [ float(target.texp) ]
            obs.exposure_counts = [ int(target.nexp) ]
            obs.cadence = float(target.tsamp)
            obs.jitter = obs_sequence['jitter_hrs']
            obs.priority = float(target.ipp)
            obs.ttl = obs_sequence['TTL_'+str(target.priority)+'_days']
            obs.user_id = script_config['user_id']
            obs.proposal_id = script_config['proposal_id']
            obs.pswd = script_config['lco_access']
            obs.focus_offset = obs_sequence['defocus']
            obs.request_type = str(target.priority)
            obs.req_origin = 'obscontrol'
            obs.get_group_id()
            
            rea_obs.append(obs)
            
            if log != None:
                log.info(obs.summary())
        if log != None:
            log.info('\n')
        
    return rea_obs
    
def rea_obs_sequence():
    """Function to define the observation sequence to be taken for all ROME 
    survey pointings"""
    
    obs_sequence = {
                    'filters':   [ 'SDSS-i'],
                    'defocus':  [ 0.0 ],
                    'sites':        ['lsc', 'cpt', 'coj'],
                    'domes':        ['doma', 'doma', 'doma'],
                    'tels':         [ '1m0', '1m0', '1m0' ],
                    'instruments':  ['fl15', 'fl16', 'fl12'],
                    'TTL_N_days':  1.0,
                    'TTL_A_days': 0.5,
                    'TTL_L_days': 1.0,
                    'TTL_B_days': 2.0,
                    'jitter_hrs': 1.0,
                    }
    return obs_sequence
    