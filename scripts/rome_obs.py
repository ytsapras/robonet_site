# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 16:31:07 2017

@author: rstreet
"""

from . import observation_classes
from datetime import datetime, timedelta
from . import rome_fields_dict
from . import observing_tools
from . import obs_conditions_tolerances

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

    rome_obs = []

    (default_obs_sequence,tolerances) = rome_obs_sequence()

    for s in range(0,len(default_obs_sequence['sites']),1):

        site_code = default_obs_sequence['sites'][s]

        (site_obs_sequence,tolerances) = rome_obs_sequence(site_code)

        if log != None:
                log.info('Building observation requests for site '+site_code+':')

        for f in field_ids:

            field = rome_fields[f]

            (ts_submit, ts_expire) = observation_classes.get_obs_dates(site_obs_sequence['TTL_days'])

            field_obs_sequence = observing_tools.review_filters_for_observing_conditions(site_obs_sequence,field,
                                                                                    ts_submit, ts_expire,tolerances,
                                                                                    log=log)

            if len(field_obs_sequence['filters']) > 0:

                obs = observation_classes.ObsRequest()
                obs.name = f
                obs.ra = field[2]
                obs.dec = field[3]
                obs.site = field_obs_sequence['sites'][0]
                obs.observatory= field_obs_sequence['domes'][0]
                obs.tel = field_obs_sequence['tels'][0]
                obs.instrument = field_obs_sequence['instruments'][0]
                obs.instrument_class = '1M0-SCICAM-SINISTRO'
                obs.set_aperture_class()
                #obs.airmass_limit = 1.2  # ROME survey limit
                obs.airmass_limit = 2.0
                obs.moon_sep_min = field_obs_sequence['moon_sep_min']
                obs.filters = field_obs_sequence['filters']
                obs.exposure_times = field_obs_sequence['exp_times']
                obs.exposure_counts = field_obs_sequence['exp_counts']
                obs.cadence = field_obs_sequence['cadence_hrs']
                obs.jitter = field_obs_sequence['jitter_hrs']
                obs.priority = field_obs_sequence['priority']
                obs.ttl = field_obs_sequence['TTL_days']
                obs.user_id = script_config['user_id']
                obs.proposal_id = script_config['proposal_id']
                obs.token = script_config['token']
                obs.focus_offset = field_obs_sequence['defocus']
                obs.request_type = 'L'
                obs.req_origin = 'obscontrol'
                obs.get_group_id()

                rome_obs.append(obs)

                if log != None:
                    log.info(obs.summary())

            else:
                if log != None:
                    log.info('WARNING: No observations possible')

        if log != None:
            log.info('\n')

    return rome_obs

def get_rome_fields(selected_field=None):
    """Function to define the fields to be observed with the ROME strategy"""

    if selected_field == None:
        rome_fields=rome_fields_dict.field_dict
    else:
        if selected_field in rome_fields_dict.field_dict.keys():
            rome_fields={selected_field:rome_fields_dict.field_dict[selected_field]}

    return rome_fields

def rome_obs_sequence(site_code=None):
    """Function to define the observation sequence to be taken for all ROME
    survey pointings"""

    # Main survey configuration
    obs_sequence = {
                    'exp_times': [ [300.0, 300.0, 300.0],
                                  [300.0, 300.0, 300.0],
                                    [300.0, 300.0, 300.0]],
                    'exp_counts': [ [ 2, 2, 2 ],
                                    [ 2, 2, 2 ],
                                    [ 2, 2, 2 ]],
                    'filters':   [ [ 'SDSS-g', 'SDSS-r', 'SDSS-i'],
                                  [ 'SDSS-g', 'SDSS-r', 'SDSS-i'],
                                    [ 'SDSS-g', 'SDSS-r', 'SDSS-i'] ],
                    'defocus':  [ [ 0.0, 0.0, 0.0 ],
                                   [ 0.0, 0.0, 0.0],
                                    [ 0.0, 0.0, 0.0]],
                    'moon_sep_min': [ 30.0, 30.0, 30.0 ],
                    'sites':        ['lsc', 'cpt', 'coj'],
                    'domes':        ['doma', 'doma', 'doma'],
                    'tels':         [ '1m0', '1m0', '1m0' ],
                    'instruments':  ['fa15', 'fa16', 'fa12'],
                    'cadence_hrs': 7.0,
                    'jitter_hrs': 7.0,
#                    'TTL_days': 6.98,
                    'TTL_days': 3.98,
                    'priority': 1.05
                    }

    # Post survey configuration
    obs_sequence = {
                    'exp_times': [ [300.0],
                                  [300.0],
                                    [300.0]],
                    'exp_counts': [ [ 2 ],
                                    [ 2 ],
                                    [ 2 ]],
                    'filters':   [ [ 'SDSS-i'],
                                  [ 'SDSS-i'],
                                    [ 'SDSS-i'] ],
                    'defocus':  [ [ 0.0 ],
                                   [ 0.0],
                                    [ 0.0,]],
                    'moon_sep_min': [ 30.0, 30.0, 30.0 ],
                    'sites':        ['lsc', 'cpt', 'coj'],
                    'domes':        ['doma', 'doma', 'doma'],
                    'tels':         [ '1m0', '1m0', '1m0' ],
                    'instruments':  ['fa15', 'fa16', 'fa12'],
                    'cadence_hrs': 4.0,
                    'jitter_hrs': 4.0,
#                    'TTL_days': 6.98,
                    'TTL_days': 3.98,
                    'priority': 1.05
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

if __name__ == '__main__':
    script_config = {'user_id': 'tester@lco.global',
                     'proposal_id': 'TEST',
                     'token': 'XXX',
                     'selected_field': 'ROME-FIELD-01'}
    rome_field_obs = build_rome_obs(script_config,log=None)
    for field_seq in rome_field_obs:
        print(field_seq.summary())
