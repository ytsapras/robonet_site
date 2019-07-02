# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 18:07:21 2017

@author: rstreet
"""
from os import environ, path
from sys import path as systempath
from sys import exit
from local_conf import get_conf
robonet_site = get_conf('robonet_site')
systempath.append(robonet_site)
environ.setdefault('DJANGO_SETTINGS_MODULE', 'robonet_site.settings')
from django.core import management
from django.conf import settings
from django.utils import timezone
from django import setup
from datetime import datetime, timedelta
import pytz
setup()

import urllib
import utilities
import requests
import instrument_overheads
import json
import httplib
from sys import exit
from exceptions import ValueError

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
        self.jitter = None
        self.priority = 1.0
        self.json_request = None
        self.ts_submit = None
        self.ts_expire = None
        self.airmass_limit = 2.0
        self.moon_sep_min = 30.0
        self.user_id = None
        self.token = None
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
                exp_list + ' ' + str(self.cadence) + ' ' + self.group_id
        return output
    
    def build_cadence_request(self, log=None, debug=False):
        
        if debug == True and log != None:
            log.info('Building Valhalla observation request')
            
        self.get_group_id()
        ur = {
            'group_id': self.group_id, 
            'proposal': self.proposal_id,
            'ipp_value': self.priority,
            'operator': 'SINGLE',
            'observation_type': 'NORMAL', 
              }
        if debug == True and log != None:
            log.info('User request parameters: ' + str( ur ))
        
        if type(self.ra) == type(1.0):
            ra_deg = self.ra
            dec_deg = self.dec
        else:
            (ra_deg, dec_deg) = utilities.sex2decdeg(self.ra, self.dec)
        target =   {
                    'name': str(self.name),
                    'type': 'SIDEREAL',
                    'ra'	: ra_deg,
                    'dec': dec_deg,
                    'proper_motion_ra': 0, 
                    'proper_motion_dec': 0,
                    'parallax': 0, 
                    'epoch': 2000,	  
                    }
        if debug == True and log != None:
            log.info('Target dictionary: ' + str( target ))
            
        location = {
                    'telescope_class' : str(self.tel).replace('a',''),
                    'site':             str(self.site),
                    'observatory':      str(self.observatory)
                    }
        if debug == True and log != None:
            log.info('Location dictionary: ' + str( location ))
        
        constraints = { 
        		  'max_airmass': float(self.airmass_limit),
                    'min_lunar_distance': float(self.moon_sep_min)
                    }
        if debug == True and log != None:
            log.info('Constraints dictionary: ' + str( constraints ))
        
        (self.ts_submit,self.ts_expire) = get_obs_dates(self.ttl)

        cadence = { 'start': self.ts_submit.strftime("%Y-%m-%d %H:%M:%S"),
                    'end': self.ts_expire.strftime("%Y-%m-%d %H:%M:%S"),
                    'period': float(self.cadence),
                    'jitter': float(self.jitter) }
        if debug == True and log != None:
            log.info('Cadence dictionary: '+str(cadence))
            
        ur['requests'] = []
        molecule_list = self.build_molecule_list(debug=debug,log=log)
        
        if len(molecule_list) > 0:
            req = { 
                    'acceptability_threshold': 90,
                    'target': target,
                    'molecules': molecule_list,
                    'cadence': cadence,
                    'location': location,
                    'constraints': constraints
                   }
            ur['requests'].append(req)
            if debug == True and log != None:
                log.info('Request dictionary: ' + str(req))

            ur = self.get_cadence_requests(ur,log=log)
            
            if debug == True and log != None:
                if 'requests' in ur.keys():
                    for r in ur['requests']:
                        try:
                            if len(r['windows']) == 0:
                                log.info('WARNING: scheduler returned no observing windows for this target')
                                self.submit_status = 'No_obs_submitted'
                                self.submit_response = 'No_obs_submitted'
                                self.req_id = '9999999999'
                                self.track_id = '99999999999'
                            else:
                                log.info('Request windows: '+repr(r['windows']))
                        except TypeError:
                            log.info('WARNING: scheduler returned invalid observing windows for this target')
                            log.info('request dictionary contains: '+repr(r))
                            self.submit_status = 'No_obs_submitted'
                            self.submit_response = 'No_obs_submitted'
                            self.req_id = '9999999999'
                            self.track_id = '99999999999'
                        except KeyError:
                            log.info('WARNING: scheduler returned no valid observing windows for this target')
                            log.info('request dictionary contains: '+repr(r))
                            self.submit_status = 'No_obs_submitted'
                            self.submit_response = 'No_obs_submitted'
                            self.req_id = '9999999999'
                            self.track_id = '99999999999'
                elif 'detail' in ur.keys():
                    self.submit_status = 'No_obs_submitted'
                    if self.submit_response != None:
                        self.submit_response = self.submit_response+' '+ur['detail']
                    else:
                        self.submit_response = 'WARNING: ' + ur['detail']
                    if debug == True and log != None:
                        log.info('WARNING: problem obtaining observing windows for this target: '+ur['detail'])
                elif 'non_field_errors' in ur.keys():
                    self.submit_status = 'No_obs_submitted'
                    if self.submit_response != None:
                        self.submit_response = self.submit_response+' '.join(ur['non_field_errors'])
                    else:
                        self.submit_response = 'WARNING: ' + ' '.join(ur['non_field_errors'])
                    if debug == True and log != None:
                            log.info('WARNING: problem obtaining observing windows for this target:'+' '.join(ur['non_field_errors']))
                    
                
        if debug == True and log != None:
            log.info(' -> Completed build of observation request ' + self.group_id)
            log.info(' -> Submit response: '+str(self.submit_response))
            
        return ur
    
    def build_cadence_request_aeon(self, log=None, debug=False):
        
        if debug == True and log != None:
            log.info('Building Valhalla-AEON observation request')
            
        self.get_group_id()
        
        if type(self.ra) == type(1.0):
            ra_deg = self.ra
            dec_deg = self.dec
        else:
            (ra_deg, dec_deg) = utilities.sex2decdeg(self.ra, self.dec)
            
        target = {
                'name': str(self.name),
                'type': 'SIDEREAL',
                'ra'	: ra_deg,
                'dec': dec_deg,
                'proper_motion_ra': 0, 
                'proper_motion_dec': 0,
                'parallax': 0, 
                'epoch': 2000,	  
                }
        
        if debug == True and log != None:
            log.info('Target dictionary: ' + str( target ))
            
        location = {
                    'telescope_class' : str(self.tel).replace('a',''),
                    'site':             str(self.site),
                    'enclosure':      str(self.observatory)
                    }
                    
        if debug == True and log != None:
            log.info('Location dictionary: ' + str( location ))
        
        constraints = { 
        		    'max_airmass': float(self.airmass_limit),
                      'min_lunar_distance': float(self.moon_sep_min)
                      }
                    
        if debug == True and log != None:
            log.info('Constraints dictionary: ' + str( constraints ))
        
        (self.ts_submit,self.ts_expire) = get_obs_dates(self.ttl)

        cadence = { 'start': self.ts_submit.strftime("%Y-%m-%d %H:%M:%S"),
                    'end': self.ts_expire.strftime("%Y-%m-%d %H:%M:%S"),
                    'period': float(self.cadence),
                    'jitter': float(self.jitter) }
                    
        inst_config_list = self.build_image_config_list(target, constraints)
        
        request_group = {'name': self.group_id,
                         'proposal': self.proposal_id,
                         'ipp_value': float(self.priority),
                         'operator': 'SINGLE',
                         'observation_type': 'NORMAL',
                         'requests': [{'configurations': inst_config_list,
                                       'cadence': cadence,
                                       'location': location}]
                         }
        
        ur = self.get_cadence_requests(request_group,log=log)

        return ur

    def build_image_config_list(self, target, constraints):
        """Function to compose the instrument configuration dictionary"""

        config_list = []
        
        for i in range(0,len(self.exposure_counts),1):
            
            config = {'type': 'EXPOSE',
                      'instrument_type': self.instrument_class,
                      'target': target,
                      'constraints': constraints,
                      'acquisition_config': {},
                      'guiding_config': {},
                      'instrument_configs': [ {
                                            'exposure_time': float(self.exposure_times[i]),
                                            'exposure_count': int(self.exposure_counts[i]),
                                            'optical_elements': {
                                                'filter': self.filters[i]},
                                                } ]
                      }
            
            config_list.append(config)
            
        return config_list
    
    def build_single_request(self, log=None, debug=False):
        
        if debug == True and log != None:
            log.info('Building Valhalla observation request')
            
        self.get_group_id()
        ur = {
            'group_id': self.group_id, 
            'proposal': self.proposal_id,
            'ipp_value': self.priority,
            'operator': 'SINGLE',
            'observation_type': 'NORMAL', 
              }
        if debug == True and log != None:
            log.info('User request parameters: ' + str( ur ))
        
        if type(self.ra) == type(1.0):
            ra_deg = self.ra
            dec_deg = self.dec
        else:
            (ra_deg, dec_deg) = utilities.sex2decdeg(self.ra, self.dec)
        target =   {
                    'name': str(self.name),
                    'type': 'SIDEREAL',
                    'ra'	: ra_deg,
                    'dec': dec_deg,
                    'proper_motion_ra': 0, 
                    'proper_motion_dec': 0,
                    'parallax': 0, 
                    'epoch': 2000,	  
                    }
        if debug == True and log != None:
            log.info('Target dictionary: ' + str( target ))
            
        location = {
                    'telescope_class' : str(self.tel).replace('a',''),
                    'site':             str(self.site),
                    'observatory':      str(self.observatory)
                    }
        if debug == True and log != None:
            log.info('Location dictionary: ' + str( location ))
        
        constraints = { 
        		  'max_airmass': float(self.airmass_limit),
                    'min_lunar_distance': float(self.moon_sep_min)
                    }
        if debug == True and log != None:
            log.info('Constraints dictionary: ' + str( constraints ))
        
        (self.ts_submit,self.ts_expire) = get_obs_dates(self.ttl)

        windows = [ 
                    { 'start': self.ts_submit.strftime("%Y-%m-%d %H:%M:%S"),
                      'end': self.ts_expire.strftime("%Y-%m-%d %H:%M:%S") }
                    ]
                    
        if debug == True and log != None:
            log.info('Cadence dictionary: '+str(cadence))
            
        ur['requests'] = []
        molecule_list = self.build_molecule_list(debug=debug,log=log)
        
        if len(molecule_list) > 0:
            req = { 
                    'acceptability_threshold': 90,
                    'target': target,
                    'molecules': molecule_list,
                    'windows': windows,
                    'location': location,
                    'constraints': constraints
                   }
            ur['requests'].append(req)
            if debug == True and log != None:
                log.info('Request dictionary: ' + str(req))
                            
        if debug == True and log != None:
            log.info(' -> Completed build of observation request ' + self.group_id)
            log.info(' -> Submit response: '+str(self.submit_response))
            
        return ur
        
    def build_molecule_list(self,debug=False,log=None):
        def parse_filter(f):
            filters = { 'SDSS-g': 'gp', 'SDSS-r': 'rp', 'SDSS-i': 'ip' }
            if f in filters.keys():
                return filters[f]
            else:
                raise ValueError('Unrecognized filter ('+f+') requested')
        
        overheads = instrument_overheads.Overhead(self.tel, self.instrument)
        if debug == True and log != None:
            log.info('Instrument overheads ' + overheads.summary() )        
        
        molecule_list = []
                
        for i,exptime in enumerate(self.exposure_times):
            nexp = self.exposure_counts[i]
            f = self.filters[i]
            defocus = self.focus_offset[i]
            
            molecule = {
                        'type': 'EXPOSE',
                        'instrument_name': self.instrument_class,
                        'filter': parse_filter(f),
                        'exposure_time': exptime,
                        'exposure_count': nexp,
                        'bin_x': 1,
                        'bin_y': 1,
                        'fill_window': False,
                        'defocus': defocus,
                        'ag_mode': 'OPTIONAL',
                        }
                        
            if debug == True and log != None:
                log.info(' -> Molecule: ' + str(molecule))
    
            molecule_list.append(molecule)

        return molecule_list  
                
    def get_cadence_requests(self,ur,log=None):
        
        
        end_point = "userrequests/cadence"
        ur = self.talk_to_lco(ur,end_point,'POST')
        
        if log !=None:
            log.info('Generated cadences, userrequest now: '+repr(ur))
            
        if 'error_type' in ur.keys():
            self.submit_response = 'ERROR: '+ur['error_msg']
        
        if log != None:
            if 'error_type' in ur.keys():
                log.info('ERROR getting cadence request: '+ur['error_msg'])
            else:
                log.info('Received response from LCO cadence API')
                
        return ur
    
    def submit_request(self, ur, config, log=None):
        
        if self.submit_status == 'No_obs_submitted':
            self.submit_response = 'No_obs_submitted'
            self.req_id = '9999999999'
            self.track_id = '99999999999'
            if log != None:
                log.info('WARNING: ' + self.submit_status)
                
        elif str(config['simulate']).lower() == 'true':
            self.submit_status = 'SIM_add_OK'
            self.submit_response = 'Simulated'
            self.req_id = '9999999999'
            self.track_id = '99999999999'
            if log != None:
                log.info(' -> IN SIMULATION MODE: ' + self.submit_status)
        
        else:
            end_point = 'userrequests'
            response = self.talk_to_lco(ur,end_point,'POST')
            self.parse_submit_response( response, log=log )
            
        if log != None:
            log.info(' -> Completed obs submission, submit response:')
            log.info(str(self.submit_response))
        
        return self.submit_status

    def cancel_request(self):
        """Method to cancel an observation request within the LCO network
        scheduler"""
        
        if self.track_id != None:
            end_point = 'userrequests/'+str(self.track_id)+'/cancel'
            response = self.talk_to_lco(None,end_point,'POST')
            
            if 'state' in response.keys():
                self.submit_status = response['state']
                
        return self.submit_status
    
    def talk_to_lco(self,ur,end_point,method):
        """Method to communicate with various APIs of the LCO network. 
        ur should be a user request while end_point is the URL string which 
        should be concatenated to the observe portal path to complete the URL.  
        Accepted end_points are:
            "userrequests" 
            "userrequests/cadence"
            "userrequests/<id>/cancel"
        Accepted methods are:
            POST GET
        """
        
        jur = json.dumps(ur)
        
        headers = {'Authorization': 'Token ' + self.token}
        
        if end_point[0:1] == '/':
            end_point = end_point[1:]
        if end_point[-1:] != '/':
            end_point = end_point+'/'
        url = path.join('https://observe.lco.global/api',end_point)
        
        if method == 'POST':
            if ur != None:
                response = requests.post(url, headers=headers, json=ur).json()
            else:
                response = requests.post(url, headers=headers).json()
        elif method == 'GET':
            response = requests.get(url, headers=headers, json=ur).json()
            
        return response

        
    def parse_submit_response( self, response, log=None, debug=False ):
        
        if debug == True and log != None:
            log.info('Request response = ' + str(submit_string) )
        
        if 'id' in response.keys():
            self.track_id = str(response['id'])
            self.req_id = '9999999999'
            self.submit_response = 'id = '+str(response['id'])
            self.submit_status = 'add_OK'
        else:
            self.submit_response = 'error'
            self.submit_status = 'WARNING'
            self.track_id = '9999999999'
            self.req_id = '9999999999'
       
        if debug == True and log != None:
            log.info('Submit status: ' + str(self.submit_status))
            log.info('Submit response: ' + str(self.submit_response))
               
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
    elif request_type == 'N':
        request_desc = 'rea'
    elif request_type == 'I':
        request_desc = 'man'
    else:
        request_desc = 'unknown'
        raise ValueError('Unknown observation request type, ' + request_type)
    
    return request_desc

def get_obs_dates(ttl):
    """Function to calculate the submit and expiry dates for an observation
    group.  
    
    The function assumes the request will be submitted and become active
    immediately, and expire at submission+TTL
    """
    
    ts_submit = timezone.now() + timedelta(seconds=(10*60))
    ts_expire = ts_submit + timedelta(seconds=(ttl*24*60*60))

    return ts_submit, ts_expire

class SubObsRequest:
    """Class describing the sub-requests which are generated by the LCO
    scheduler for every cadence ObsRequest."""
    
    def __init__(self):
        self.sr_id = None
        self.request_grp_id = None
        self.request_track_id = None
        self.state = None
        self.window_start = None
        self.window_end = None
        self.time_executed = None
            
    def summary(self):
        
        text = str(self.sr_id)+' '+str(self.request_grp_id)+' '+\
            str(self.request_track_id)+' '+str(self.state)+' '+\
            self.window_start.strftime("%Y-%m-%dT%H:%M:%S")+' '+\
            self.window_end.strftime("%Y-%m-%dT%H:%M:%S")
        
        if self.time_executed != None and str(self.time_executed) != 'None':
            
            text = text + ' ' + self.time_executed.strftime("%Y-%m-%dT%H:%M:%SZ")
            
        else:

            text = text + ' Not observed'
            
        return text
    
    def get_status(self):
        
        utcnow = datetime.utcnow()
        utcnow = utcnow.replace(tzinfo=pytz.UTC)
        
        if self.state == 'COMPLETED' or self.time_executed != None:
            
            status = 'Executed'
                    
        elif self.state == 'CANCELED':
            
            status = 'Canceled'
                
        elif self.window_end < utcnow and self.time_executed == None:
                            
            status = 'Not executed'
                        
        elif self.state == 'WINDOW_EXPIRED' and self.time_executed == None:
            
            status = 'Not executed'
            
        else:
            
            status = 'Pending'

        return status

class SurveyField:
    """Class describing observations for a given survey field pointing"""
    
    def __init__(self):
        
        self.field_id = None
        self.instruments = []
        self.subrequests = []
        self.obsrequests = []
    
    def summary(self):
        
        grpids = ''
        for obs in self.obsrequests:
            grpids += ' '+obs.grp_id
    
        subreqs = ''
        for k,camera in enumerate(self.instruments):
            grpids += ' '+camera+': '+repr(self.obsrequests[k])
            subreqs += ' '+camera+': '+repr(self.subrequests[k])
            
        output = str(self.field_id)+' '+'\n'+\
                '                  -> obsrequests: '+grpids+'\n'+\
                '                  -> sub-obsrequests: '+subreqs
        
        return output