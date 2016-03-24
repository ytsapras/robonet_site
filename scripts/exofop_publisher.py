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
    
    # Remove the READY file from the transfer machine to stop IPAC 
    # transfering data while the script is running. 
    ready_file( config, 'remove' )
    log.info( 'Removed the transfer READY file' )
    key_list = ['ogle_ra', 'ogle_dec']
    
    # Read back the master list of all events known to date:
    known_events = get_known_events( config )
    n_events = len(known_events['master_index'])
    log.info( 'Read list of ' + str( n_events ) + ' known events' )
    
    # Read in lists of previously-identified events so that we don't
    # have to repeat time-consuming calculations later except where necessary:
    false_positives = get_false_positives( config )    
    known_duplicates = get_duplicate_events_list( config, log )
    
    # Load TAP output to provide the prioritization data:
    tap_data = load_tap_output( config, log )    
    
    output_target = False
    if output_target == True:
        sidx = 2518
        sid = 'OGLE-2016-BLG-0211'
        sorigin = 'ogle'
        key_list = [ 'ogle_ra', 'ogle_dec', 'ogle_t0', 'ogle_te' ]
        log.info( 'KNOWN: ' + known_events['master_index'][sidx].summary(key_list)+'\n' )
    
    # Read in the information on the K2 campaign:
    k2_campaign = k2_footprint_class.K2Footprint( config['k2_campaign'], \
                                                    config['k2_year'], log=log )
    
    # Data are provided by combining datastreams from the providing surveys + 
    # ARTEMiS, RTModel.  First step is to read in a list of the event parameters  
    # from all these providers and compare to ensure the list is up to date.  
    # Produce master event dictionary events, but only include
    # those events found within the K2C9 superstamp.
    (artemis_events, artemis_renamed) = load_artemis_event_data( config, log )
    rtmodels = rtmodel_subscriber.rtmodel_subscriber(log=log, \
                                                    renamed=artemis_renamed)
    survey_events = load_survey_event_data( config, known_duplicates, log )
    update_known_duplicates( config, known_duplicates )
    
    # Select those events which are in the K2 footprint
    # Combine all available data on them
    known_events = \
            combine_K2C9_event_feed( known_events, false_positives, \
                                        artemis_events, survey_events, \
                                            rtmodels, tap_data, log )
    
    # Identify which events are within the K2 campaign footprint & dates:
    known_events = targets_for_k2_campaign(config, known_events, k2_campaign, log)
    
    # Assign K2C9 identifiers to any events within the footprint which
    # do not yet have them:
    known_events = assign_identifiers( known_events )    
    
    # Extract findercharts for K2C9 objects:
    get_finder_charts( config, known_events, log )
    
    # Now output the combined information stream in the format agreed on for 
    # the ExoFOP transfer
    generate_exofop_output( config, known_events, log )
    
    # Generate K2C9 event summary table:
    generate_K2C9_events_table( config, known_events, log )
    
    # Update the master list of known events, and those within the K2C9 footprint:
    xsuperstamp_events = update_known_events( config, known_events, log )
    
    # Plot locations of events:
    log.info('Plotting event locations...')
    plotname = path.join( config['log_directory'], 'k2_events_map.png' )
    k2_campaign.plot_footprint( plot_file=plotname, \
                                targets=known_events['master_index'] )
    log.info('Plotted K2C9 event locations')
    
    plotname = path.join( config['log_directory'], 
                                 'k2_events_outside_superstamp_map.png' )
    k2_campaign.plot_footprint( plot_file=plotname, \
                                targets=xsuperstamp_events, \
                                plot_isolated_stars=True, \
                                plot_dark_patches=True )
    log.info('Plotted event locations outside superstamp')
    
    # Sync data for transfer to IPAC with transfer location:
    log.info('Syncing data to transfer directory')
    sync_data_for_transfer( config )  
    
    log_utilities.end_day_log( log )
    
###############################################################################
# SERVICE FUNCTIONS
def lock( config, state=None ):
    """Function to create or remove the scripts lockfile"""
    
    lock_file = path.join( config['log_directory'], \
                                'exofop_lock' )
    if state == None:
        return 0
    elif state == 'create':
        fileobj = open( lock_file, 'w' )
        ts = Time.now()
        fileobj.write( ts.isot + '\n' )
        fileobj.close()
        return 0
    elif state == 'remove':
        if path.isfile( lock_file ) == True:
            remove( lock_file )
            return 0
    else:
        return 0
        
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
                  
            if str(entries[5]).lower() != 'none':
                event_name = str( entries[5] )
                origin = 'ogle'
            if str(entries[6]).lower() != 'none':
                event_name = str( entries[6] )
                origin = 'moa'
            if str(entries[7]).lower() != 'none':
                event_name = str( entries[7] )
                origin = 'kmt'
            
            if event_name not in known_events[origin].keys():
                event = event_classes.K2C9Event()
                event.set_event_name( {'name': event_name} )
                event.master_index = int(entries[0])
                event.identifier = entries[1]
                event.in_footprint = parse_boolean(entries[2])
                event.in_superstamp = parse_boolean(entries[3])
                event.during_campaign = parse_boolean(entries[4])
                event.recommended_status = str(entries[8]).upper()
                event.status = 'UPDATED'
                
                known_events[origin][event_name] = event.master_index
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
                ' ' + str(event.recommended_status).upper() + '\n'
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
    prefix_keys = [ 'a0', 't0', 'sig_t0', 'te', 'sig_te', 'u0', 'sig_u0' ]
    
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

