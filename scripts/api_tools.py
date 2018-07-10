# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 13:47:12 2017

@author: rstreet
"""

import httplib
import urllib
import json
import requests
from os import path
from datetime import datetime

################################################################################
def submit_obs_request_record(config,params):
    """Function to submit a record of a new observation to the database 
    using the API record_obs_request endpoint
    Required parameters:
        config    dict    script configuration parameters
        params    dict    observation request parameters, including
                    field       str
                    t_sample    float
                    exptime     int
                    timestamp   string
                    time_expire string
    """
    
    end_point = 'record_obs_request'
    
    message = talk_to_db(params,end_point,\
                            config['db_user_id'],config['db_pswd'],
                            testing=True)

################################################################################
def submit_sub_obs_request_record(config,params,testing=False,verbose=False):
    """Function to submit a record of a new observation to the database 
    using the API record_obs_request endpoint
    Required parameters:
        config    dict    script configuration parameters
        params    dict    observation request parameters, including
                    sr_id,
                    grp_id,
                    track_id,
                    window_start,
                    window_end, 
                    status, 
                    time_executed
    """
    
    end_point = 'record_sub_obs_request'
    
    key_order = [ 'sr_id', 'grp_id', 'track_id', 'window_start', 'window_end', 
                 'status' ]
    if 'time_executed' in params.keys():
        key_order.append('time_executed')
    
    query = build_url_query(end_point,key_order,params)
    
    message = talk_to_db(query,config['db_token'],
                            testing=testing,verbose=verbose)
                            
    return message
    
################################################################################
def submit_event_record(config,params):
    """Function to submit a record of a new event to the database 
    using the API add_event endpoint
    Required parameters:
        config    dict    script configuration parameters
        params    dict    event request parameters, including
                    field_name       str
                    operator_name    str
                    ev_ra            str
		    ev_dec           str
		    status           str
                    anomaly rank     float
                    year             str
    """
    
    end_point = 'add_event'
    
    response = talk_to_db(params,end_point,\
                            config['db_user_id'],config['db_pswd'],
                            testing=True)

################################################################################
def submit_eventname_record(config,params):
    """Function to submit a record of a new event name to the database 
    using the API add_eventname endpoint
    Required parameters:
        config    dict    script configuration parameters
        params    dict    eventname request parameters, including
                    event         str
                    operator      str
                    name          str
    """
    
    end_point = 'add_eventname'
    
    response = talk_to_db(params,end_point,\
                            config['db_user_id'],config['db_pswd'],
                            testing=True)


################################################################################
def submit_data_file_record(config,params,testing=False):
    """Function to submit a record of a new observation to the database 
    using the API record_obs_request endpoint
    Required parameters:
        config    dict    script configuration parameters
        params    dict    observation request parameters, including
                    event_name  str   Name of the event
                    datafile    str   Path to the data
                    tel         str   Name of the telescope
                    filt        str   Name of the filter used
                    last_mag    float Last measured magnitude
                    last_upd    datetime Last updated time stamp
                    last_obs    datetime of last observation
                    baseline    float Event's baseline magnitude
                    g           float ARTEMiS' fitted blend parameter
                    ndata       int   Number of datapoints
    """
    
    end_point = 'record_data_file'
    
    message = talk_to_db(params,end_point,\
                            config['db_user_id'],config['db_pswd'],
                            testing=testing)
    return message
    
################################################################################
def submit_operator_record(config,params):
    """Function to submit a record of a new operator to the database 
    using the API add_operator endpoint
    Required parameters:
        config    dict    script configuration parameters
        params    dict    operator parameters, including
                    name       str
    """
    
    end_point = 'add_operator'
    
    response = talk_to_db(params,end_point,\
                            config['db_user_id'],config['db_pswd'],
                            testing=True)

################################################################################
def submit_telescope_record(config,params):
    """Function to submit a record of a new telescope to the database 
    using the API add_telescope endpoint
    Required parameters:
        config    dict    script configuration parameters
        params    dict    telescope parameters, including
                    operator 		str
                    telescope_name 	str
                    aperture 		float
                    latitude 		float
                    longitude 		float
                    altitude 		float
                    site 		str
    """
    
    end_point = 'add_telescope'
    
    response = talk_to_db(params,end_point,\
                            config['db_user_id'],config['db_pswd'],
                            testing=True)

################################################################################
def submit_singlemodel_record(config,params):
    """Function to submit a record of a new single lens model to the database 
    using the API add_singlemodel endpoint
    Required parameters:
        config    dict    script configuration parameters
        params    dict    singlemodel parameters, including
                    event 	str
                    Tmax 	float
                    e_Tmax 	float
                    tau 	float
                    e_tau 	float
                    umin 	float
                    e_umin 	float
		    rho		float
		    e_rho	float
		    pi_e_n	float
		    e_pi_e_n	float
		    pi_e_e	float
		    e_pi_e_e	float
		    modeler	str
		    last_updated str
		    tap_omega	float
		    chi_sq	float
    """
    
    end_point = 'add_singlemodel'
    
    response = talk_to_db(params,end_point,\
                            config['db_user_id'],config['db_pswd'],
                            testing=True)

################################################################################
def submit_binarymodel_record(config,params):
    """Function to submit a record of a new binary lens model to the database 
    using the API add_binarymodel endpoint
    Required parameters:
        config    dict    script configuration parameters
        params    dict    binarymodel parameters, including
                    event 	str
                    Tmax 	float
                    e_Tmax 	float
                    tau 	float
                    e_tau 	float
                    umin 	float
                    e_umin 	float
		    mass_ratio 	float
		    e_mass_ratio float
		    separation 	float
		    e_separation float
		    angle_a 	float
		    e_angle_a	float
		    dsdt 	float
		    e_dsdt 	float
		    dadt 	float
		    e_dadt 	float
		    rho		float
		    e_rho	float
		    pi_e_n	float
		    e_pi_e_n	float
		    pi_e_e	float
		    e_pi_e_e	float
		    modeler	str
		    last_updated str
		    tap_omega	float
		    chi_sq	float
    """
    
    end_point = 'add_binarymodel'
    
    response = talk_to_db(params,end_point,\
                            config['db_user_id'],config['db_pswd'],
                            testing=True)

################################################################################
def submit_eventreduction_record(config,params):
    """Function to submit a record of a new event reduction to the database 
    using the API add_eventreduction endpoint
    Required parameters:
        config    dict    script configuration parameters
        params    dict    eventreduction parameters, including
                    event	    str
                    lc_file         str
                    timestamp	    str
                    ref_image	    str
                    target_found    bool
                    ron 	    float
                    gain	    float
		    oscanx1	    int
		    oscanx2	    int
		    oscany1	    int
		    oscany2	    int
		    imagex1	    int
		    imagex2	    int
		    imagey1	    int
		    imagey2	    int
		    minval	    int
		    maxval	    int
		    growsatx	    int
		    growsaty	    int
		    coeff2	    str
		    coeff3	    str
		    sigclip	    float
		    sigfrac	    float
		    flim	    float
		    niter	    int
		    use_reflist     int
		    max_nimages     int
		    max_sky	    float
		    min_ell	    float
		    trans_type      str
		    trans_auto      int
		    replace_cr      int
		    min_scale	    float
		    max_scale	    float
		    fov 	    float
		    star_space      int
		    init_mthresh    float
		    smooth_pro      int
		    smooth_fwhm     float
		    var_deg	    int
		    det_thresh      float
		    psf_thresh      float
		    psf_size	    float
		    psf_comp_dist   float
		    psf_comp_flux   float
		    psf_corr_thresh float
		    ker_rad	    float
		    lres_ker_rad    float
		    subframes_x     int
		    subframes_y     int
		    grow	    float
		    ps_var	    int
		    back_var	    int
		    diffpro         int
    """
    
    end_point = 'add_eventreduction'
    
    response = talk_to_db(params,end_point,\
                            config['db_user_id'],config['db_pswd'],
                            testing=True)

################################################################################
def submit_tap_record(config,params):
    """Function to submit a record of a new TAP to the database 
    using the API add_tap endpoint
    Required parameters:
        config    dict    script configuration parameters
        params    dict    tap parameters, including
        event     		str
        possible_priority	str
        timestamp		str
        priority		str
        tsamp			float
        texp			int
        nexp			int
        telclass		str
        imag			float
        omega			float
        err_omega		float
        peak_omega		float
        blended			bool
        visibility		float
        cost1m			float
        passband		str
        ipp			float
    """
    
    end_point = 'add_tap'
    
    response = talk_to_db(params,end_point,\
                            config['db_user_id'],config['db_pswd'],
                            testing=True)

################################################################################
def submit_taplima_record(config,params):
    """Function to submit a record of a new TAPLima to the database 
    using the API add_taplima endpoint
    Required parameters:
        config    dict    script configuration parameters
        params    dict    tap parameters, including
        event     		str
        possible_priority	str
        timestamp		str
        priority		str
        tsamp			float
        texp			int
        nexp			int
        telclass		str
        imag			float
        omega			float
        err_omega		float
        peak_omega		float
        blended			bool
        visibility		float
        cost1m			float
        passband		str
        ipp			float
    """
    
    end_point = 'add_taplima'
    
    response = talk_to_db(params,end_point,\
                            config['db_user_id'],config['db_pswd'],
                            testing=True)


################################################################################
def submit_datafile_record(config,params):
    """Function to submit a record of a new ARTEMiS DataFile to the database 
    using the API add_datafile endpoint
    Required parameters:
        config    dict    script configuration parameters
        params    dict    datafile parameters, including
        event     		str
	datafile		str
	last_upd		str
	last_hjd		float
	last_mag		float
	tel			str
	ndata			int
	inst			str		
	filt			str
	baseline		float
	g			float
     """
    
    end_point = 'add_datafile'
    
    response = talk_to_db(params,end_point,\
                            config['db_user_id'],config['db_pswd'],
                            testing=True)

################################################################################
def submit_image_record(config,params,testing=False,verbose=False):
    """Function to submit a record of a new image to the database 
    using the API add_image endpoint
    Required parameters:
        config    dict    script configuration parameters
        params    dict    image parameters, including
	field_name     	str
	image_name	str
	date_obs  	str
	timestamp 	str
	tel       	str
	inst      	str
	filt      	str
	grp_id    	str
	track_id  	str
	req_id    	str
	airmass   	float
	avg_fwhm  	float
	avg_sky   	float
	avg_sigsky	float
	moon_sep  	float
	moon_phase	float
	moon_up   	bool
	elongation	float
	nstars    	int
	ztemp     	float
	shift_x   	int
	shift_y   	int
	quality   	str
     """

    end_point = 'record_image'
    
    key_order = [ 
                'field_name', 'image_name', 'date_obs', 'timestamp', 
                'tel', 'inst', 'filt', 'grp_id', 'track_id', 'req_id',
                'airmass', 'avg_fwhm', 'avg_sky', 'avg_sigsky',
                'moon_sep', 'moon_phase', 'moon_up', 'elongation', 'nstars',
                'ztemp', 'shift_x', 'shift_y', 'quality'
                  ]
    
    query = build_url_query(end_point,key_order,params)
    
    message = talk_to_db(query,config['db_token'],
                            testing=testing,verbose=verbose)
    
    return message
    
################################################################################
def get_obs_list(config,params,testing=False,verbose=False):
    """Function to retrieve from the database API endpoint a list of 
    observations matching the parameters given.
    
    Inputs:
        :param dict config: script configuration parameters
        :param dict params: observation parameters, where key, values match
                            the keywords and data types in the ObsRequest.
    """
    
    end_point = 'query_obs_by_date'
    
    key_order = [ 'timestamp', 'time_expire', 'request_status' ]

    status_options = [ 'AC', 'EX', 'CN' ]    
    
    if params['request_status'] != 'ALL':
        
        status_options = [ params['request_status'] ]
    
    obs_list = []
    
    for status in status_options:
        
        qparams = {}
        
        for key in key_order:
            
            qparams[key] = params[key]
        
        qparams['request_status'] = status
        
        query = build_url_query(end_point,key_order,qparams)
        
        (message, response) = ask_db(query,config['db_token'],
                                testing=testing,verbose=verbose)
        
        if 'Got observations list' in message:
            
            table_data = extract_table_data(response)
            
            obs_list = obs_list + table_data
            
    return message, obs_list

def check_image_in_db(config,params,testing=False,verbose=False):
    """Function to check the database to see if an image is present
    
    Inputs:
        :params dict config: script configuration parameters
        :param dict params: containing image_name as a parameter.
    """
    
    end_point = 'image_search'
    
    key_order = [ 'image_name' ]
    
    query = build_url_query(end_point,key_order,params)
    
    (message, response) = ask_db(query,config['db_token'],
                                testing=testing,verbose=verbose)
    
    return message
    
def extract_table_data(html_text):
    """Function to extract table data from HTML-format text"""
    
    lines = html_text.split('\n')
    
    istart = None
    iend = None
    for i,l in enumerate(lines):
        if '<table>' in l:
            istart = i
        elif '</table>' in l:
            iend = i
    
    data = []
    
    for l in lines[istart+1:iend]:
        
        if l.lstrip()[0:4] == '<tr>' and '<th>' not in l:
            
            ldata = l.lstrip().replace('<tr>','').replace('</tr>\n','')
            ldata = ldata.replace('<td>','::').replace('</td>','::').split('::')
                        
            entry = {}
            entry['pk'] = int(ldata[1])
            entry['grp_id'] = ldata[3]
            entry['track_id'] = ldata[5]
            entry['timestamp'] = datetime.strptime(ldata[7],"%Y-%m-%dT%H:%M:%S")
            entry['time_expire'] = datetime.strptime(ldata[9],"%Y-%m-%dT%H:%M:%S")
            entry['status'] = ldata[11]
            
            data.append( entry )
    
    return data

def build_url_query(end_point,key_order,params):
    """Function to build an URL query string in the format necessary for
    an API"""
    
    query = end_point + '/'
    
    for i,key in enumerate(key_order):
        
        value = params[key]
        
        if i < len(key_order)-1:
            query = query + key + '=' + str(value) + '&'
        else:
            query = query + key + '=' + str(value)
    
    return query
    
################################################################################
def talk_to_db(query,token,testing=False,verbose=False):
    """Method to communicate with various APIs of the ROME/REA database to
    submit information (i.e. POST)
    
    Required arguments are:
        query        string  API endpoint address and query parameters 
                            concatenated in URL format
        token       string   User token login for database
    
    E.g. if submitting to URL:
        http://robonet.lco.global/db/record_obs_request/
    end_point = 'record_obs_request
    
    Optional arguments:
        testing    boolean            Switch to localhost URL for testing
                                        Def=False for operations
        verbose    boolean            Switch for additional debugging output
    """
    
    if testing == True:
        host_url = 'http://127.0.0.1:8000/db/'
    else:
        host_url = 'https://robonet.lco.global/db/'
    if host_url[-1:] != '/':
        host_url = host_url + '/'
    
    url = path.join(host_url,query)
    if url[-1:] != '/':
        url = url + '/'
    
    if verbose==True:
        print 'End point URL:',url
    
    headers = {'Authorization': 'Token ' + token}
    
    response = requests.post(url, headers=headers, verify=True)
    
    if verbose==True:

        print 'Completed successfully'
    
    message = parse_db_message(response)
    
    return message

def ask_db(query,token,testing=False,verbose=False):
    """Method to communicate with various APIs of the ROME/REA database to 
    extract information (i.e. GET)
    
    Required arguments are:
        query        string  API endpoint address and query parameters 
                            concatenated in URL format
        token       string   User token login for database
    
    E.g. if submitting to URL:
        http://robonet.lco.global/db/record_obs_request/
    end_point = 'record_obs_request
    
    Optional arguments:
        testing    boolean            Switch to localhost URL for testing
                                        Def=False for operations
        verbose    boolean            Switch for additional debugging output
    """
    
    if testing == True:
        host_url = 'http://127.0.0.1:8000/db'
    else:
        host_url = 'https://robonet.lco.global/db'
    
    url = path.join(host_url,query)
    if url[-1:] != '/':
        url = url + '/'
    
    if verbose==True:
        print 'End point URL:',url
    
    headers = {'Authorization': 'Token ' + token}
    
    response = requests.get(url, headers=headers)
    
    message = parse_db_message(response)
    
    return message, response.text

def parse_db_message(response):
    """Function to parse the database response message"""
    
    message = None

    for line in response.text.split('\n'):

        if 'DBREPLY' in line:

            message = line.lstrip().replace('<h5>','').replace('</h5>','')
            message = message.replace('<center>','').replace('</center>','')
            message = message.replace('DBREPLY: ','')
    
    if message == None:
        message = response.text
        
    return message
    