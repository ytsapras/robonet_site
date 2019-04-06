# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 18:50:24 2017

@author: rstreet
"""
import os
import sys
from local_conf import get_conf
robonet_site = get_conf('robonet_site')
sys.path.append(robonet_site)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'robonet_site.settings')
from django.core import management
from django.conf import settings
from django.utils import timezone
from django import setup
from datetime import datetime, timedelta
setup()

from rome_fields_dict import field_dict
from field_check import romecheck
import utilities
from events.models import ObsRequest, Tap, Event, SingleModel, SubObsRequest
from events.models import EventName, Image, Field, Operator, DataFile
from observation_classes import get_request_desc

class TapEvent():
    """Class describing the attributes of an event selected for REA 
    observations by TAP"""
    
    def __init__(self):
        self.pk = None
        self.event = None
        self.event_id = None
        self.names = None
        self.field = None
        self.ev_ra = None
        self.ev_dec = None
        self.tap_status = None
        self.priority = None
        self.tsamp = None
        self.texp = None
        self.nexp = None
        self.telclass = None
        self.omega = None
        self.passband = None
        self.ipp = None
    
    def summary(self):
        return str(self.pk)+' '+self.names + ' ' + str(self.event_id) + ' ' + \
            self.field.name + ' ' + str(self.priority) + ' ' + \
            str(self.tsamp) + ' ' + str(self.texp) + ' ' +\
            str(self.nexp) + ' ' + str(self.ipp)

def get_active_obs(log=None):
    """Function to extract a list of the currently-active observations 
    requests from the database"""
    
    now = timezone.now()
    qs = ObsRequest.objects.filter(
                    time_expire__gt = now,
                    timestamp__lte = now,
                    request_status='AC'
                    )
    
    if log != None:
        log.info('\n')
        log.info('Queried DB for list of active observations:')
        if qs.count() == 0:
            log.info('DB returned no currently-active observation requests')
        else:
            for q in qs:
                log.info(' '.join([q.grp_id, q.field.name,\
                            get_request_desc(q.request_type), \
                            'submitted=',q.timestamp.strftime('%Y-%m-%dT%H:%M:%S'), \
                            'expires=',q.time_expire.strftime('%Y-%m-%dT%H:%M:%S'),\
                            'status=',q.request_status]))
        log.info('\n')

    return qs

def get_old_active_obs(log=None):
    """Function to extract a QuerySet of observation requests that have
    exceeded their expiry date but still have the status set to 'AC'"""
    
    now = timezone.now()
    qs = ObsRequest.objects.filter(
                    time_expire__lte = now,
                    request_status='AC'
                    )
    
    if log != None:
        log.info('\n')
        log.info('Queried DB for list of out-of-date active observations:')
        if qs.count() == 0:
            log.info('DB returned no expired observations marked as active')
        else:
            for q in qs:
                log.info(' '.join([q.grp_id, q.field.name,\
                            get_request_desc(q.request_type), \
                            'submitted=',q.timestamp.strftime('%Y-%m-%dT%H:%M:%S'), \
                            'expires=',q.time_expire.strftime('%Y-%m-%dT%H:%M:%S'),\
                            'status=',q.request_status]))
        log.info('\n')

    return qs
    
def select_obs_by_date(criteria,log=None):
    """Function to extract a list of the currently-active observations 
    requests from the database
    
    Inputs:
        :param dict criteria: Dictionary of selection criteria where the
                            keys and value types match those of ObsRequest
                            objects
                            Currently required:
                            timestamp, time_expire and request_status
    
    Returns:
        :param QuerySet qs: QuerySet of matching ObsRequests
    """
    
    if 'request_status' in criteria.keys():
        
        qs = ObsRequest.objects.filter(
                        timestamp__gte = criteria['timestamp'],
                        time_expire__lte = criteria['time_expire'],
                        request_status= criteria['request_status'])
                        
    else:

        qs = ObsRequest.objects.filter(
                        timestamp__gte = criteria['timestamp'],
                        time_expire__lte = criteria['time_expire'])
                        
    if log != None:

        log.info('\n')
        log.info('Queried DB for list of active observations:')

        if qs.count() == 0:

            log.info('DB returned no currently-active observation requests')

        else:

            for q in qs:
                                
                log.info(' '.join([q.grp_id, q.field.name,\
                            get_request_desc(q.request_type), \
                            'submitted=',q.timestamp.strftime('%Y-%m-%dT%H:%M:%S'), \
                            'expires=',q.time_expire.strftime('%Y-%m-%dT%H:%M:%S'),\
                            'status=',q.request_status]))

        log.info('\n')
    
    return qs

    
def get_rea_targets(log=None):
    """Function to query the DB for a list of targets recommended for 
    observation under the REA strategy."""
    
    qs = Tap.objects.filter(omega__gte=6.0).order_by('timestamp').reverse()
    
    for q in qs:
        print q.event.ev_ra, q.tsamp,q.priority
    
    if log != None:
        log.info('\n')
        log.info('Queried DB for list of current REA targets:')
        for q in qs:
            log.info(' '.join([q.event.field.name,\
                        'priority=',q.priority, \
                        't_sample=',str(q.tsamp)]))
        log.info('\n')
                        
    return qs

def get_tap_list(log=None):
    """Function to query the DB and return the list of targets recommended 
    for REA-mode observations by TAP, and the details of those 
    observations"""
    
    tap_list = []
    qs = Event.objects.filter(status='MO')
    for q in qs:
        names = get_event_names(q.pk)
        name = ''
        for n in names:
            if len(name) == 0:
                name += n.name
            else:  
                name += '/' + n.name
        target = TapEvent()
        target.event_id = q.pk
        target.names = name
        target.field = q.field
        target.ev_ra = q.ev_ra
        target.ev_dec = q.ev_dec
        target.tap_status = q.status
        
        tap_entry = Tap.objects.filter(event=q.pk).order_by('timestamp').reverse()[0]
        target.pk = tap_entry.pk
        target.event = q
        target.priority = tap_entry.priority
        target.tsamp = float(tap_entry.tsamp)
        target.texp = float(tap_entry.texp)
        target.nexp = int(tap_entry.nexp)
        target.telclass = tap_entry.telclass+'0'
        target.omega = tap_entry.omega
        target.passband = tap_entry.passband
        target.ipp = float(tap_entry.ipp)
        tap_list.append(target)
        
    if log != None:
        log.info('\n')
        log.info('Queried DB for list of current TAP list:')
        for target in tap_list:
            log.info(target.summary())
        log.info('\n')
                        
    return tap_list

def target_field(ev_ra,ev_dec):
    """Function to identify the field a given target lies in"""
    

def get_last_single_model(event,modeler=None,log=None):
    """Function to return the last model submitted to the DB by the 
    modeler given
    Inputs:
        events    Event object
        modeler   String       Name of originator of model
    """
    
    if modeler==None:
        qs = SingleModel.objects.filter(event=event).order_by('last_updated').reverse()
    else:
        qs = SingleModel.objects.filter(
                                        event=event
                                        ).filter(
                                        modeler=modeler
                                        ).order_by('last_updated').reverse()
    
    try:    
        model = qs[0]
    except IndexError:
        model = None
        
    if log != None:
        log.info('\n')
        log.info('Queried DB for last single-lens model for this event:')
        log.info(' '.join([model.modeler,\
                        't_0='+str(model.Tmax),'t_E='+str(model.tau),\
                        'u_0='+str(model.umin)]))
        log.info('\n')
   
    return model

def get_last_datafile(event,log=None):
    """Function to return the last datafile submitted to the DB for a given 
    event
    
    Inputs:
        events    Event object
        log       Logger object
    """
    
    qs = DataFile.objects.filter(event=event).order_by('last_upd').reverse()
    
    try:    
        df = qs[0]
    except IndexError:
        df = None
        
    if log != None:
        log.info('\n')
        log.info('Queried DB for last datafile for this event:')
        log.info(' '.join(['HJD='+str(df.last_hjd),\
                        'i='+str(df.last_mag)]))
        log.info('\n')
   
    return df

def get_latest_tap_entry(event,log=None):
    """Function to extract the latest entry in the TAP table, if any,
    for a given event
    Inputs:
        events    Event object
        log       Logger object
    """
    
    qs = Tap.objects.filter(event=event).order_by('timestamp').reverse()
    
    if len(qs) == 0:
        entry = None
    else:
        entry = qs[0]
    
    if log != None:
        log.info('\n')
        log.info('Queried DB for last TAP entry for this event:')
        log.info(' '.join(['HJD='+str(entry.timestamp),\
                        'i='+str(entry.priority)]))
        log.info('\n')
    
    return entry
    
def get_event(event_pk):
    """Function to extract an event object from the DB based on its 
    primary key)
    Inputs:
            event_pk    int    Primary key of known event in DB
    """
    
    qs = Event.objects.get(pk=event_pk)
    return qs

def get_event_by_name(event_name):
    """Function to extract an event object from the DB based on any of its 
    assigned names
    Inputs:
            event_name  str   Full-length name e.g. OGLE-2017-BLG-1234
    """
    qs_name = EventName.objects.filter(name=event_name)
    if len(qs_name) == 0:
        return None, 'Event name not in DB'
    else:
        event = Event.objects.get(pk=qs_name[0].event_id)
        return event, 'OK'

def get_event_names(event_id):
    """Function to extract the names of a target, given the event ID number
    Returns a Django QuerySet"""
    
    qs = EventName.objects.filter(event_id=event_id)
    return qs

def get_event_by_params(params):
    """Function to extract a set of events matching all the parameters given"""
    
    search_params = {}
    
    if params['anomaly_rank'] != None:
        search_params['anomaly_rank'] = params['anomaly_rank']
    
    if params['year'] != None:
        search_params['year'] = params['year']
    
    if 'All' not in params['field']:
        qs = Field.objects.filter(name=params['field'])
        search_params['field'] = qs[0]
    
    if 'ALL' not in params['operator']:
        qs = Operator.objects.filter(name=params['operator'])
        search_params['operator'] = qs[0]
        
    if 'ANY' not  in params['status']:
        search_params['status'] = params['status']
    
    if params['ibase_min'] != None and params['ibase_max'] != None:
        search_params['ibase__gte'] = params['ibase_min']
        search_params['ibase__lte'] = params['ibase_max']
    
    qs = Event.objects.filter(**search_params)
    
    return qs
    
def get_event_name_list(event_id):
    """Function to extract the names of a target, given the event ID number
    Returns a list of the name strings"""
    
    names = []
    qs = EventName.objects.filter(event_id=event_id)
    for q in qs:
        names.append(q.name)
    
    return names

def get_coords_in_degrees(ra,dec):
    
    if ':' in str(ra):
        ra_deg, dec_deg = utilities.sex2decdeg(ra, dec)
    else:
        ra_deg = ra
        dec_deg = dec

    return ra_deg, dec_deg

def get_event_field_id(ra_str,dec_str):
    """Function to identify which ROMEREA field the event lies in"""
    
    (ev_ra_deg, ev_dec_deg) = get_coords_in_degrees(ra_str,dec_str)
    
    (id_field, rate) = romecheck(ev_ra_deg, ev_dec_deg)

    if id_field == -1:
        id_field = 'Outside ROMEREA footprint'
    else:
        id_field = sorted(field_dict.keys())[id_field]
    return id_field, rate

def get_event_by_position(ra_str,dec_str):
    """Function to find an event by its sky coordinates in sexigesimal format.
    Returns first event from resulting QuerySet.    
    """
    
    try:
        event = Event.objects.filter(
                            ev_ra__contains=ra_str, 
                            ev_dec__contains=dec_str
                            )[0]
        
    except IndexError:
        event = None

    return event

def get_events_within_radius(ra_str, dec_str, radius):
    """Function to find a list of all events within a specified radius less than
    1 arcmin.  Related to update_db_2's check_coords function. 
    Inputs:
        ra_str   str    RA in sexagesimal format
        dec_str  str    Dec in sexagesimal format
        radius   float  Search radius in decimal arcsec < 60 arcsec
    Outputs:
        events_list list  Event objects
    Events_list is returned sorted, with the nearest match first
    """

    (ra1,dec1) = utilities.sex2decdeg(ra_str,dec_str)
    radius = radius / 3600.0

    events_list = []
    separations = []
    
    qs_events = Event.objects.filter(ev_ra__contains=ra_str[0:5]).filter(ev_dec__contains=dec_str[0:5])
    for event in qs_events:
        (ra2, dec2) = utilities.sex2decdeg(event.ev_ra,event.ev_dec)
        sep = utilities.separation_two_points((ra1,dec2),(ra2,dec2))
        if sep <= radius:
            events_list.append(event)
            separations.append(sep)
    if len(events_list) > 1:
        (separations, events_list) = zip(*sorted(zip(separations,events_list)))
    
    return events_list

def get_events_box_search(params):
    """Function to find a list of all events within a specified radius less than
    1 arcmin.  Related to update_db_2's check_coords function. 
    Inputs in params dictionary:
        ra_centre   float    RA of cone centre
        dec_centre  float    Dec of cone centre
        delta_ra   float  Search height in RA, decimal arcsec < 60 arcsec
        delta_dec   float  Search height in Dec, decimal arcsec < 60 arcsec
    Outputs:
        events_list list  Event objects
    Events_list is returned sorted, with the nearest match first
    """

    events_list = []
    separations = []
    
    events = Event.objects.filter(ra__gte=params['ra_min'],
                                     ra__lte=params['ra_max'],
                                     dec__gte=params['dec_min'],
                                     dec__lte=params['dec_max'])
    
    return events

def get_field_containing_coordinates(params):
    """DB-enabled equivalent to field_check.romecheck; function to check whether
    a given set of coordinates lies within the ROME survey fields"""
    
    field_list = Field.objects.all()
    
    lhalf = 0.220833333333
    
    for f in field_list:
        if f.field_ra_decimal != None and f.field_dec_decimal != None:
            if params['ra'] < float(f.field_ra_decimal) + lhalf and\
               params['ra'] > float(f.field_ra_decimal) - lhalf and\
               params['dec'] < float(f.field_dec_decimal) + lhalf and\
               params['dec'] > float(f.field_dec_decimal) - lhalf:
                   
                   return f.name
               
    return 'Outside ROME footprint'
    
def combine_event_names(qs_event_names):
    """Function to return the combined name of an event discovered by multiple
    surveys.
    Input:
        qs_event_names  QuerySet   EventName objects
    Output:
        combined_name   string     Combined name string
    """
    
    name_list = []
    for name in qs_event_names:
        name_list.append(name.name)
    combined_name = utilities.combined_survey_name(name_list)
    return combined_name
    
def get_image_rejection_statistics(date_start=None,date_end=None):
    """Function to query the DB for the reasons why images were accepted or
    rejected by reception.
    All images will be returned unless start and end date ranges are given.
    
    Currently has a workaround for the multiply ingested images.
    """
    
    if date_start == None and date_end == None:
        image_list = Image.objects.all()
    elif date_start !=None and date_end == None:
        image_list = Image.objects.filter(date_obs__gte=date_start)
    elif date_start == None and date_end !=None:
        image_list = Image.objects.filter(date_obs__lte=date_end)
    else:
        image_list = Image.objects.filter(date_obs__gte=date_start, 
                                   date_obs__lte=date_end)
    checked_images = []
    
    stats = {'Accepted': 0, 'Total number of images': len(image_list)}
    for image in image_list:
        if image.image_name not in checked_images:
            qs = Image.objects.filter(image_name=image.image_name).order_by('timestamp').reverse()
            recent_entry = qs[0]
            if len(recent_entry.quality) == 0:
                stats['Accepted'] = stats['Accepted'] + 1
            else:
                keys = recent_entry.quality.split(' ; ')
                for k in keys:
                    if k in stats.keys():
                        stats[k] = stats[k] + 1
                    else:
                        stats[k] = 1
            checked_images.append(image.image_name)
    stats['Total number of images'] = len(checked_images)
    
    return stats

def check_image_in_db(image_name):
    """Function to check whether an image has been ingested into the database.
    Input:
        image_name    str    Name of image file without directory path
    Outputs:
        present       Bool   Status flag indicating whether the image is 
                              recorded in the DB
    """
    
    qs = Image.objects.filter(image_name=image_name)
    if len(qs) > 0:
        return True
    else:
        return False

def get_subrequests_for_obsrequest(obs_grp_id):
    """Function to extract a list of SubObsRequests for an ObsRequest, 
    given the Group ID of the ObsRequest."""
    
    qs = SubObsRequest.objects.filter(grp_id = obs_grp_id)
    
    return qs

if __name__ == '__main__':
    stats = get_image_rejection_statistics()
    print stats