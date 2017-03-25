# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 18:39:09 2017

@author: rstreet
"""

import query_db
import observation_classes

def build_rea_obs(script_config,log=None):
    """Function to define the observations to be taken for the REA
    microlensing program, based on the targets extracted from the database
    as recommended by TAP"""
    
    qs = query_db.get_rea_targets(log=log)
    obs_sequence = rea_obs_sequence()
    
    rea_obs = []
    for s in range(0,len(obs_sequence['sites']),1):
        if log != None:
                log.info('Building observation requests for site ' + \
                        obs_sequence['sites'][s] + ':')
        for q in qs:
            obs = observation_classes.ObsRequest()
            obs.name = q.event.field
            obs.ra = q.event.ev_ra
            obs.dec = q.event.ev_dec
            obs.site = obs_sequence['sites'][s]
            obs.observatory= obs_sequence['domes'][s]
            obs.tel = obs_sequence['tels'][s]
            obs.instrument = obs_sequence['instruments'][s]
            obs.instrument_class = 'sinistro'
            obs.set_aperture_class()
            obs.filters = obs_sequence['filters']
            obs.exposure_times = [ q.texp ]
            obs.exposure_counts = [ q.nexp ]
            obs.cadence = q.tsamp
            obs.priority = q.ipp
            obs.ttl = obs_sequence['TTL_days']
            obs.user_id = script_config['user_id']
            obs.proposal_id = script_config['proposal_id']
            obs.focus_offset = obs_sequence['defocus']
            obs.request_type = q.priority
            obs.req_origin = 'obscontrol'
            obs.get_group_id()
            
            rome_obs.append(obs)
            
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
                    'TTL_days':  24.0
                    }
    return obs_sequence
    