def load_survey_event_data( config, known_duplicates, log ):
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
        if ogle_id == 'OGLE-2016-BLG-0211':
            print 'GOT OGLE-2016-BLG-0211'
            print lens.summary()
            
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
                                artemis_events, survey_events, rtmodels, \
                                    tap_data, log ):
    """Function to produce a dictionary of just those events identified
    within the superstamp of K2C9."""
    
    prefix_keys = [ 'a0', 't0', 'sig_t0', 'te', 'sig_te', 'u0', 'sig_u0', \
                'ra', 'dec' ]
    
    log.info('Combining data on all known events')
    log.info(' -> Combining survey data')
    
    # Review all events reported by the surveys:
    for event_name, event in survey_events.items():
        
        origin = str(event_name.split('-')[0]).lower()
            
        # Exclude known false positives:
        if event_name not in false_positives and \
                'microlensing' in event.classification:
        
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
    
    
    # Combine the complete listing of events with ARTEMiS', TAP's and 
    # RTmodel's output:
    log.info(' -> Combining data from ARTEMiS, TAP and RTModel')
    
    sig_keys = [ 'signalmen_a0', 'signalmen_t0', 'signalmen_sig_t0', \
                 'signalmen_te', 'signalmen_sig_te', 'signalmen_u0', \
                 'signalmen_sig_u0', 'signalmen_anomaly' ]

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
            ' events to check against K2 Campaign parameters')
    
    # Check each new target against the K2 Campaign parameters:
    events = k2_campaign.targets_in_footprint( events, verbose=False )
    if config['k2_campaign'] == str(9):
        events = k2_campaign.targets_in_superstamp( events, verbose=False )
    events = k2_campaign.targets_in_campaign( events, verbose=False )
    
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
        if event.ogle_name == 'OGLE-2016-BLG-0095':
            print event.summary()
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
    
def generate_exofop_output( config, known_events, log ):
    """Function to output datafiles for all events in the format agreed 
    with ExoFOP
    """
    
    log.info('Outputing data for ExoFOP transfer')
    
    # Open manifest file to describe documents for transfer:
    manifest_file = path.join( config['log_directory'], 'MANIFEST' )    
    manifest = open( manifest_file, 'w' )
    
    # Loop over all events, ensuring the correct data products are present
    # for events within the footprint only:
    for event_id, event in known_events['master_index'].items():
        origin = event.get_event_origin()
        event_name = getattr( event, origin.lower()+'_name' )
        
        if event.in_footprint  == True and event.during_campaign == True:
            log.info(' -> Event ' + event_name + ' is within the campaign')
            output_file = str( event.identifier ) + '.param'
            output_path = path.join( config['log_directory'], output_file )
            
            # Output event parameter file:
            event.generate_exofop_data_file( output_path )
            check_sum = utilities.md5sum( output_path )
            manifest.write( output_file + ' ' + check_sum + '\n' )
            log.info(' --> Transfered event parameter file')
            
            # Copy over the finderchart, if it isn't already there:
            data_origin = origin.lower()+'_data_local_location'
            src = path.join( config[data_origin], event_name + '_fchart.fits' )
            dest = path.join( config['log_directory'], \
                                        event_name + '_fchart.fits' )
            if path.isfile(dest) == False:
                copy(src,dest)
            check_sum = utilities.md5sum( dest )
            manifest.write( event_name + '_fchart.fits ' + check_sum + '\n' )
            log.info(' --> Transfered event finder chart')
            
    # Lightcurve data file:
    
    # Model lightcurve data file:
    
    # Colour-magnitude diagrams
    
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
    
def sync_data_for_transfer( config ):
    """Function to scp data to the location from which it will be pulled by
    IPAC. """
    
    def rsync_file( config, path_string ):
        """Function to rsync a single file"""
        
        c = 'rsync -av ' + path_string + ' ' + \
            str( config['transfer_user'] ) + ':' + \
                str( config['transfer_location'] )
        (iexec, coutput) = getstatusoutput( c )
        #print coutput
    
    # Firstly, ensure any existing READY file has been removed to let
    # IPAC know all transfers should be suspended until its removed:
    ready_file( config, 'remove' )
    
    # Read and parse the manifest file to get a list of the files to be
    # transfered.  The manifest itself is added to this list to ensure it too
    # gets transfered.  
    manifest = path.join( config['log_directory'], 'MANIFEST' )
    file_lines = open( manifest, 'r' ).readlines()
    file_lines.append( 'MANIFEST  None' )
    
    # Rsync everything in the Manifest:
    for line in file_lines:
        f = line.split()[0]
        try:
            file_path = path.join( config['log_directory'], f.replace('\n','') )
        except UnicodeDecodeError:
            print config['log_directory'], f.replace('\n','')
        #print ' -> Syncing file ' + file_path
        if path.isfile( file_path ) == True:
            rsync_file( config, file_path )
    
    # Set the READY FILE:
    ready_file( config, 'create' )
    
###############################################################################
# COMMANDLINE RUN SECTION
if __name__ == '__main__':
    
    exofop_publisher()