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
from . import update_db_2
from . import field_check
from . import utilities
from . import query_db
from . import get_errors
from astropy.coordinates import SkyCoord

from . import local_conf
robonet_site = local_conf.get_conf('robonet_site')
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


    def sync_event_with_DB(self,last_updated,log=None,debug=False):
        '''Method to sync the latest survey parameters with the database.'''

        # Find out which sky region the target falls into:
        (id_field,rate) = query_db.get_event_field_id(self.ra,self.dec)
        if debug==True and log!=None:
            log.info(' -> Identified field: '+str(id_field)+' '+\
                            str(self.ra)+' '+str(self.dec))
        if 'Outside' in id_field:
            event_status = 'NF'
        else:
            event_status= 'AC'

        # Get the discovery year of the event from the event name to avoid
        # it being autoset to the current year:
        year = str(self.name).split('-')[1]

        # Add the event to the database - returns False if already present
        (ra, dec) = utilities.sex2decdeg(self.ra,self.dec)
        (event_status, ev_ra, ev_dec,response) = update_db_2.add_event(id_field, \
                                                    self.origin, \
                                                    self.ra,self.dec,\
                                                    status=event_status,\
                                                    year=year,
                                                    ibase=self.i0)
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
            (status, response) = update_db_2.add_event_name(event=event,\
                                                            operator=operator,\
                                                            name=self.name)
            if debug==True and log!=None:
                log.info(' -> New event, added eventname with output '+str(status)+' '+str(response))

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
                (status, response) = update_db_2.add_event_name(event=event,\
                                                            operator=operator,\
                                                            name=self.name)
                if debug==True and log!=None:
                    log.info(' -> Added eventname for known event with output '+str(status)+' '+str(response))
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

            (model_status,response) = update_db_2.add_single_lens(self.name, \
                            self.t0, self.te, self.u0, last_updated,
                            modeler=self.modeler)

            if debug==True and log!=None:
                log.info(' -> Outcome of adding the single lens model:')
                log.info(str(model_status)+' '+str(response))

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
        (status,message) = update_db_2.add_datafile(self.event_name,self.data_file,
                                            self.last_upd, self.last_hjd,
                                            self.last_mag,self.tel,
                                            self.ndata, inst=self.instrument,
                                            filt=self.filter,
                                            baseline=self.baseline,g=self.g)
        if log!=None:
            log.info(' -> Status: '+repr(status)+', '+message)
