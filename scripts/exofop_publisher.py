# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 18:03:54 2016

@author: rstreet
"""

######################################################################################################
#                                   EXOFOP_PUBLISHER
#
# Script to provide a live datafeed of microlensing events within the K2C9 superstamp to ExoFOP
######################################################################################################

from os import path, remove
from sys import argv, exit
import config_parser
import glob
import artemis_subscriber
import rtmodel_subscriber
import pylima_subscriber
import survey_data_utilities
from astropy.time import Time
import numpy as np
import utilities
import k2_footprint_class
import event_classes
import log_utilities
import logging
from commands import getstatusoutput
import ftplib
from shutil import copy
import email_harvester

def exofop_publisher():
    """
    Driver function to provide a live datafeed of microlensing events 
    within the K2C9 superstamp to ExoFOP
    """
    config_file_path = path.join(path.expanduser('~'),
                                 '.robonet_site', 'exofop_publish.xml')
    config = config_parser.read_config( config_file_path )
    
    log = log_utilities.start_day_log( config, __name__, console=False )
    log.info( 'Read script configuration\n' )
    
    # Check for lock file to prevent multiple instances:
    respect_locks = [ config['lock_file'] ]
    utilities.lock( config, 'check', respect_locks, log )
    utilities.lock( config, 'lock', respect_locks, log )
    
    # Remove the READY file from the transfer machine to stop IPAC 
    # transfering data while the script is running. 
    ready_file( config, 'remove' )
    log.info( 'Removed the transfer READY file' )
    key_list = ['ogle_ra', 'ogle_dec']
    
    # Read back the master list of all events known to date:
    known_events = get_known_events( config )
    n_events = len(known_events['master_index'])
    log.info( 'Read list of ' + str( n_events ) + ' known events' )

    # Read list of event alert dates:
    event_alerts = email_harvester.harvest_events_from_email( config['log_directory'] )
    log.info( 'Read/harvested event alert timestamps' )
    
    # Read in lists of previously-identified events so that we don't
    # have to repeat time-consuming calculations later except where necessary:
    false_positives = get_false_positives( config )    
    known_duplicates = get_duplicate_events_list( config, log )
    
    # Load TAP output to provide the prioritization data:
    tap_data = load_tap_output( config, log )    

    # Read in the information on the K2 campaign:
    k2_campaign = k2_footprint_class.K2Footprint( config, log=log )
    
    # Data are provided by combining datastreams from the providing surveys + 
    # ARTEMiS, RTModel.  First step is to read in a list of the event parameters  
    # from all these providers and compare to ensure the list is up to date.  
    # Produce master event dictionary events, but only include
    # those events found within the K2C9 superstamp.
    (artemis_events, artemis_renamed) = load_artemis_event_data( config, log )
    rtmodels = rtmodel_subscriber.rtmodel_subscriber(log=log, \
                                                    renamed=artemis_renamed)
    pylima_data = pylima_subscriber.load_pylima_output( config, log=log, \
                                                    renamed=artemis_renamed )
    survey_events = load_survey_event_data( config, known_duplicates, \
                                                event_alerts, log )
    if 'MOA-2016-BLG-205' in survey_events.keys():
        log.info( 'Got MOA-2016-BLG-205')
    else:
        log.info( 'Missing MOA-2016-BLG-205 from survey data')
        
    update_known_duplicates( config, known_duplicates )
    
    # Select those events which are in the K2 footprint
    # Combine all available data on them
    known_events = \
            combine_K2C9_event_feed( known_events, false_positives, \
                                        artemis_events, survey_events, \
                                            rtmodels, tap_data, pylima_data, log )
    
    # Identify which events are within the K2 campaign footprint & dates:
    known_events = targets_for_k2_campaign(config, known_events, k2_campaign, log)
    
    # Assign K2C9 identifiers to any events within the footprint which
    # do not yet have them:
    known_events = assign_identifiers( known_events )    
    
    # Extract findercharts for K2C9 objects:
    get_finder_charts( config, known_events, log )
    
    # Now output the combined information stream in the format agreed on for 
    # the ExoFOP transfer
    generate_exofop_output( config, known_events, artemis_renamed, log )
    
    # Generate K2C9 event summary table:
    generate_K2C9_events_table( config, known_events, log )
    
    # Update the master list of known events, and those within the K2C9 footprint:
    xsuperstamp_events = update_known_events( config, known_events, log )
    
    # Plot locations of events:
    log.info('Plotting event locations...')
    plotname = path.join( config['log_directory'], 'k2_events_map.png' )
    k2_campaign.plot_footprint( plot_file=plotname, \
                                targets=known_events['master_index'], iplt=1 )
    log.info('Plotted K2C9 event locations')
    
    plotname = path.join( config['log_directory'], 
                                 'k2_events_outside_superstamp_map.png' )
    plot_title = 'Events selected for K2 outside the superstamp'
    k2_campaign.load_xsuperstamp_targets( config )
    k2_campaign.plot_footprint( plot_file=plotname, \
                                targets=k2_campaign.xsuperstamp_targets, \
                                label_xsuper_targets=True,\
                                iplt=2, \
                                title=plot_title )
    log.info('Plotted event locations outside superstamp')
    
    # Sync data for transfer to IPAC with transfer location:
    sync_data_for_transfer( config, log )  
    
    utilities.lock( config, 'unlock', respect_locks, log )
    log_utilities.end_day_log( log )
    
###############################################################################
# FUNCTIONS
        
def get_known_events( config ):
    """Function to load the list of known events within the K2 footprint.
    File format: # indicates comment line
    K2C9identifier OGLE_name MOA_name KMT_name
    All name entries may individually contain None entries, but one of
    them must be a valid, long-hand format name.
    """
    
    def parse_boolean( value ):
        """Entries may be Boolean or Unknown"""
        
        if str( value ).lower() == 'unknown':
            return value
        elif 'true' in str( value ).lower():
            return True
        elif 'false' in str( value ).lower():
            return False
        else:
            return 'Unknown'
            
    events_file = path.join( config['log_directory'], \
            config['master_events_list'] )
    
    if path.isfile( events_file ) == False:
        print 'Error: Missing events file, ' + events_file
        exit()
        
    file_lines = open( events_file, 'r' ).readlines()
    key_list = [ 'identifier', 'ogle_name', 'moa_name', \
                'in_footprint', 'in_superstamp', 'during_campaign' ]
    known_events= {'identifiers': {}, \
                   'master_index': {},\
                   'ogle': {}, \
                   'moa': {}, \
                   'kmt': {},
                   'max_index': 0
                   }
    for line in file_lines:
        if len(line) > 0 and line.lstrip()[0:1] != '#':
            entries = line.split()
            survey_names = {}
            
            if str(entries[5]).lower() != 'none':
                survey_names['ogle'] = str( entries[5] )
            if str(entries[6]).lower() != 'none':
                survey_names['moa'] = str( entries[6] )
            if str(entries[7]).lower() != 'none':
                survey_names['kmt'] = str( entries[7] )
            
            event_recog = False
            for origin, ename in survey_names.items():
                if ename in known_events[origin].keys():
                    event_recog = True
            
            if event_recog == False:
                event = event_classes.K2C9Event()
                event.master_index = int(entries[0])
                if str(entries[1]).lower() == 'none':
                    event.identifier = None
                else:
                    event.identifier = entries[1]
                event.in_footprint = parse_boolean(entries[2])
                event.in_superstamp = parse_boolean(entries[3])
                event.during_campaign = parse_boolean(entries[4])
                event.recommended_status = str(entries[8]).upper()
                event.status = 'UPDATED'
                
                for origin, ename in survey_names.items():
                    event.set_event_name( {'name': ename} )
                    known_events[origin][ename] = event.master_index
                    
                known_events['identifiers'][event.master_index] = event.identifier
                known_events['master_index'][event.master_index] = event
                if str(event.identifier).lower() != 'none':
                    idx = int(str(event.identifier).replace('K2C9-R-',''))
                    if known_events['max_index'] == None:
                        known_events['max_index'] = idx
                    else:
                        if idx > known_events['max_index']:
                            known_events['max_index'] = idx
    
    return known_events

def get_false_positives( config ):
    """Function to load the list of known false positive alerts"""
    
    file_path = path.join( config['log_directory'], 'known_false_positives' )
    file_lines = open( file_path, 'r' ).readlines()
    false_positives = []
    for line in file_lines:
        if line.lstrip()[0:1] != '#':
            false_positives.append( line.replace('\n', '') )
    return false_positives
    
def get_duplicate_events_list( config, log ):
    """Function to read the list of known duplicate events. 
    File format:
        event_name  action  substitute_name
            where action = { no_duplicate, keep_existing_event, substitute }
            and substitute_name = { None, event_name }
    """
    
    known_duplicates = {}
    file_path = path.join( config['log_directory'], 'known_duplicates' )
    if path.isfile(file_path) == True:
        file_lines = open( file_path, 'r' ).readlines()
        for line in file_lines:
            entries = line.replace('\n','').split()
            event_id = entries[0]
            action = entries[1]
            substitute = entries[2]
            known_duplicates[event_id] = { 'action': action, 'substitute': substitute }
        log.info('Read list of ' + str(len(known_duplicates)) + ' known duplicate events' )
    
    return known_duplicates

def update_known_duplicates( config, known_duplicates ):
    """Function to output the updated list of known event duplicates"""
    file_path = path.join( config['log_directory'], 'known_duplicates' )
    fileobj = open(file_path, 'w')
    for event_id, params in known_duplicates.items():
        output = event_id + ' ' + params['action'] + ' ' + \
                                            params['substitute'] + '\n'
        fileobj.write(output)
    fileobj.close()
    
def update_known_events( config, known_events, log ):
    """Function to output a cross-identified list of all event identifiers"""
    
    log.info('Identifying events within the footprint and outside the superstamp')
    
    events_file = path.join( config['log_directory'], \
                            config['master_events_list'] )
    
    fileobj = open( events_file, 'w' )
    fileobj.write('# Event_index   K2C9_ID   In_footprint  In_superstamp  During_campaign OGLE_ID MOA_ID KMTNET_ID RECOMMENDED_STATUS\n' )
    for master_index, event in known_events['master_index'].items():
        line = str(master_index) + ' ' + str(event.identifier) + ' ' + \
                str(event.in_footprint) + ' ' + str(event.in_superstamp) + ' '\
                + str(event.during_campaign) + ' ' + str(event.ogle_name) + \
                ' ' + str(event.moa_name) + ' ' + str(event.kmt_name) + \
                ' ' + str(event.artemis_status).upper() + '\n'
        fileobj.write( line )
    fileobj.close()

    k2_events_file = path.join( config['log_directory'], \
                            config['events_list'] )
    fileobj = open( k2_events_file, 'w' )
    fileobj.write( '# K2C9_ID OGLE_ID MOA_ID KMTNet_ID   In_footprint  In_superstamp  During_campaign \n' )
    xsuperstamp_events = {}
    for event_id, event in known_events['master_index'].items():
        if event.in_footprint == True and event.during_campaign == True:        
            line = str(event.identifier) + ' ' + str(event.ogle_name) + \
                ' ' + str(event.moa_name) + ' ' + str(event.kmt_name) + ' ' + \
                str(event.in_footprint) + ' ' + str(event.in_superstamp) + ' '\
                + str(event.during_campaign) + '\n'
            fileobj.write( line )
            if event.in_superstamp == False:
                xsuperstamp_events[ event_id ] = event
                
    fileobj.close()
    log.info('-> Identified ' + str(len(xsuperstamp_events)) + \
                ' events outside the superstamp' )
    
    return xsuperstamp_events    

def assign_identifiers( known_events ):
    """Function to assign K2C9 identifiers to events that are within the 
    footprint and Campaign duration"""
    
    for event_id, event in known_events['master_index'].items():
        if event.in_footprint == True and event.during_campaign == True\
            and str(event.identifier).lower() == 'none':
            ( event.identifier, known_events ) = set_identifier( known_events )
            known_events['master_index'][event_id] = event
    return known_events
    
def load_artemis_event_data( config, log ):
    """Function to load the full list of events known to ARTEMiS."""

    log.info('Loading ARTEMiS event data')    
    
    # List of keys in a K2C9Event which should be prefixed with
    # Signalmen:
    prefix_keys = [ 'a0', 't0', 'sig_t0', 'te', 'sig_te', 'u0', 'sig_u0', \
                    'anomaly' ]
    
    # Load list of events renamed by Martin because they are from the
    # previous year:
    artemis_renamed = {}
    file_path = path.join( config['log_directory'], 'artemis_renamed_events')
    if path.isfile(file_path) == True:
        file_lines = open(file_path,'r').readlines()
        for line in file_lines:
            (key,value) = line.split()
            artemis_renamed[key] = value
    
    # Make a dictionary of all events known to ARTEMiS based on the 
    # ASCII-format model files in its 'models' directory.
    search_str = path.join( config['models_local_location'], \
            '?B1[5-6]????.model' )
    model_file_list = glob.glob( search_str )
    
    artemis_events = {}
    for model_file in model_file_list:
        params = artemis_subscriber.read_artemis_model_file( model_file )
        params = artemis_subscriber.check_anomaly_status(config['internal_data_local_location'], \
                                        params, log=log)
        if params['long_name'] in artemis_renamed.keys():
            params['long_name'] = artemis_renamed[params['long_name']]
        params = set_key_names( params, prefix_keys, 'signalmen' )
        if len( params ) > 0:
            event = event_classes.K2C9Event()
            event.set_params( params )
            event.set_event_name( params )
            artemis_events[ params['long_name'] ] = event
    log.info(' -> Loaded data for ' + str(len(artemis_events)))
    
    return artemis_events, artemis_renamed

def load_survey_event_data( config, known_duplicates, event_alerts, log ):
    """Method to load the parameters of all events known from the surveys.
    """
    
    log.info('Loading survey event data')
    
    ogle_data = survey_data_utilities.read_ogle_param_files( config )
    moa_data = survey_data_utilities.read_moa_param_files( config )
    
    # Combine the data from both sets of events into a single 
    # dictionary of K2C9Event objects.
    # Cross-match by position to identify objects detected by multiple surveys
    
    # Start by working through OGLE events since this is usually a superset
    # of those detected by the other surveys:
    survey_events = {}
    prefix_keys = [ 'name', 'survey_id', 'a0', 't0', 'sig_t0', 'te', \
                'sig_te', 'u0', 'sig_u0', 'ra', 'dec', 'i0' ]
    for ogle_id, lens in ogle_data.lenses.items():
            
        # Check for duplicated events under different names. 
        # Note: this filter removes the later event
        (duplicate_event, status, known_duplicates) = \
                    filter_duplicate_events( survey_events, lens, known_duplicates )
        
        if status in ['substitute', 'keep_existing_event']:
            log.info('DUPLICATE EVENT')
            log.info('New lens ' + ogle_id + ' RA,Dec:' + str(lens.ra) + \
                                ' ' + str(lens.dec) + ' matches position of ' + \
                                duplicate_event + ' action: ' + status)
            
        if status in [ 'no_duplicate', 'substitute' ]:
            event = event_classes.K2C9Event()
            params = lens.get_params()
            params = set_key_names( params, prefix_keys, 'ogle' )
            event.set_event_name( {'name': ogle_id} )
            event.set_params( params )
            event.classification = lens.classification
            event.set_ogle_url( config )
            
            if ogle_id in event_alerts:
                event.ogle_alert = event_alerts[ogle_id].strftime("%Y-%m-%dT%H:%M:%S")
                position = ( event.ogle_ra, event.ogle_dec )
                event.ogle_alert_hjd = utilities.ts_to_hjd( event.ogle_alert, position )
            survey_events[ event.ogle_name ] = event
            
    ogle_id_list = survey_events.keys()
    ogle_id_list.sort()
    
    # Now work through MOA events, adding them to the dictionary:
    for moa_id, lens in moa_data.lenses.items():
        
        coords1 = ( lens.ra, lens.dec )
        
        # If this event matches one already in the dictionary, 
        # add the MOA parameters to the K2C9Event instance:
        i = 0
        match = False
        while i < len( ogle_id_list ) and match == False:
            ogle_event = survey_events[ ogle_id_list[i] ]
            coords2 = ( ogle_event.ogle_ra, ogle_event.ogle_dec )
            match = match_events_by_position( coords1, coords2 )

            if match == True:
                #print 'Matched events: ',ogle_event.ogle_name, lens.name
                moa_lens_params = lens.get_params()
                moa_lens_params = set_key_names( moa_lens_params, prefix_keys, 'moa' )
                #print moa_lens_params
                ogle_event.set_params( moa_lens_params )
                ogle_event.set_moa_url( config )
                survey_events[ ogle_id_list[i] ] = ogle_event
                
                if moa_id in event_alerts:
                    ogle_event.moa_alert = event_alerts[moa_id].strftime("%Y-%m-%dT%H:%M:%S")
                    position = ( ogle_event.moa_ra, ogle_event.moa_dec )
                    ogle_event.moa_alert_hjd = utilities.ts_to_hjd( ogle_event.moa_alert, position )
                survey_events[ moa_lens_params['moa_name'] ] = ogle_event
                
            i = i + 1
            
        # If no match to an existing OGLE event is found, add this
        # event to the dictionary as a MOA event. 
        if match == False:

            # Check for duplicate MOA event:
            ( duplicate_event, status, known_duplicates ) = \
                filter_duplicate_events( survey_events, lens, known_duplicates )
        
            if duplicate_event != None and status == 'substitute':
                log.info('DUPLICATE EVENT')
                log.info('New lens ' + moa_id + ' RA,Dec:' + str(lens.ra) + \
                                ' ' + str(lens.dec) + ' matches position of ' + \
                                duplicate_event + ' action: ' + status)
                
            if status in [ 'no_duplicate', 'substitute' ]: 
                event = event_classes.K2C9Event()
                moa_params = lens.get_params()
                moa_params = set_key_names( moa_params, prefix_keys, 'moa' )
                event.set_event_name( {'name': moa_id} )
                event.set_params( moa_params )
                event.classification = lens.classification
                event.set_moa_url( config )
                
                if moa_id in event_alerts:
                    event.moa_alert = event_alerts[moa_id].strftime("%Y-%m-%dT%H:%M:%S")
                    position = ( event.moa_ra, event.moa_dec )
                    event.moa_alert_hjd = utilities.ts_to_hjd( event.moa_alert, position )

                survey_events[ event.moa_name ] = event

    log.info(' -> ' + str(len(survey_events)) + ' events from surveys')
    
    return survey_events
    
    
def match_events_by_position( coords1, coords2, debug=False ):
    """Function to match events by location given tuples of their
    coordinates from two data providers.
    If the coordinates fall within 0.5arcsec, True is returned, 
    otherwise False
    """
    
    match = False
    threshold = 2.5     # arcsec
    
    try: 
        ra1 = utilities.sexig2dec(coords1[0])
        ra1 = ra1 * 15.0
    except AttributeError:
        ra1 = coords1[0]
    try:
        dec1 = utilities.sexig2dec(coords1[1])
    except AttributeError:
        dec1 = coords1[1]
        
    try:
        ra2 = utilities.sexig2dec(coords2[0])
        ra2 = ra2 * 15.0
    except AttributeError:
        ra2 = coords2[0]
    try:
        dec2 = utilities.sexig2dec(coords2[1])
    except AttributeError:
        dec2 = coords2[1]
    sep = utilities.separation_two_points( (ra1,dec1), (ra2,dec2) )
    
    if sep < ( threshold / 3600.0):
        match = True

    if debug == True:
        print 'MATCH: ',sep, threshold, match
    
    return match

def filter_duplicate_events( survey_events, new_lens, known_duplicates ):
    """Function to filter out duplicate events identified multiple times by
    the same survey.  
    Possible return states:
        No duplicate event - new event should be added to the events dictionary
        Duplicate event:
            Existing event was discovered earlier - new event should be ignored
            Existing event discovered later - should be substituted for new event
    
    Return states are indicated with two criteria:
    duplicate_event    { None or event_name }
    status             { 'no_duplicate', 'keep_existing_event', 'substitute' }
    
    """
    
    # First check to see if the event has already been filtered:
    if new_lens.name in known_duplicates.keys():
        status = known_duplicates[new_lens.name]['action']
        duplicate_event = known_duplicates[new_lens.name]['substitute']
    
    # If not, match events by location.  If this is the case, add
    # the new event to the known_duplicates dictionary:
    else:
        new_origin = str(new_lens.name).split('-')[0].lower()
        coords1 = ( new_lens.ra, new_lens.dec )
        new_year = float(str(new_lens.name).split('-')[1])
        new_number = float(str(new_lens.name).split('-')[-1])
        duplicate_event = None
        status = 'no_duplicate'
        
        for event_name, event in survey_events.items():
            origin = event.get_event_origin()
            
            if origin == new_origin:
                coords2 = event.get_location()
                match = match_events_by_position( coords1, coords2 )
                
                if match == True:
                    match_year = float(event_name.split('-')[1])
                    match_number = float(event_name.split('-')[-1])
                    duplicate_event = event_name
                    
                    if match_year > new_year:
                        status = 'substitute'
                    
                    elif match_year < new_year:
                        status = 'keep_existing_event'
                        
                    else:
                        if match_number > new_number:
                            status = 'substitute'
                        else:
                            status = 'keep_existing_event'
        known_duplicates[new_lens.name] = { 'action': status, \
                                            'substitute': str(duplicate_event)}
                                            
    return duplicate_event, status, known_duplicates
    
def load_tap_output( configs, log ):
    """Function to load TAP prioritization output from the online table."""

    tap_data = { }
    
    # Read the TAP output website:
    (tap_output,msg) = utilities.get_http_page( configs['tap_url'] )
    
    for line in tap_output.split('\n \n \n'):
        if len(line) > 0: 
            entry = line.split('\n')
            if 'MOA' in entry[0][0:20] or 'OGLE' in entry[0][0:20]:
                event_name = str(entry[0]).lstrip().rstrip()
                priority = str(entry[7]).lstrip().rstrip().replace('\t','')
                omega_s_now = entry[10]
                sig_omega_s_now = entry[11]
                omega_s_peak = entry[12]
                
                if 'MOA' in event_name:
                    event_year = str(event_name).split('-')[1]
                    event_number = str(event_name).split('-')[-1]
                    if len(event_number) == 4 and event_number[0:1] == '0':
                        event_name = 'MOA-' + event_year + '-BLG-' + event_number[1:]
                        
                event_number = float(event_name.split('-')[-1])
                if event_number > 3000.0:
                    aka_list = str(entry[4]).split(',')
                    for item in aka_list:
                        if 'OB15' in item:
                            event_number = item[4:]
                            event_name = 'OGLE-2015-BLG-' + event_number
                            #print 'EVENT NAME -> ',event_name
                
                tap_data[event_name] = { 'priority': entry[7], \
                                     'omega_s_now': float(entry[10]), \
                                     'sig_omega_s_now': float(entry[11]), \
                                     'omega_s_peak': float(entry[12])
                                     }
    log.info('Loaded TAP data for all events')
    
    return tap_data
    
def combine_K2C9_event_feed( known_events, false_positives, \
                                artemis_events, survey_events, \
                                    rtmodels, tap_data, pylima_data, log ):
    """Function to produce a dictionary of just those events identified
    within the superstamp of K2C9."""
    
    prefix_keys = [ 'a0', 't0', 'sig_t0', 'te', 'sig_te', 'u0', 'sig_u0', \
                'ra', 'dec' ]
    
    log.info('Combining data on all known events')
    log.info(' -> Combining survey data')
    
    # Review all events reported by the surveys:
    for event_name, event in survey_events.items():
        
        origin = str(event_name.split('-')[0]).lower()
        if event_name == 'MOA-2016-BLG-205':
            log.info( 'Combining data on MOA-2016-BLG-205' )
        # Exclude known false positives:
        if event_name not in false_positives:
            
            # Previously known events (K2C9Events):
            # THIS NEEDS TO CHECK FOR EVENTS UNDER BOTH SURVEYS
            if event_name in known_events[origin].keys():
                event.master_index = known_events[origin][event_name]
                existing_event = known_events['master_index'][ event.master_index ]
                event.in_superstamp = existing_event.in_superstamp
                event.in_footprint = existing_event.in_footprint
                event.during_campaign = existing_event.during_campaign
                
                # Check to see if it has a K2 index:
                if event.master_index in known_events['identifiers'].keys():
                    event.identifier = known_events['identifiers'][event.master_index]
                
                # Ensure event has the up to date parameters from the survey:
                
                event.status = 'UPDATED'
                
            # New events:
            else:
                
                # Generate a new master_index and add to the known_events index:
                if len(known_events['master_index'].keys()) > 0:                
                    event.master_index = np.array(known_events['master_index'].keys()).max() + 1
                else:
                    event.master_index = 1
                event.status = 'NEW'
                known_events[origin][event_name] = event.master_index

            
            # Always update the known_events with the most up to date event data
            known_events['master_index'][ event.master_index ] = event
    
    
    # Combine the complete listing of events with ARTEMiS', TAP's, PyLIMA's and  
    # RTmodel's output.  Also now set the official event name and artemis status, 
    # since we have combined all the data from all surveys and RTmodel:
    log.info(' -> Combining data from ARTEMiS, TAP and RTModel')
    
    sig_keys = [ 'signalmen_a0', 'signalmen_t0', 'signalmen_sig_t0', \
                 'signalmen_te', 'signalmen_sig_te', 'signalmen_u0', \
                 'signalmen_sig_u0', 'signalmen_anomaly', 'ndata' ]

    for event_id, event in known_events['master_index'].items():
        
        event_name = event.get_event_name()
        
        if event_name in tap_data.keys():
            tap = tap_data[event_name]
            event.tap_priority = tap['priority']
            event.omega_s_now = tap['omega_s_now']
            event.sig_omega_s_now = tap['sig_omega_s_now']
            event.omega_s_peak = tap['omega_s_peak']
    
            known_events['master_index'][event_id] = event
            
        if event_name in artemis_events.keys():
            artemis_data = artemis_events[ event_name ]
            params = artemis_data.get_params(key_list=sig_keys)
            event.set_params( params )
            
            known_events['master_index'][event_id] = event
        
        if event_name in rtmodels.keys():
            model = rtmodels[event_name]
            log.info( model.summary() )
            params  = model.get_params()
            event.set_params( params )
            log.info('BOZZA_T0: ' + str(event.bozza_t0))
            
            known_events['master_index'][event_id] = event

        if event_name in pylima_data.keys():
            pars = pylima_data[event_name]
            for key, value in pars.items():
                setattr(event,str(key).lower(),value)
                
            known_events['master_index'][event_id] = event
            
        event.set_official_name()
        event.set_artemis_status()
        
    n_events = len(known_events['master_index'])
    log.info(' -> total of ' + str(n_events) + ' events')
    
    return known_events

def targets_for_k2_campaign(config, known_events, k2_campaign, log):
    """Function to check whether targets are within the parameters of the
    current K2 campaign"""
    
    log.info('Identifying events within the K2 Campaign')
    
    # First select only those events which we have not checked before:
    events = {}
    for event_id,event in known_events['master_index'].items():
        if event.in_footprint == 'Unknown':
            events[event_id] = event
    log.info(' -> ' + str(len(events)) + \
            ' events to check against K2 Campaign location parameters')
    
    # Check each new target against the K2 Campaign parameters:
    events = k2_campaign.targets_in_footprint( config, events, log=log )
    log.info(' --> Checked events against the whole footprint')
    if config['k2_campaign'] == str(9):
        events = k2_campaign.targets_in_superstamp( events, verbose=False )
        log.info(' --> Checked events relative to the Campaign 9 superstamp')
    
    # Update the master event index:
    for event_id, event in events.items():
        known_events['master_index'][event_id] = event
    
    # Now select all events within the field to (re)check their duration:
    events = {}
    for event_id,event in known_events['master_index'].items():
        if event.in_footprint == True:
            events[event_id] = event
    log.info(' -> ' + str(len(events)) + \
            ' events to check against K2 Campaign dates')
    events = k2_campaign.targets_in_campaign( events, verbose=False, log=log )
    log.info(' --> Checked events occur during Campaign')
    
    # Update the master event index:
    for event_id, event in events.items():
        known_events['master_index'][event_id] = event
    
    return known_events
    
def set_identifier( known_events ):
    """Function to assign a new identifier by incrementing the maximum
    index found in the known_events dictionary
    """
    idx = known_events['max_index']
    idx = idx + 1
    known_events['max_index'] = idx
    
    sidx = str( idx )
    while len(sidx) < 4:
        sidx = '0' + sidx
    identifier = 'K2C9-R-' + sidx
    return identifier, known_events
    
def set_key_names( params, prefix_keys, prefix ):
    """Function to re-name the prefixes of keys in a parameter dictionary
    appropriate to use for a K2C9Event class object
    """
    
    output = {}
    for key, value in params.items():
        if key in prefix_keys:
            output[ prefix + '_' + key ] = value
        else:
            output[ key ] = value
    return output

def get_finder_charts( config, known_events, log ):
    """Function to retrive the findercharts for known events within the K2
    footprint"""
    
    log.info('Fetching findercharts for events within the K2 Campaign')
    
    # Loop through all events, but only extract the finderchart data
    # for targets within the footprint, since its time consuming:
    for event_id, event in known_events['master_index'].items():
        if event.in_footprint  == True and event.during_campaign == True:
            
            origin = event.get_event_origin()
            
            # URL construction and output depends on the survey:
            if origin == 'ogle':
                event_year = str(event.ogle_name).split('-')[1]
                event_number = str(event.ogle_name).split('-')[-1]
                
                file_path = path.join( config['ogle_data_local_location'], \
                                       event.ogle_name + '_fchart.fits' )
                if path.isfile( file_path ) == False:
                    ftp = ftplib.FTP( config['ogle_ftp_server'] )
                    ftp.login()
                    ftp_file_path = path.join( 'ogle', 'ogle4', 'ews', \
                                        event_year, 'blg-'+event_number )
                    ftp.cwd(ftp_file_path)
                    ftp.retrbinary('RETR fchart.fts', open( file_path, 'w').write )
                    ftp.quit()
            
            elif origin == 'moa':
                event_year = str(event.moa_name).split('-')[1]
                event_number = str(event.moa_name).split('-')[-1]
                file_path = path.join( config['moa_data_local_location'], \
                                       event.moa_name + '_fchart.fits' )
                if path.isfile( file_path ) == False:
                    url = path.join( config['moa_root_url'] + event_year, \
                            'datab', 'finder-' + event.moa_survey_id + '.fit.gz' )
                    (page_data,msg) = utilities.get_http_page(url,parse=False)
                    open( file_path, 'w').write(page_data)
                

def generate_K2C9_events_table( config, known_events, log, debug=False ):
    """Function to output a table of events in the K2C9 footprint"""
    
    log.info('Generating event summary tables')
    
    file_path = path.join( config['log_directory'], 'K2C9_events_table.dat' )
    fileobj1 = open( file_path, 'w' )
    fileobj1.write('# Name  RA  Dec  t0  tE  u0  A0  Base_mag  Peak_mag  In_footprint  In_superstamp During_campaign TAP_priority Omega_S(now) sig(Omega_S_now) Omega_S(peak)\n')
    file_list1 = []
    
    file_path = path.join( config['log_directory'], 'K2C9_events_outside_superstamp.dat' )
    fileobj2 = open( file_path, 'w' )
    fileobj2.write('# Name  RA  Dec  t0  tE  u0  A0  Base_mag  Peak_mag  In_footprint  In_superstamp During_campaign TAP_priority Omega_S(now) sig(Omega_S_now) Omega_S(peak) Npixels\n')
    file_list2 = []
    
    pixel_sum = 0.0
    for event_id, event in known_events['master_index'].items():
        if event.in_footprint  == True and event.during_campaign == True:
            
            name = str(event.ogle_name) + ' ' + str(event.moa_name)
            (ra, dec) = event.get_location()
            origin = event.get_event_origin()
            t0 = getattr(event,origin+'_t0')
            te = getattr(event,origin+'_te')
            u0 = getattr(event,origin+'_u0')
            A0 = getattr(event,origin+'_a0')
            vmag = getattr(event,origin+'_i0')
            classification = getattr(event,'classification')
            if str(A0) != 'None' and float(A0) > 0.0:            
                vpeak = round( (float(vmag) - 2.5 * np.log10( float( A0 ) )), 3 )
            else:
                vpeak = 'None'
            if vpeak != 'None' and vpeak <= 9.5:
                npix = '> 100?'
            else:
                npix = '100'
            
            #if str(A0) == 'None' or float(A0) > 0.0:
            entry = name + ' ' + str(ra) + ' ' + str(dec) + ' ' + str(t0) + ' ' + \
                    str(te) + ' ' + str(u0) + ' ' + str(A0) + ' ' + \
                    str(vmag) + ' ' + str(vpeak) + ' ' + \
                    str(event.in_footprint) + ' ' + str(event.in_superstamp) + \
                    ' ' + str(event.during_campaign)  + ' ' + str(event.tap_priority) +\
                    ' ' + str(event.omega_s_now) + ' ' + str(event.sig_omega_s_now) + \
                    ' ' +str(event.omega_s_peak)
                    
                #fileobj1.write(entry+ '\n')
            file_list1.append(entry + '\n')
            
            if event.in_footprint == True and event.in_superstamp == False \
                and event.during_campaign == True:
                #if float(A0) > 0.0:
                if 'microlensing' in classification and float(te) < 10000.0:
                    entry = entry + ' ' + npix + '\n'
                    file_list2.append(entry)
                    pixel_sum = pixel_sum + 100
            
        #if debug == True:
         #   print '-> completed ',event.get_event_name()
    
    file_list1.sort()
    for line in file_list1:
        fileobj1.write(line)
    fileobj1.close()
    file_list2.sort()
    for line in file_list2:
        fileobj2.write(line)
    fileobj2.write('\nTotal N pixels = ' + str(pixel_sum) + '\n')
    fileobj2.close()
    log.info('Completed event summary tables')
    
def generate_exofop_output( config, known_events, artemis_renamed, log ):
    """Function to output datafiles for all events in the format agreed 
    with ExoFOP
    """
    
    log.info('Outputing data for ExoFOP transfer')
    
    # Open manifest file to describe documents for transfer:
    manifest_file = path.join( config['log_directory'], 'MANIFEST' )    
    manifest = open( manifest_file, 'w' )
    
    # Loop over all events, ensuring the correct data products are present
    # for events within the footprint only.  Exclude possible 
    # duplicate event entries to the manifest.  
    identifier_list = []
    for event_id, event in known_events['master_index'].items():
        origin = event.get_event_origin()
        event_name = getattr( event, origin.lower()+'_name' )
        
        if event.in_footprint  == True and event.identifier != None and \
            event.identifier not in identifier_list:
            log.info(' -> Event ' + event_name + '=' + event.identifier + \
                            ' is within the campaign')
            identifier_list.append( event.identifier )
            
            # DO THIS FIRST:
            # Extract available lightcurve data from the appropriate 
            # ARTEMiS file - provides counts of data from survey 
            # providers required for later output. 
            short_name = utilities.long_to_short_name(event_name)
            file_path = path.join( config['models_local_location'], \
                                        short_name+'.plotdata' )
            (ndata, phot_data) = artemis_subscriber.read_artemis_data_file(file_path)
            log.info(' --> Loaded data from ' + path.basename(file_path))
            if event_name in artemis_renamed.values():
                for key, value in artemis_renamed.items():
                    if value == event_name:
                        short_name = utilities.long_to_short_name(key)
                        file_path = path.join( config['models_local_location'], \
                                        short_name+'.plotdata' )
                        (ndata2, phot_data2) = \
                            artemis_subscriber.read_artemis_data_file(file_path)
                        for key, value in ndata2.items():
                            if key in ndata.keys():
                                ndata[key] = ndata[key] + ndata2[key]
                            else:
                                ndata[key] = ndata2[key]
                        phot_data = np.array( phot_data.tolist() + phot_data2.tolist() )
                        log.info(' --> Loaded data from ' + path.basename(file_path))
            if event.ogle_name != None and event.moa_name != None:
                ogle_year = int(event.ogle_name.split('-')[1])
                moa_year = int(event.moa_name.split('-')[1])
                if ogle_year != moa_year:
                    if 'OGLE' in event_name:
                        short_name = utilities.long_to_short_name(event.moa_name)
                    elif 'MOA' in event_name:
                        short_name = utilities.long_to_short_name(event.ogle_name)
                    file_path = path.join( config['models_local_location'], \
                                        short_name+'.plotdata' )
                    (ndata2, phot_data2) = \
                            artemis_subscriber.read_artemis_data_file(file_path)
                    for key, value in ndata2.items():
                        if key in ndata.keys():
                            ndata[key] = ndata[key] + ndata2[key]
                        else:
                            ndata[key] = ndata2[key]
                    phot_data = np.array( phot_data.tolist() + phot_data2.tolist() )
                    log.info(' --> Loaded data from ' + path.basename(file_path))
            
            surveys = { 'O': 'ogle', 'K': 'moa' }
            for code,key in surveys.items():
                if code in ndata.keys():
                    setattr(event, key+'_ndata', ndata[code])
            ntotal = 0
            for p, ncount in ndata.items():
                ntotal = ntotal + ncount
            event.ndata = ntotal
            
            # Output event parameter file:
            output_file = str( event.identifier ) + '.param'
            output_path = path.join( config['log_directory'], output_file )
            event.generate_exofop_param_file( output_path )
            check_sum = utilities.md5sum( output_path )
            manifest.write( path.basename(output_file) + ' ' + check_sum + '\n' )
            log.info(' --> Generated event parameter file')
            
            # Output datafiles of the data which can be shared.  Note this
            # means that datafiles are sometimes NOT produced, and therefore
            # not always included in the manifest
            output_file = str( event.identifier ) + '.data'
            output_path = path.join( config['log_directory'], output_file ) 
            event.generate_exofop_data_file( phot_data, output_path, log )
            if path.isfile( output_path ) == True:
                check_sum = utilities.md5sum( output_path )
                manifest.write( path.basename(output_file) + ' ' + check_sum + '\n' )
                log.info(' --> Generated event data file')
            
            # Copy over the finderchart, if it isn't already there:
            data_origin = origin.lower()+'_data_local_location'
            src = path.join( config[data_origin], event_name + '_fchart.fits' )
            dest = path.join( config['log_directory'], \
                                        event.identifier + '.fchart.' + \
                                        origin.upper() + '.fits' )
            if path.isfile(dest) == False and path.isfile(src) == True:
                copy(src,dest)
                check_sum = utilities.md5sum( dest )
                manifest.write( path.basename(dest) + ' ' + check_sum + '\n' )
                log.info(' --> Generated event finder chart')
            elif path.isfile(dest) == True:
                check_sum = utilities.md5sum( dest )
                manifest.write( path.basename(dest) + ' ' + check_sum + '\n' )
                log.info(' --> Generated event finder chart')
                
            # Generate model PSPL lightcurve files based on ARTEMiS fits:
            key_list = [ 'signalmen_t0', 'signalmen_u0', 'signalmen_te', \
                            origin+'_i0' ]
            params = event.get_params( key_list )
            if None not in params.values():
                params['tstart'] = event.signalmen_t0 - (3.0 * event.signalmen_te)
                params['tstop'] = event.signalmen_t0 + (3.0 * event.signalmen_te)
                model = event_classes.PSPL()
                model.set_params( params, prefix='signalmen' )
                model.mag0 = params[origin+'_i0']
                model.generate_lightcurve()
                lc_file = path.join( config['log_directory'], \
                                    event.identifier + '.model' )
                model.output_model_lightcurve( lc_file, event.identifier, \
                                                            event_name )
                
                check_sum = utilities.md5sum( lc_file )
                manifest.write( path.basename(lc_file) + ' ' + check_sum + '\n' )
                log.info(' --> Generated ARTEMiS model lightcurve ' + \
                        path.basename(lc_file))
            else:
                log.info(' --> No Signalmen parameters available')
            
            # Check for PyLIMA model output:
            # PyLIMA follows ARTEMiS' naming convention, so need to check
            # an event hasn't been renamed:
            if event_name in artemis_renamed.values():
                art_name = None
                for ename, name in artemis_renamed.items():
                    if name == event_name:
                        art_name = ename
            else:
                art_name = event_name
            log.info(' --> Checking for pyLIMA output under the name ' + \
                            event_name + ' = ' + art_name)
            files = { 
                path.join( config['pylima_directory'], art_name+'_pyLIMA.lightcurve' ): \
                path.join( config['log_directory'], \
                                        event.identifier + '.pylima.lightcurve' ), 
                path.join( config['pylima_directory'], art_name+'_pyLIMA.png' ): \
                path.join( config['log_directory'], \
                                        event.identifier + '.pylima.png' )
                }
            
            for src, dest in files.items():
                if path.isfile(src) == True:
                    copy(src,dest)
                    check_sum = utilities.md5sum( dest )
                    manifest.write( path.basename( dest ) + ' ' + check_sum + '\n'   )
                    log.info(' --> Fetched pyLIMA file ' + \
                        path.basename(dest))
    manifest.close()

def ready_file( config, status ):
    """Function to remove the READY file that indicates the data are
    ready for transfer to IPAC.
    Status can be either create or remove    
    """
    
    ready_path = path.join( config['transfer_location'], '../microlensing.READY' )
    
    if status == 'create':
        op = 'touch'
    elif status == 'remove':
        op = '\\rm'
    
    c = 'ssh -X ' + str( config['transfer_user'] ) + ' ' + op + ' ' + ready_path
    (iexec, coutput) = getstatusoutput( c )

def clear_transfer_directory( config ):
    """Function to clear the contents of the IPAC transfer directory to avoid
    confusion with older data products. 
    Note this does NOT clear the findercharts, on the grounds that these 
    rarely change and are quite large    
    """
    search_strings = [ 'K2C9\*model', 'K2C9\*param', 'K2C9\*fchart\*' ]    
    
    for file_name in search_strings:
        file_path = path.join( config['transfer_location'], file_name )
        c = 'ssh -X ' + str( config['transfer_user'] ) + ' \\rm ' + file_path
        (iexec, coutput) = getstatusoutput( c )


def sync_data_for_transfer( config, log ):
    """Function to scp data to the location from which it will be pulled by
    IPAC. """
    
    def rsync_file( config, path_string, log, i, nfiles ):
        """Function to rsync a single file"""
        
        c = 'rsync -av ' + path_string + ' ' + \
            str( config['transfer_user'] ) + ':' + \
                str( config['transfer_location'] )
        (iexec, coutput) = getstatusoutput( c )
        log.info( str(i) + ' out of ' + str(nfiles) + ': ' + \
                    coutput.replace('\n',' ') )
    
    log.info('Syncing data to transfer directory')
    
    # Firstly, ensure any existing READY file has been removed to let
    # IPAC know all transfers should be suspended until its removed:
    ready_file( config, 'remove' )
    
    # Next, clear all old data products from the rsync directory to avoid
    # confusion:
    clear_transfer_directory( config )    
    
    # Read and parse the manifest file to get a list of the files to be
    # transfered.  The manifest itself is added to this list to ensure it too
    # gets transfered.  
    manifest = path.join( config['log_directory'], 'MANIFEST' )
    file_lines = open( manifest, 'r' ).readlines()
    file_lines.append( 'MANIFEST  None' )
    nfiles = len(file_lines)
    log.info(' -> ' + str(nfiles) + ' files to transfer')
    
    # Rsync everything in the Manifest:
    for i,line in enumerate(file_lines):
        f = line.split()[0]
        try:
            file_path = path.join( config['log_directory'], f.replace('\n','') )
        except UnicodeDecodeError:
            log.info('Error: ' + config['log_directory'] + ' ' + f.replace('\n','') )
        if path.isfile( file_path ) == True:
            rsync_file( config, file_path, log, i, nfiles )
    
    # Set the READY FILE:
    ready_file( config, 'create' )
    
###############################################################################
# COMMANDLINE RUN SECTION
if __name__ == '__main__':
    
    exofop_publisher()