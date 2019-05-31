# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 12:47:32 2019

@author: rstreet
"""

import observation_classes
from datetime import datetime, timedelta
from rome_fields_dict import field_dict
import observing_tools
import obs_conditions_tolerances
import config_parser
from obs_control import read_config


def build_obs_request(params,log=None):
    """Function to build an observation request based on the parameters
    provided through a manual interface"""
    
    script_config = read_config()
    
    obs_requests = []
    
    obs = observation_classes.ObsRequest()
    obs.name = params['field']
    obs.ra = params['ra']
    obs.dec = params['dec']
    obs.site = params['site']
    obs.observatory= params['dome']
    obs.tel = params['tel']
    obs.instrument = params['camera']
    obs.instrument_class = '1M0-SCICAM-SINISTRO'
    obs.set_aperture_class()
    obs.airmass_limit = params['airmass_limit']
    obs.moon_sep_min = params['lunar_distance_limit']
    obs.filters = params['filters']
    obs.exposure_times = params['exp_times']
    obs.exposure_counts = params['n_exps']
    obs.cadence = params['cadence_hrs']
    obs.jitter = params['jitter_hrs']
    obs.priority = params['ipp']
    obs.user_id = script_config['user_id']
    obs.proposal_id = script_config['proposal_id']
    obs.token = script_config['token']
    obs.focus_offset = params['focus_offsets']
    obs.request_type = params['request_type']
    obs.req_origin = 'manual'
    
    obs.ttl = (params['time_expire'] - params['timestamp']).days
    
    obs.get_group_id()
    
    obs_requests.append(obs)
    
    if log!=None:
        log.info('Manual observation requested with parameters:')
        log.info(obs.summary())
        
    return obs_requests, script_config, params['simulate']

def extract_obs_params_from_post(request,oform,eform1,eform2,eform3,obs_options,
                                 log=None):
    """Function to extract and parse the parameters of an observation request,
    from the parameters provided by the webform."""
    
    params = {}
    params['field'] = oform.cleaned_data['field']
    
    params['ra'] = field_dict[params['field']][2]
    params['dec'] = field_dict[params['field']][3]
    
    params['filters'] = []
    params['exp_times'] = []
    params['n_exps'] = []
    params['focus_offsets'] = []
    
    data = request.POST.copy()
    filter_list = data.getlist('which_filter')
    exptime_list = data.getlist('exptime')
    nexp_list = data.getlist('n_exp')
    
    for i in range(0,3,1):
        if int(nexp_list[i]) > 0:
            params['filters'].append(filter_list[i])
            params['exp_times'].append(float(exptime_list[i]))
            params['n_exps'].append(int(nexp_list[i]))
            params['focus_offsets'].append(0.0)
    
    params['cadence_hrs'] = oform.cleaned_data['t_sample']
    params['jitter_hrs'] = oform.cleaned_data['jitter']
    params['timestamp'] = oform.cleaned_data['timestamp']
    params['time_expire'] = oform.cleaned_data['time_expire']
    params['airmass_limit'] = oform.cleaned_data['airmass_limit']
    params['lunar_distance_limit'] = oform.cleaned_data['lunar_distance_limit']
    params['ipp'] = oform.cleaned_data['ipp']
    
    if 'true' in str(oform.cleaned_data['simulate']).lower():
        params['simulate'] = True
    else:
        params['simulate'] = False
        
    params['user_id'] = request.user
    
    facility_data = str(request.POST['facility']).split()
    params['site'] = facility_data[0]
    params['dome'] = facility_data[1]
    params['tel'] = facility_data[2]
    params['camera'] = facility_data[3]
    
    params['request_type'] = obs_options['request_type']
    
    if log!=None:
        log.info('Observation parameters requested from online form:')
        for key, value in params.items():
            log.info(str(key)+' = '+repr(value))
        
    return params
