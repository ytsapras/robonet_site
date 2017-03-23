# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 16:31:07 2017

@author: rstreet
"""

import observation_classes
from datetime import datetime, timedelta

def build_rome_obs(script_config,log=None):
    """Function to define the observations to be taken during the ROME
    microlensing program, based on the field pointing definitions and
    the pre-defined survey observation sequence"""
    
    rome_fields = get_rome_fields(testing=True)
    field_ids = rome_fields.keys()
    field_ids.sort()
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
            obs.instrument_class = 'sinistro'
            obs.set_aperture_class()
            obs.filters = obs_sequence['filters']
            obs.exposure_times = obs_sequence['exp_times']
            obs.exposure_counts = obs_sequence['exp_counts']
            obs.cadence = obs_sequence['cadence_hrs']
            obs.priority = 1.0
            obs.ttl = obs_sequence['TTL_days']
            obs.user_id = script_config['user_id']
            obs.proposal_id = script_config['proposal_id']
            obs.focus_offset = obs_sequence['defocus']
            obs.request_type = 'L'
            obs.req_origin = 'obscontrol'
            obs.get_group_id()
            
            rome_obs.append(obs)
            
            if log != None:
                log.info(obs.summary())
        if log != None:
            log.info('\n')
            
    return rome_obs
    
def get_rome_fields(testing=False):
    """Function to define the fields to be observed with the ROME strategy"""
    
    rome_fields={'ROME-FIELD-01':[ 267.835895375 , -30.0608178195 , '17:51:20.6149','-30:03:38.9442' ],
            'ROME-FIELD-02':[ 269.636745458 , -27.9782661111 , '17:58:32.8189','-27:58:41.758' ],
            'ROME-FIELD-03':[ 268.000049542 , -28.8195573333 , '17:52:00.0119','-28:49:10.4064' ],
            'ROME-FIELD-04':[ 268.180171708 , -29.27851275 , '17:52:43.2412','-29:16:42.6459' ],
            'ROME-FIELD-05':[ 268.35435 , -30.2578356389 , '17:53:25.044','-30:15:28.2083' ],
            'ROME-FIELD-06':[ 268.356124833 , -29.7729819283 , '17:53:25.47','-29:46:22.7349' ],
            'ROME-FIELD-07':[ 268.529571333 , -28.6937071111 , '17:54:07.0971','-28:41:37.3456' ],
            'ROME-FIELD-08':[ 268.709737083 , -29.1867251944 , '17:54:50.3369','-29:11:12.2107' ],
            'ROME-FIELD-09':[ 268.881108542 , -29.7704673333 , '17:55:31.4661','-29:46:13.6824' ],
            'ROME-FIELD-10':[ 269.048498333 , -28.6440675 , '17:56:11.6396','-28:38:38.643' ],
            'ROME-FIELD-11':[ 269.23883225 , -29.2716684211 , '17:56:57.3197','-29:16:18.0063' ],
            'ROME-FIELD-12':[ 269.39478875 , -30.0992361667 , '17:57:34.7493','-30:05:57.2502' ],
            'ROME-FIELD-13':[ 269.563719375 , -28.4422328996 , '17:58:15.2927','-28:26:32.0384' ],
            'ROME-FIELD-14':[ 269.758843 , -29.1796030365 , '17:59:02.1223','-29:10:46.5709' ],
            'ROME-FIELD-15':[ 269.78359875 , -29.63940425 , '17:59:08.0637','-29:38:21.8553' ],
            'ROME-FIELD-16':[ 270.074981708 , -28.5375585833 , '18:00:17.9956','-28:32:15.2109' ],
            'ROME-FIELD-17':[ 270.81 , -28.0978333333 , '18:03:14.4','-28:05:52.2' ],
            'ROME-FIELD-18':[ 270.290886667 , -27.9986032778 , '18:01:09.8128','-27:59:54.9718' ],
            'ROME-FIELD-19':[ 270.312763708 , -29.0084241944 , '18:01:15.0633','-29:00:30.3271' ],
            'ROME-FIELD-20':[ 270.83674125 , -28.8431573889 , '18:03:20.8179','-28:50:35.3666' ]}
    
    if testing == True:
        rome_fields={'ROME-FIELD-01':[ 267.835895375 , -30.0608178195 , '17:51:20.6149','-30:03:38.9442' ]}
    
    return rome_fields

def rome_obs_sequence():
    """Function to define the observation sequence to be taken for all ROME 
    survey pointings"""
    
    obs_sequence = {
                    'exp_times': [ 300.0, 300.0, 300.0],
                    'exp_counts': [ 1, 1, 1 ],
                    'filters':   [ 'SDSS-g', 'SDSS-r', 'SDSS-i'],
                    'defocus':  [ 0.0, 0.0, 0.0],
                    'sites':        ['lsc', 'cpt', 'coj'],
                    'domes':        ['doma', 'doma', 'doma'],
                    'tels':         [ '1m0', '1m0', '1m0' ],
                    'instruments':  ['fl15', 'fl16', 'fl12'],
                    'cadence_hrs': 24.0,
                    'TTL_days': 7.0,
                    }
    return obs_sequence
    