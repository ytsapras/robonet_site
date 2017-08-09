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
        self.event_status = None
        self.event_pk = -1
        self.eventname_pk = -1
        self.got_eventname = False
        
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
                
    def get_field(self,log=None,debug=False):
        """Method to identify which ROME survey field the event falls within,
        based on a query by sky position. 
        Populates the field_id, field_pk and event_status attributes.  
        A negative field_pk indicates that the object falls outside the ROME 
        footprint. 
        """
        response = api_tools.query_field_id(config,{self.ra,self.dec})
        (self.field_id, self.field_pk) = response.split(' ')
        
        if debug==True and log!=None:
            log.info(' -> Identified field: '+str(self.field_id)+' '+\
            str(self.field_pk)+' '+str(self.ra)+' '+str(self.dec))
        if 'Outside' in id_field:
            self.event_status = 'NF'
        else:
            self.event_status= 'AC'
    
    def check_event_name_in_DB(self,log=None,debug=False):
        """Method to check whether the event name is already known to the DB.
        This method sets the eventname_pk attribute.  An index of -1 is returned
        if the event name is not yet in the DB."""
        
        params = {'name': self.name}
        self.eventname_pk = int(api_tools.submit_eventname_record(config,params))
    
    def check_event_name_assoc_event(self,log=None,debug=False):
        """Method to check whether an event name is already associated with 
        a specific event.
        This method sets the boolean got_eventname attribute. 
        False indicates that the eventname is not associated with the event.
        """
        
        params = {'event': self.event_pk,
                      'name': self.name}
        response = api_tools.check_eventname_assoc(config,params)
    
    def check_event_in_DB(self,log=None,debug=False):
        """Method to check whether the event is already known to the DB.
        This method sets the event_pk attribute, returning a value of -1 if the
        event is not yet present in the DB."""
        params = {'ev_ra': self.ra,
                  'ev_dec': self.dec
                  }
        self.event_pk = int(api_tools.query_event_by_coords(config,params))
    
    def sync_event_with_DB(self,config,last_updated,log=None,debug=False):
        """Method to sync the latest survey parameters with the database.
        
        Identifies which ROME field the event falls within
        Checks if event is known to the DB
        Checks if eventname is known to the DB
        Adds the event if not known
        Adds the eventname if not known
        Queries for most recent single-lens model parameters
        Updates the single-lens model parameters if necessary
        """
        
        self.get_field(log=log,debug=debug)
        
        # Get the discovery year of the event from the event name to avoid
        # it being autoset to the current year:
        year = str(self.name).split('-')[1]
        
        self.check_event_in_DB(log=log,debug=debug)
        if self.event_pk > 0:
            self.check_event_name_in_DB(log=log,debug=debug)
        
        if debug==True and log!=None:
            log.info(' -> Tried to add_event with output:')
            log.info(' -> '+str(event_status)+' '+str(ev_ra)+' '+str(ev_dec)+\
                        ' '+str(response))
        
        # Add_event doesn't ingest the EventName, so ensure that the eventname
        # is linked to the correct Event sky location:
        if debug==True and log!=None:
                log.info(' -> Checking event name in DB:')
        if event_status == True and 'OK' in response:
            event = Event.objects.filter(ev_ra=ev_ra).filter(ev_dec=ev_dec)[0]
            operator = Operator.objects.filter(name=self.origin)[0]
            params = {'event': event.pk,
                      'operator': operator.pk,
                      'name': self.name
                      }
            response = api_tools.submit_eventname_record(config,params)
            
            if debug==True and log!=None:
                log.info(' -> New event, added eventname with output '+str(response))
                
        elif event_status == False and 'exists' in response:
            event = query_db.get_event_by_position(ev_ra,ev_dec)
            if event != None:
                name_list = query_db.get_event_name_list(event.pk)
                name_str = utilities.combined_survey_name(name_list)
                if debug==True and log!=None:
                    log.info(' -> Current names for this event: '+name_str)
                    log.info(' -> Looking for name: '+str(self.name))
            else:
                message = 'ERROR: Event appears in DB but could not find it by position'
                get_errors.update_err('artemis_subscriber', message)
                if log!=None:
                    log.info(message)
                name_list = []
                
            if event != None and self.name not in name_list:
                operator = Operator.objects.filter(name=self.origin)[0]
                params = {'event': event.pk,
                      'operator': operator.pk,
                      'name': self.name
                      }
                response = api_tools.submit_eventname_record(config,params)
                if debug==True and log!=None:
                    log.info(' -> Added eventname for known event with output '+str(response))
            else:
                if debug==True and log!=None:
                    log.info(' -> Event name already known to DB')
        else:
            message = 'ERROR: Incomprehensible combination of event and names'
            get_errors.update_err('artemis_subscriber', message)
            if log!=None:
                log.info(message)
                
        # Confirm that both Event and EventName are properly registered:
        if log!=None:
            log.info(' -> Verifying event and names registered with DB:')
        event = Event.objects.filter(ev_ra=ev_ra).filter(ev_dec=ev_dec)[0]
        eventnames = EventName.objects.filter(event=event.id)
        if debug==True and log!=None:
            log.info(' -> Searched for event, found: '+str(event))
            eventname = ''
            for n in eventnames:
                eventname+=str(n)
            log.info(' -> Searched for event name, found: '+eventname)
        
        # Check that the current model parameters have been ingested and if
        # not, add them:
        last_model = query_db.get_last_single_model(event,modeler=self.modeler)
        if debug==True and log!=None:
            log.info(' -> Last model for event '+str(self.name)+': '+str(last_model))
        
        if last_model == None or self.last_updated == None or \
                self.last_updated > last_model.last_updated:
                    
            if debug==True and log!=None:
                log.info(' -> Attempting to add a single lens model with parameters:')
                log.info(str(self.name)+' '+str(self.t0)+' '+str(self.te)+\
                        str(self.u0)+' '+str(last_updated)+' '+str(self.modeler))
            params = {'event': event.pl,
                      'Tmax':self.t0,'e_Tmax':0.0,
                      'tau':self.te,'e_tau':0.0,
                      'umin':self.u0,'e_umin':0.0,
                      'modeler':self.modeler,
                      'last_updated':str(last_updated)
                      }
            
            response = api_tools.submit_singlemodel_record(config,params)
            
            if debug==True and log!=None:
                log.info(' -> Outcome of adding the single lens model:')
                log.info(str(response))
    
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
        
        FETCH EVENT INDEX
        
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
        