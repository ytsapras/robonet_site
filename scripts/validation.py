# -*- coding: utf-8 -*-
"""
Created on Tue Mar 21 15:31:32 2017

@author: rstreet
"""
from datetime import datetime

def test_type(par_list,t,params):
    status = True
    msg = 'OK'
    for p in par_list:
        if type(params[p]) is not t:
            status = False
            msg = 'Request ' + p + ' must be type ' + repr(t)
            return status, msg
    return status, msg
    
def check_obs_request(params):
    """Function to verify that the parameters of an observation request are
    valid"""
    
    status = True
    msg = 'OK'
    
    required_pars = [ 'field_name', 't_sample', 'exptime', 'timestamp', \
                'time_expire','pfrm_on','onem_on', 'twom_on', 'request_type', \
                'which_filter','which_inst', 'grp_id', 'track_id', 'req_id', \
                'n_exp']
    for p in required_pars:
        if p not in params.keys():
            status = False
            msg = 'Request missing parameter '+p
            return status, msg
    
    pars = ['field_name', 'request_type', 'which_filter','which_inst', \
                'grp_id', 'track_id', 'req_id']
    (status,msg) = test_type(pars,str,params)
    if status == False:
        return status, msg
    
    pars = ['timestamp','time_expire']
    (status,msg) = test_type(pars,datetime,params)
    if status == False:
        return status, msg
    
    
    pars = ['pfrm_on', 'onem_on', 'twom_on']
    (status,msg) = test_type(pars,bool,params)
    if status == False:
        return status, msg

    pars = ['t_sample']
    (status,msg) = test_type(pars,float,params)
    if status == False:
        return status, msg
            
    
    pars = ['exptime', 'n_exp']
    (status,msg) = test_type(pars,int,params)
    if status == False:
        return status, msg
    
    if len(params['request_type']) != 1 or params['request_type'] not in ['L','A','M']:
        status = False
        msg = 'Request type parameter must be a one-character string code, one of {L,A,M}'
        return status, msg
    
    if params['which_filter'] not in ['SDSS-g', 'SDSS-r', 'SDSS-i']:
        status = False
        msg = 'Request which_filter must be one of SDSS-g, SDSS-r, SDSS-i'
        return status, msg
    
    inst_list = ['fl16', 'fl15', 'fl12']
    if params['which_inst'] not in inst_list:
        status = False
        msg = 'Request which_filter must be one of ' + ' '.join(inst_list)
        return status, msg
  
    return status, msg