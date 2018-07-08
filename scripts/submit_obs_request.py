# -*- coding: utf-8 -*-
"""
Created on Fri Jul  6 17:57:16 2018

@author: rstreet
"""
from os import path
from sys import argv
import obs_control
import validation
import update_db_2
import observation_classes

def obs_request_from_file():
    """Function to compose an observation request from text file input and 
    submit it"""
    
    (obs_file,simulate) = get_args()
    
    config = parse_config(simulate)
    
    obs_requests = compose_obs_from_file_data(config, obs_file)
        
    build_and_submit_obs_requests(config,obs_requests,simulate)
    
    submit_status = record_obs_request(obs_requests)
    
def compose_obs_from_file_data(config, obs_file):
    """Function to parse a file containing a full description of observation
    parameters and convert it to an ObsRequest object."""
    
    if path.isfile == False:
        print('Error: Cannot find input file '+obs_file)
        exit()
    
    file_lines = open(obs_file,'r').readlines()
    
    robs = observation_classes.ObsRequest()
    
    for line in file_lines:
        
        line.replace('\n','').replace('\t',' ')
        
        if '#' in line:
            line = line.split('#')[0]
        
        if '[' in line and ']' in line:
        
            i1 = line.index('[')
            i2 = line.index(']')
            
            entries = line[i1+1:i2].split(',')
            
            key = line[0:i1].split()[0]
            
            if key == 'exposure_times':
                
                value = convert_list_entries(entries,'float')
                
            elif key == 'exposure_counts':
                
                value = convert_list_entries(entries,'int')
                
            else:
                
                value = convert_list_entries(entries,'str')
            
        else:
        
            (key, value) = line.split()
            
            try:
                
                value = float(value)
                
            except ValueError:
                
                pass
            
        try:
            
            val = getattr(robs,key)
            
            setattr(robs,key,value)
        
        except AttributeError:
            
            print('ERROR: input file contains a non-standard parameter '+key)
            exit()
    
    
    robs.user_id = config['user_id']
    robs.proposal_id = config['proposal_id']
    robs.token = config['token']
    robs.req_origin = 'manual'
    
    obs_requests = [ robs ]

    return obs_requests

def build_and_submit_obs_requests(config,obs_requests,simulate):
    """Function to take a list of ObsRequest objects as specified by the user
    and build the LCO-format JSON observation user requests appropriate to the 
    type of the group requested, resolving cadence windows where necessary, 
    before submitting them."""
    
    for obs in obs_requests:
        
        try:
        
            if obs.cadence == 0.0 or obs.cadence == None:
                
                ur = obs.build_single_request( )
                
            else:
                
                ur = obs.build_cadence_request( )
            
        except AttributeError:
            
            ur = obs.build_cadence_request( )
        
        if simulate == False:
                        
            response = obs.submit_request(ur, config)
        
        else:
                
            response = 'SIM_add_OK'
        
        print 'Obs request '+obs.group_id+' submitted to LCO with response: '+\
                obs.submit_response+' '+obs.submit_status

def parse_config(simulate):
    """Function to read the user's configuration file for obs_control and parse
    the simulation parameter to override the simulate parameter at the
    user's request"""
    
    config = obs_control.read_config()
    
    if simulate == False:
        
        config['simulate'] = 'False'
        
    else:
        config['simulate'] = 'True'
    
    return config
    
def record_obs_request(obs_requests):
    """Function to record the observation to the ROME/REA DB"""
    
    status_list = []
    
    obs = obs_requests[0]
    
    print('Exposure groups submitted to DB with response(s): ')
    
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
        
        status = update_db_2.add_request(obs.name, (obs.cadence*60.0), \
            int(obs.exposure_times[i]), timestamp=obs.ts_submit, \
            time_expire=obs.ts_expire, \
            pfrm_on=obs.pfrm, onem_on=obs.onem, twom_on=obs.twom, \
            request_type=obs.request_type, which_site=obs.site,\
            which_filter=obs.filters[i],which_inst=obs.instrument, \
            grp_id=obs.group_id, track_id=obs.track_id, req_id=obs.req_id,\
            n_exp=obs.exposure_counts[i],\
            request_status=req_status)
                        
        status_list.append( status )  
        
        print(obs.filters[i]+': '+repr(status))
        
    return status_list
    
def get_args():
    """Function to harvest the required user-specified parameters"""
    
    simulate = True
    
    if len(argv) > 2:
        
        obs_file = argv[1]
        opt = argv[2]
        
    else:
        
        obs_file = raw_input('Please enter the path to the observation specification file: ')
        opt = raw_input('Submit active observation requests? Y or N: ')
    
    if str(opt).upper() == 'Y':
        
        simulate = False
    
    if str(opt).lower() == 'submit':
        
        simulate = False
        
    return obs_file, simulate

def convert_list_entries(input_list,new_type):
    """Function to convert the entries in a list to one of string, float 
    or integer"""
    
    if new_type not in [ 'str', 'float', 'int']:
        
        return input_list
    
    output_list = []
    
    for item in input_list:
        
        if new_type == 'str':
        
            output_list.append( str(item.strip()) )
            
        elif new_type == 'float':
            
            output_list.append( float(item) )
            
        elif new_type == 'int':
            
            output_list.append( int(item) )
    
    return output_list
    
if __name__ == '__main__':
    
    obs_request_from_file()