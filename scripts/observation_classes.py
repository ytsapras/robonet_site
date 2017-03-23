# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 18:07:21 2017

@author: rstreet
"""
from os import environ, path
from sys import path as systempath
from local_conf import get_conf
robonet_site = get_conf('robonet_site')
systempath.append(robonet_site)
environ.setdefault('DJANGO_SETTINGS_MODULE', 'robonet_site.settings')
from django.core import management
from django.conf import settings
from django.utils import timezone
from django import setup
from datetime import datetime, timedelta
setup()

import urllib
import utilities
import requests
import instrument_overheads
import json
import httplib
from sys import exit
from exceptions import ValueError

LCO_API_URL = 'https://lco.global/observe/api/'

class ObsRequest:
    
    def __init__(self):
        self.name = None
        self.group_id = None
        self.track_id = None
        self.req_id = None
        self.ra = None
        self.dec = None
        self.site = None
        self.observatory = None
        self.tel = None
        self.instrument = None
        self.instrument_class = None
        self.filters = None
        self.group_type = 'single'
        self.exposure_times = []
        self.exposure_counts = []
        self.cadence = None
        self.priority = 1.0
        self.json_request = None
        self.ts_submit = None
        self.ts_expire = None
        self.user_id = None
        self.proposal_id = None
        self.ttl = None
        self.focus_offset = []
        self.request_type = None
        self.req_origin = None
        self.pfrm = False
        self.onem = False
        self.twom = False
        self.submit_response = None
        self.submit_status = None

    def get_group_id(self):
        dateobj = timezone.now()
        time = float(dateobj.hour) + (float(dateobj.minute)/60.0) + \
        (float(dateobj.second)/3600.0) + (float(dateobj.microsecond)/3600e6)
        time = round(time,8)
        ctime = str(time)
        date = dateobj.strftime('%Y%m%d')
        TS = date+'T'+ctime
        req_type = get_request_desc(self.request_type)
        self.group_id = str(req_type).upper().replace('-','')+TS

    def set_aperture_class(self):
        if '0m4' in self.tel:
            self.pfrm = True
        elif '1m0' in self.tel:
            self.onem = True
        elif '2m0' in self.tel:
            self.twom = True
    
    def summary(self):
        exp_list = ''
        f_list = ''
        for i in range(0,len(self.exposure_counts),1):
            exp_list = exp_list + ' ' + str(self.exposure_counts[i])
            f_list = f_list + ' ' + self.filters[i]
            
        output = str(self.name) + ' ' + str(self.ra) + ' ' + str(self.dec) + \
                ' ' + str(self.site) + ' ' + str(self.observatory) + ' ' + \
                ' ' + str(self.instrument) + ' ' + f_list + ' ' + \
                exp_list + ' ' + str(self.cadence)
        return output

    def build_json_request(self, config, log=None, debug=False):
        
        def parse_filter(f):
            filters = { 'SDSS-g': 'gp', 'SDSS-r': 'rp', 'SDSS-i': 'ip' }
            if f in filters.keys():
                return filters[f]
            else:
                raise ValueError('Unrecognized filter ('+f+') requested')
                
        proposal = { 
                    'proposal_id': config['proposal_id'],
                    'user_id'    : config['user_id'] 
                    }
        if debug == True and log != None:
            log.info('Building ODIN observation request')
            log.info('Proposal dictionary: ' + str( proposal ))
            
        location = {
                    'telescope_class' : str(self.tel).replace('a',''),
                    'site':             str(self.site),
                    'observatory':      str(self.observatory)
                    }
        if debug == True and log != None:
            log.info('Location dictionary: ' + str( location ))
            
        (ra_deg, dec_deg) = utilities.sex2decdeg(self.ra, self.dec)
        target =   {
                    'name'		    : str(self.name),
                    'ra'		          : ra_deg,
                    'dec'		    : dec_deg,
                    'proper_motion_ra'  : 0, 
                    'proper_motion_dec' : 0,
                    'parallax'	   : 0, 
                    'epoch'  	   : 2000,	  
                    }
        if debug == True and log != None:
            log.info('Target dictionary: ' + str( target ))
            
        constraints = { 
        		  'max_airmass': 2.0,
                    'min_lunar_distance': 10
                    }
        if debug == True and log != None:
            log.info('Constraints dictionary: ' + str( constraints ))
            
        imager = instrument_overheads.Overhead(self.tel, self.instrument)
        self.instrument_class = imager.instrument_class
        if debug == True and log != None:
            log.info('Instrument overheads ' + imager.summary() )
            
        self.get_group_id()   
        ur = { 'group_id': self.group_id }
        reqList = []
        
        self.ts_submit = timezone.now() + timedelta(seconds=(10*60))
        self.ts_expire = self.ts_submit + timedelta(seconds=(self.ttl*24*60*60))
        
        request_start = self.ts_submit
        while request_start < self.ts_expire:
            molecule_list = []
            
            for i,exptime in enumerate(self.exposure_times):
                nexp = self.exposure_counts[i]
                f = self.filters[i]
                defocus = self.focus_offset[i]
            
                molecule = { 
                		 # Required fields
                		 'exposure_time'   : exptime,    
                		 'exposure_count'  : nexp,	     
                		 'filter'	   : parse_filter(f),      
                		 
                		 'type' 	   : 'EXPOSE',      
                		 'ag_name'	   : '',	     
                		 'ag_mode'	   : 'Optional',
                		 'instrument_name' : imager.instrument,
                		 'bin_x'	   : 1,
                		 'bin_y'	   : 1,
                		 'defocus'	   : defocus      
                	       }
                if debug == True and log != None:
                    log.info(' -> Molecule: ' + str(molecule))
        
                molecule_list.append(molecule)
                
            window = float(config['request_window']) * 60.0 * 60.0
            exposure_group_length = imager.calc_group_length( nexp, exptime )
            request_end = request_start + \
                     timedelta( seconds= ( exposure_group_length + window ) )

            req = { 'observation_note':'',
                    'observation_type': 'NORMAL', 
                    'target': target , 
                    'windows': [ { 'start': request_start.strftime("%Y-%m-%d %H:%M:%S"), 
                                   'end': request_end.strftime("%Y-%m-%d %H:%M:%S") } ],
                    'fail_count': 0,
                    'location': location,
                    'molecules': molecule_list,
                    'type': 'request', 
                    'constraints': constraints
                    }
            reqList.append(req)
            if debug == True and log != None:
                log.info('Request dictionary: ' + str(req))
                
            request_start = request_end + \
                    timedelta( seconds= ( self.cadence*24.0*60.0*60.0 ) )
                    
        ur['requests'] = reqList
        if len(reqList) == 1:
            ur['operator'] = 'single'
        else:
            ur['operator'] = 'many'
        ur['type'] = 'compound_request'
        self.json_request = json.dumps(ur)
        if debug == True and log != None:
            log.info(' -> Completed build of observation request')
    
    def submit_request(self, config, log=None, debug=False):
        
        params = {'username': config['user_id'] ,
                  'password': config['odin_access'], 
                  'proposal': config['proposal_id'], 
                  'request_data' : self.json_request}
        if debug == True and log != None:
            log.info( 'Observation request parameters for submission: ' + \
                                    str(params) )
        
        if str(config['simulate']).lower() == 'true':
            self.submit_status = 'SIM_add_OK'
            self.submit_response = 'Simulated'
            self.req_id = '9999999999'
            self.track_id = '99999999999'
            if log != None:
                log.info(' -> IN SIMULATION MODE: ' + self.submit_status)
            
        else:
            url_request = urllib.urlencode(params)
            headers = {'Content-type': 'application/x-www-form-urlencoded'}
            
            secure_connect = httplib.HTTPSConnection("lco.global") 
            secure_connect.request("POST", "/observe/service/request/submit", 
                                               url_request, headers)
            submit_string = secure_connect.getresponse().read()	
            
            self.parse_submit_response( config, submit_string, log=log, debug=debug )
            secure_connect.close()
        if log != None:
            log.info(' -> Completed obs submission')
        
        return self.submit_status
        
    def parse_submit_response( self, config, submit_string, log=None, debug=False ):
        
        if debug == True and log != None:
            log.info('Request response = ' + str(submit_string) )
            
        submit_string = submit_string.replace('{','').replace('}','')
        submit_string = submit_string.replace('"','').split(',')
        
        for entry in submit_string: 
            if 'Unauthorized' in entry:
                self.submit_status = 'ERROR'
                self.submit_response = entry
            elif 'time window' in submit_string:
      		self.submit_status = 'ERROR'
                self.submit_response = entry
            else:
                try: 
                    (key,value) = entry.split(':')
                    self.submit_response = str(key) + ' = ' + str(value)
                    self.track_id = str(value)
                    self.submit_status = 'add_OK'
                    self.get_request_numbers(config,log=log)
                except ValueError:
                    try:
                        (key,value) = entry.split('=')
                        self.submit_response = str(key) + ' = ' + str(value)
                        self.track_id = str(value)
                        self.submit_status = 'add_OK'
                        self.get_request_numbers(config,log=log)
                    except:
                        self.submit_response = str(submit_string)
                        self.submit_status = 'WARNING'
                        self.track_id = '9999999999'
                        self.req_id = '9999999999'
       
        if debug == True and log != None:
            log.info('Submit status: ' + str(self.submit_status))
            log.info('Submit response: ' + str(self.submit_response))
    
    def get_request_numbers(self,config,log=None):
        
        self.req_id = ''
        if self.track_id != None:
            token = config['token']
            headers = {'Authorization': 'Token ' + config['token']}
            url = path.join(LCO_API_URL,'user_requests',str(self.track_id)+'/')
            response = requests.get(url, headers=headers).json()
            if 'requests' in response.keys():
                for r in response['requests']:
                    self.req_id = self.req_id +':'+str(r['request_number'])
                self.req_id = self.req_id +':'
            
    def obs_record( self, config ):
        """Method to output a record, in standard format, of the current 
        observation request"""
        
        if 'OK' in str(self.submit_status):
            report = str(self.submit_status)
        else:
            report = str(self.submit_status) + ': ' + str(self.submit_response)
        
        output = ''
        for i, exptime in enumerate(self.exposure_times):
            output = output + \
                str(self.group_id) + ' ' + str(self.track_id) + ' ' + \
                str(self.req_id) + ' ' + \
                str(self.site) + ' ' + str(self.observatory) + ' ' + \
                str(self.tel).replace('a','') + ' ' + \
                str(self.instrument) + ' ' + str(self.name) + ' ' + \
                str(self.request_type)+ ' ' + \
                str(self.ra) + ' ' + str(self.dec) + \
                ' ' + str(self.filters[i]) + ' ' + str(exptime) + ' ' + \
                str(self.exposure_counts[i]) + ' ' + str(self.cadence) + ' ' + \
                str(self.priority) + ' ' + self.ts_submit.strftime("%Y-%m-%dT%H:%M:%S") + ' ' + \
                self.ts_expire.strftime("%Y-%m-%dT%H:%M:%S") + ' ' + \
                str(self.ttl) + ' ' + \
                str(self.focus_offset[i]) + ' ' + str(self.req_origin) + ' '\
                + str(report)+ '\n'
        return output
        
def get_request_desc(request_type):
    """Function to parse the observation request_type from a
    single-digit character into a short, human-readable description"""
    
    if request_type == 'L':
        request_desc = 'rome'
    elif request_type == 'A':
        request_desc = 'rea-hi'
    elif request_type == 'M':
        request_desc = 'rea-lo'
    else:
        request_desc = 'unknown'
        raise ValueError('Unknown observation request type, ' + request_type)
    
    return request_desc