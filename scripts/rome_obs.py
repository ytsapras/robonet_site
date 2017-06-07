# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 16:31:07 2017

@author: rstreet
"""

import observation_classes
from datetime import datetime, timedelta
from rome_fields_dict import field_dict

def build_rome_obs(script_config,log=None):
    """Function to define the observations to be taken during the ROME
    microlensing program, based on the field pointing definitions and
    the pre-defined survey observation sequence"""
    
    rome_fields = get_rome_fields(selected_field=script_config['selected_field'])
    field_ids = rome_fields.keys()
    field_ids.sort()
    if log != None:
        log.info('Building observation requests for '+\
                            str(len(field_ids))+' fields:')
        log.info(' '.join(field_ids))
    obs_sequence = rome_obs_sequence()
    rome_obs = []
    
    for s in range(0,len(obs_sequence['sites']),1):
        if log != None:
                log.info('Building observation requests for site ' + \
                        obs_sequence['sites'][s] + ':')
        for f in field_ids:
            field = rome_fields[f]
            obs = observation_classes.ObsRequest()
            obs.name = f
            obs.ra = field[2]
            obs.dec = field[3]
            obs.site = obs_sequence['sites'][s]
            obs.observatory= obs_sequence['domes'][s]
            obs.tel = obs_sequence['tels'][s]
            obs.instrument = obs_sequence['instruments'][s]
            obs.instrument_class = '1M0-SCICAM-SINISTRO'
            obs.set_aperture_class()
            obs.filters = obs_sequence['filters'][s]
            obs.exposure_times = obs_sequence['exp_times'][s]
            obs.exposure_counts = obs_sequence['exp_counts'][s]
            obs.cadence = obs_sequence['cadence_hrs']
            obs.jitter = obs_sequence['jitter_hrs']
            obs.priority = 1.0
            obs.ttl = obs_sequence['TTL_days']
            obs.user_id = script_config['user_id']
            obs.proposal_id = script_config['proposal_id']
            obs.token = script_config['token']
            obs.focus_offset = obs_sequence['defocus'][s]
            obs.request_type = 'L'
            obs.req_origin = 'obscontrol'
            obs.get_group_id()
            
            rome_obs.append(obs)
            
            if log != None:
                log.info(obs.summary())
        if log != None:
            log.info('\n')
            
    return rome_obs
    
def get_rome_fields(selected_field=None):
    """Function to define the fields to be observed with the ROME strategy"""
    
    if selected_field == None:
        rome_fields=field_dict
    else:
        if selected_field in field_dict.keys():
            rome_fields={selected_field:field_dict[selected_field]}
    
    return rome_fields

def rome_obs_sequence():
    """Function to define the observation sequence to be taken for all ROME 
    survey pointings"""
    
    obs_sequence = {
                    'exp_times': [ [300.0],
                                  [300.0, 300.0, 300.0],
                                    [300.0, 300.0, 300.0]],
                    'exp_counts': [ [ 1 ],
                                    [ 1, 1, 1 ],
                                    [ 1, 1, 1 ]],
                    'filters':   [ [ 'SDSS-i'],
                                  [ 'SDSS-g', 'SDSS-r', 'SDSS-i'],
                                    [ 'SDSS-g', 'SDSS-r', 'SDSS-i'] ],
                    'defocus':  [ [ 0.0 ],
                                 [ 0.0, 0.0, 0.0],
                                    [ 0.0, 0.0, 0.0]],
                    'sites':        ['lsc', 'cpt', 'coj'],
                    'domes':        ['domb', 'doma', 'doma'],
                    'tels':         [ '1m0', '1m0', '1m0' ],
                    'instruments':  ['fl03', 'fl16', 'fl12'],
                    'cadence_hrs': 7.0,
                    'jitter_hrs': 1.0,
                    'TTL_days': 7.0,
                    }
    return obs_sequence

if __name__ == '__main__':
    script_config = {'user_id': 'tester@lco.global', 
                     'proposal_id': 'TEST',
                     'token': 'XXX',
                     'selected_field': 'ROME-FIELD-01'}
    rome_field_obs = build_rome_obs(script_config,log=None)
    for field_seq in rome_field_obs:
        print field_seq.summary()
    