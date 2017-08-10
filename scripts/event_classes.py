# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 13:49:18 2016

@author: rstreet
"""

from astropy.time import Time
from os import getcwd, path, remove, environ
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'..'))
import numpy as np
from field_check import romecheck
from rome_fields_dict import field_dict
import utilities
import query_db
import get_errors
import api_tools

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
from events.models import Event, EventName, Operator

##################################################
# LENS CLASS DESCRIPTION
class Lens():
    """Class describing the basic parameters of a microlensing event 
    (point source point lens) as required for most purposes for the
    database"""

    def __init__(self):
        self.name = None
        self.survey_id = None
        self.ra = None
        self.dec = None
        self.t0 = None
        self.te = None
        self.u0 = None
        self.a0 = None
        self.i0 = None
        self.origin = None
        self.modeler = None
        self.classification = 'microlensing'
        self.last_updated = None
        self.field_id = None
        self.field_pk = None
        self.operator_id = None
        self.operator_pk = None
        self.event_status = None
        self.event_pk = -1
        self.eventname_pk = -1
        self.got_eventname = False
        self.singlemodel_pk = -1
        self.singlemodel_ts = None
        
    def set_par(self,par,par_value):

        if par in [ 'name', 'survey_id', 'classification', 'last_updated' ]: 
            setattr(self,par,par_value)
        else: 
            if par_value == None or str(par_value).lower() == 'none':
                setattr(self,par,par_value)
            else:
                try:
                    setattr(self,par,float(par_value))
                except ValueError:
                    setattr(self,par,par_value)

    def summary(self):
        return str(self.name) + ' ' + str(self.survey_id) + ' ' + \
                str(self.ra) + '  ' + str(self.dec) + '  ' + \
                str(self.t0) + ' ' + str(self.te) + ' ' + str(self.u0) + '  ' +\
                str(self.a0) + ' ' + str(self.i0) + ' ' + str(self.classification)
                
    def get_field(self,config,log=None,debug=False,testing=False):
        """Method to identify which ROME survey field the event falls within,
        based on a query by sky position. 
        Populates the field_id, field_pk and event_status attributes.  
        A negative field_pk indicates that the object falls outside the ROME 
        footprint. 
        """
        params = {'field_ra': self.ra, 'field_dec': self.dec}
        response = api_tools.contact_db(config,params,
                                        'query_field_id',testing=testing)
        if 'Outside' in response:
            self.field_id = 'Outside ROMEREA footprint'
            self.field_pk = response.split(' ')[-1]
            self.event_status = 'NF'
        else:
            (self.field_id, self.field_pk) = response.split(' ')
            self.event_status= 'AC'
            
        if debug==True and log!=None:
            log.info(' -> Identified field: '+str(self.field_id)+' '+\
            str(self.field_pk)+' '+str(self.ra)+' '+str(self.dec))
        
            
    def get_operator(self,config,log=None,debug=False,testing=False):
        """Method to identify which survey operator has found the event,
        based on its long-format name. 
        Populates the operator attribute, and returns 'other' if the
        operator is not recognised.
        """
        
        params = {'name': str(self.name).split('-')[0]}
        response = api_tools.contact_db(config,params,
                                        'query_operator',testing=testing)
        
        self.operator_pk = int(response.split(' ')[0])
        self.operator_id = response.split(' ')[1]
        
        if debug==True and log!=None:
            log.info(' -> Identified operator: '+str(self.operator_pk)+' '+\
            self.operator_id)
            
    def check_event_name_in_DB(self,config,log=None,debug=False,testing=False):
        """Method to check whether the event name is already known to the DB.
        This method sets the eventname_pk attribute.  An index of -1 is returned
        if the event name is not yet in the DB."""
        
        params = {'name': self.name}
        self.eventname_pk = int(api_tools.contact_db(config,params,
                                            'query_eventname',testing=testing))
        
        if log!= None:
            if self.eventname_pk != -1:
                log.info(' -> Identified eventname: '+str(self.name)+' '+\
                str(self.eventname_pk))
            else:
                log.info(' -> Eventname not yet in DB')
                
    def check_event_name_assoc_event(self,config,log=None,debug=False,testing=False):
        """Method to check whether an event name is already associated with 
        a specific event.
        This method sets the boolean got_eventname attribute. 
        False indicates that the eventname is not associated with the event.
        """
        
        params = {'event': self.event_pk,'name': self.name}
        self.got_eventname = bool(api_tools.contact_db(config,params,
                                    'query_eventname_assoc',testing=testing))
        
        if log!= None:
            if self.got_eventname == True:
                log.info(' -> Verified that the eventname is associated with this event')
            else:
                log.info(' -> WARNING: eventname not associated with the event')
                
    def check_event_in_DB(self,config,log=None,debug=False,testing=False):
        """Method to check whether the event is already known to the DB.
        This method sets the event_pk attribute, returning a value of -1 if the
        event is not yet present in the DB."""
        
        params = {'ev_ra': self.ra, 'ev_dec': self.dec}
        self.event_pk = int(api_tools.contact_db(config,params,
                                    'query_event_by_coords',testing=testing))
        
        if log!=None:
            if self.event_pk != -1:
                log.info(' -> Identified event as : '+str(self.event_pk))
            else:
                log.info(' -> Event not yet known to DB')
        
    def add_event_to_DB(self,config,log=None,debug=False,testing=False):
        """Method to add a new event's details to the DB.
        This method also performs the look-up functions to obtain the
        survey field and operator IDs, and sets the event_pk attribute. 
        """
        
        self.get_field(config,log=log,debug=debug,testing=testing)
        self.get_operator(config,log=log,debug=debug,testing=testing)
        year = str(self.name).split('-')[1]
        
        params = { 'field': self.field_pk,
                   'operator': self.operator_pk, 
                   'ev_ra': self.ra, 
                   'ev_dec': self.dec, 
		       'status': self.event_status, 
			 'anomaly_rank': -1,
			 'year': year
                }
        
        response = api_tools.contact_db(config,params,'add_event',testing=testing)
        
        
        if debug==True and log!=None:
            log.info(' -> Tried to add_event with output:')
            log.info(' -> '+str(response))
        
        if 'OK' in response or 'already exists' in response:
            params = {'ev_ra': self.ra,'ev_dec': self.dec}
            self.event_pk = int(api_tools.contact_db(config,params,
                                                     'query_event_by_coords',
                                                     testing=testing))
            if debug==True and log!=None:
                log.info(' -> Event PK: '+str(self.event_pk))
            
    def add_eventname_to_DB(self,config,log=None,debug=False):
        """Method to add a new eventname to the DB, associating it with
        an event which is already ingested.  
        This method also performs the look-up functions to set the eventname_pk
        attribute"""
        
        if self.operator_id == None:
            self.get_operator(log=log,debug=debug)
        
        params = { 'name': self.name,
                   'event': self.event_pk,
                   'operator': self.operator_pk,
                   }
        response = api_tools.contact_db(config,params,'add_event')
        
        if 'True' in response \
                or 'name is already associated with an event' in response:
            self.check_event_name_in_DB(log=log,debug=debug)
            if debug==True and log!=None:
                log.info(' -> Eventname PK: '+str(self.eventname_pk))
    
    def check_last_singlemodel(self,config,log=None,debug=False):
        """Method to check for the last singlemodel for the current event"""
        
        params = { 'event': self.event_pk,
                   'modeler': self.modeler }
        response = api_tools.contact_db(config,params,'query_last_singlemodel')
        
        self.singlemodel_pk = int(response.split(' ')[0])
        self.singlemodel_ts = datetime.strptime("%Y-%m-%dT%H:%M:%S",response.split(' ')[1])
        
    def add_singlemodel_to_DB(self,config,log=None,debug=False):
        """Method to add a singlemodel to the DB."""
        
        if debug==True and log!=None:
            log.info(' -> Attempting to add a single lens model with parameters:')
            log.info(str(self.name)+' '+str(self.t0)+' '+str(self.te)+\
                str(self.u0)+' '+str(last_updated)+' '+str(self.modeler))
                
        params = {'event': self.event_pk,
                  'Tmax':self.t0,'e_Tmax':0.0,
                  'tau':self.te,'e_tau':0.0,
                  'umin':self.u0,'e_umin':0.0,
                  'modeler':self.modeler,
                  'last_updated':self.last_updated.strftime("%Y-%m-%dT%H:%M:%S")
                  }
            
        response = api_tools.contact_db(config,params,'add_singlemodel')
    
        if debug==True and log!=None:
            log.info(' -> Outcome of adding the single lens model:')
            log.info(str(response))
            
    def sync_event_with_DB(self,config,last_updated,log=None,debug=False):
        """Method to sync the latest survey parameters with the database.
        
        Checks if event is known to the DB
        Checks if eventname is known to the DB
        Adds the event if not known
        Adds the eventname if not known
        Queries for most recent single-lens model parameters
        Updates the single-lens model parameters if necessary
        """
        
        self.check_event_in_DB(config,log=log,debug=debug)
        if self.event_pk == -1:
            self.add_event_to_DB(config,log=log,debug=debug)
        
        self.check_event_name_in_DB(log=log,debug=debug)
        if self.eventname_pk == -1:
            self.add_eventname_to_DB(config,log=log,debug=debug)
            
        self.check_last_singlemodel(log=log,debug=debug)
        if self.singlemodel_pk == -1 or self.last_updated > self.singlemodel_ts:
            self.add_singlemodel_to_DB(config,log=log,debug=debug)
            
    
    def get_params(self):
        """Method to return the parameters of the current event in a 
        dictionary format
        """
        key_list = [ 'name', 'survey_id', 'ra', 'dec', 't0', 'te', 'u0', \
                        'a0', 'i0', 'origin']
        params = {}
        for key in key_list:
            params[ key ] = getattr( self, key )
        return params

            
class EventDataSet():
    """Class describing all parameters associated with a data set taken for
    a microlensing event"""
    
    def __init__(self):
        self.event_name = None
        self.data_file = None
        self.last_updated = None
        self.last_hjd = None
        self.last_mag= None
        self.tel = None
        self.instrument = ''
        self.filter = None
        self.ndata = 0
        self.baseline = None
        self.g = None
        
    def sync_artemis_data_pars_with_db(self,log=None):
        """Method to update the database with the data and alignment 
        parameters from ARTEMiS"""

        if log!=None:
            log.info('Syncing ARTEMiS data and align parameters with DB')
            log.info(repr(self.event_name))
        
        params = {'event': event.pk,
                  'datafile': self.data_file,
                  'last_upd': self.last_updated,
                  'last_hjd': self.last_hjd,
                  'last_mag': self.last_mag,
                  'ndata': self.ndata,
                  'tel': self.tel,
                  'inst': self.instrument,
                  'filt': self.filter,
                  'baseline': self.baseline,
                  'g': self.g,
                  }
        response = api_tools.submit_datafile_record(config,params)
        
        if log!=None:
            log.info(' -> Status: '+repr(response))
        