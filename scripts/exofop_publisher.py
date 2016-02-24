# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 18:03:54 2016

@author: rstreet
"""

#!/usr/bin/python
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

def exofop_publisher():
    """
    Driver function to provide a live datafeed of microlensing events within the K2C9 superstamp to ExoFOP
    """
    
    config = config_parser.read_config( '../configs/exofop_publish.xml' )
    
    log = log_utilities.start_day_log( config, __name__ )
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
    
    output_target = False
    if output_target == True:
        sidx = 1433
        sid = 'MOA-2015-BLG-102'
        sorigin = 'moa'
        key_list = [ 'moa_ra', 'moa_dec', 'moa_t0', 'moa_te' ]
        log.info( 'KNOWN: ' + known_events['master_index'][sidx].summary(key_list)+'\n' )
    
    # Read in the information on the K2 campaign:
    k2_campaign = k2_footprint_class.K2Footprint( config['k2_campaign'], \
                                                    config['k2_year'] )
    
    # Data are provided by combining datastreams from the providing surveys + 
    # ARTEMiS.  First step is to read in a list of the event parameters from 
    # all these providers and compare to ensure the list is up to date.  
    # Produce master event dictionary events, but only include
    # those events found within the K2C9 superstamp.
    log.info('Loading ARTEMiS event data')
    artemis_events = load_artemis_event_data( config )
    log.info(' -> ' + str(len(artemis_events)) + ' events from ARTEMiS')
    log.info('Loading survey event data')
    survey_events = load_survey_event_data( config, log )
    log.info(' -> ' + str(len(survey_events)) + ' events from surveys')
    
    if output_target == True:
        log.info('SURVEY: '+survey_events[sid].summary(key_list)+'\n')

    # Select those events which are in the K2 footprint
    # Combine all available data on them
    log.info('Combining data on all known events')
    known_events = \
            combine_K2C9_event_feed( known_events, artemis_events, \
                                               survey_events )
    n_events = len(known_events['master_index'])
    log.info(' -> total of ' + str(n_events) + ' events')  

    if output_target == True:
        log.info('COMBINED: '+known_events['master_index'][sidx].summary(key_list)+'\n')

    # Identify which events are within the K2 campaign footprint & dates:
    log.info('Identifying events within the K2 Campaign')
    events = known_events['master_index']
    events = k2_campaign.targets_in_footprint( events, verbose=True )
    if config['k2_campaign'] == str(9):    
        events = k2_campaign.targets_in_superstamp( events, verbose=True )
    events = k2_campaign.targets_in_campaign( events, verbose=True )
    known_events['master_index']= events
    
    if output_target == True:
        log.info('IDENTIFIED: '+known_events['master_index'][sidx].summary(key_list)+'\n')
    
    # Assign K2C9 identifiers to any events within the footprint which
    # do not yet have them:
    known_events = assign_identifiers( known_events )    
    
    # Extract findercharts for K2C9 objects:
    
    
    # Now output the combined information stream in the format agreed on for 
    # the ExoFOP transfer
    generate_exofop_output( config, known_events )
    log.info('Output data for ExoFOP transfer')
    
    # Update the master list of known events, and those within the K2C9 footprint:
    update_known_events( config, known_events )
    
    # Plot locations of events:
    plotname = path.join( config['log_directory'], 'k2_events_map.png' )
    k2_campaign.plot_footprint( plot_file=plotname, \
                                targets=known_events['master_index'] )
    
    # Sync data for transfer to IPAC with transfer location:
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

def update_known_events( config, known_events ):
    """Function to output a cross-identified list of all event identifiers"""
    
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
    for event_id, event in known_events['master_index'].items():
        if event.in_footprint == True and event.during_campaign == True:        
            line = str(event.identifier) + ' ' + str(event.ogle_name) + \
                ' ' + str(event.moa_name) + ' ' + str(event.kmt_name) + ' ' + \
                str(event.in_footprint) + ' ' + str(event.in_superstamp) + ' '\
                + str(event.during_campaign) + '\n'
            fileobj.write( line )
    fileobj.close()
    

def assign_identifiers( known_events ):
    """Function to assign K2C9 identifiers to events that are within the 
    footprint and Campaign duration"""
    
    for event_id, event in known_events['master_index'].items():
        if event.in_footprint == True and event.during_campaign == True\
            and str(event.identifier).lower() == 'none':
            ( event.identifier, known_events ) = set_identifier( known_events )
            known_events['master_index'][event_id] = event
    return known_events
    
def load_artemis_event_data( config ):
    """Function to load the full list of events known to ARTEMiS."""
    
    # List of keys in a K2C9Event which should be prefixed with
    # Signalmen:
    prefix_keys = [ 'a0', 't0', 'sig_t0', 'te', 'sig_te', 'u0', 'sig_u0' ]
    
    # Make a dictionary of all events known to ARTEMiS based on the 
    # ASCII-format model files in its 'models' directory.
    search_str = path.join( config['models_local_location'], \
            '?B1\[5-6\]????.model' )
    model_file_list = glob.glob( search_str )
    
    artemis_events = {}
    for model_file in model_file_list:
        params = artemis_subscriber.read_artemis_model_file( model_file )
        params = set_key_names( params, prefix_keys, 'signalmen' )
        if len( params ) > 0:
            event = event_classes.K2C9Event()
            event.set_params( params )
            event.set_event_name( params )
            artemis_events[ params['long_name'] ] = event
            
    return artemis_events    

def load_survey_event_data( config, log ):
    """Method to load the parameters of all events known from the surveys.
    """
    
    ogle_data = survey_data_utilities.read_ogle_param_files( config )
    moa_data = survey_data_utilities.read_moa_param_files( config )
    
    # Combine the data from both sets of events into a single 
    # dictionary of K2C9Event objects.
    # Cross-match by position to identify objects detected by multiple surveys
    
    # Start by working through OGLE events since this is usually a superset
    # of those detected by the other surveys:
    survey_events = {}
    prefix_keys = [ 'a0', 't0', 'sig_t0', 'te', 'sig_te', 'u0', 'sig_u0', \
                'ra', 'dec' ]
    for ogle_id, lens in ogle_data.lenses.items():
        event = event_classes.K2C9Event()
        params = lens.get_params()
        params = set_key_names( params, prefix_keys, 'ogle' )
        event.set_event_name( params )
        event.set_params( params )
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
                moa_lens_params = lens.get_params()
                ogle_event.set_params( moa_lens_params )
                survey_events[ ogle_id_list[i] ] = ogle_event
                survey_events[ moa_lens_params['name'] ] = ogle_event
            
            i = i + 1
            
        # If no match to an existing OGLE event is found, add this
        # event to the dictionary as a MOA event. 
        if match == False:
            event = event_classes.K2C9Event()
            moa_params = lens.get_params()
            moa_params = set_key_names( moa_params, prefix_keys, 'moa' )
            event.set_event_name( moa_params )
            event.set_params( moa_params )
            survey_events[ event.moa_name ] = event

    
    return survey_events
    
    
def match_events_by_position( coords1, coords2, debug=False ):
    """Function to match events by location given tuples of their
    coordinates from two data providers.
    If the coordinates fall within 0.5arcsec, True is returned, 
    otherwise False
    """
    
    match = False
    threshold = 1.0     # arcsec
    
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

def combine_K2C9_event_feed( known_events, artemis_events, survey_events ):
    """Function to produce a dictionary of just those events identified
    within the superstamp of K2C9."""
    
    prefix_keys = [ 'a0', 't0', 'sig_t0', 'te', 'sig_te', 'u0', 'sig_u0', \
                'ra', 'dec' ]
    
    # First review all events known to ARTEMiS:
    for event_id, event in artemis_events.items():
        
        origin = str(event_id.split('-')[0]).lower()
        
        # Event already known:
        if event_id in known_events[origin].keys():
            event.master_index = known_events[origin][event_id]
            if event.master_index in known_events['identifiers'].keys():
                event.identifier = known_events['identifiers'][event.master_index]
                
            # Update event from known_events with ARTEMiS parametersXXX
            
            event.status = 'UPDATED'
            
        else:
            # Generate a new master_index and add to the known_events index:
            event.master_index = len(known_events['master_index'])
            event.status = 'NEW'
            known_events[origin][event_id] = event.master_index
            
        # Is this event in the survey_events list?
        # Theoretically it should always be, but if the surveys webservice
        # gets out of sync for whatever reason, we should handle this case
        # Events are listed by both OGLE and MOA names for easy look-up
        # If an event is found, transfer the parameters from the survey data:
        if event_id in survey_events.keys():
            survey_data = survey_events[ event_id ]
            params = survey_data.get_params()
            params = set_key_names( params, prefix_keys, origin )
            event.set_params( params )
            
        known_events['master_index'][ event.master_index ] = event
            
    # Now review all events reported by the survey as a double-check
    # that ARTMEMiS isn't out of sync:
    for event_name, event in survey_events.items():
        
        origin = str(event_name.split('-')[0]).lower()
        
        # Previously known events (K2C9Events):
        if event_name in known_events[origin].keys():
            event.master_index = known_events[origin][event_name]
            # Check to see if it has a K2 index:
            if event.master_index in known_events['identifiers'].keys():
                event.identifier = known_events['identifiers'][event.master_index]
            
            # Ensure event has the up to date parameters from the survey:
            
            event.status = 'UPDATED'
            
        # New events:
        else:
            
            # Generate a new master_index and add to the known_events index:
            event.master_index = len(known_events['master_index'])
            event.status = 'NEW'
            known_events[origin][event_name] = event.master_index
            
        # Always update the known_events with the most up to date event data
        known_events['master_index'][ event.master_index ] = event
        
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

def get_finder_charts( config, known_events ):
    """Function to retrive the findercharts for known events within the K2
    footprint"""
    
    # Loop through all events, but only extract the finderchart data
    # for targets within the footprint, since its time consuming:
    for event_id, event in known_events['master_index'].items():
        if event.in_footprint  == True and event.during_campaign == True:
            
            origin = event.get_event_origin()
            
            # URL construction and output depends on the survey:
            if origin == 'ogle':
                event_year = str(event.ogle_name).split('-')[1]
                event_number = str(event.ogle_name).split('-')[-1]
                
                ftp = ftplib.FTP( config['ogle_ftp_server'] )
                ftp.login()
                ftp_file_path = path.join( 'ogle', 'ogle4', 'ews', \
                                    event_year, 'blg-'+event_number )
                ftp.cwd(ftp_file_path)
                file_path = path.join( config['ogle_data_local_location'], \
                                       event.ogle_name + '_fchart.fits' )
                print file_path
                ftp.retrbinary('RETR fchart.fts', open( file_path, 'w').write )
                ftp.quit()
                

def generate_exofop_output( config, known_events ):
    """Function to output datafiles for all events in the format agreed 
    with ExoFOP
    """
    
    # Open manifest file to describe documents for transfer:
    manifest_file = path.join( config['log_directory'], 'MANIFEST' )    
    manifest = open( manifest_file, 'w' )
    
    # Loop over all events, ensuring the correct data products are present
    # for events within the footprint only:
    for event_id, event in known_events['master_index'].items():
        
        if event.in_footprint  == True and event.during_campaign == True:
            output_file = str( event.identifier ) + '.param'
            output_path = path.join( config['log_directory'], output_file )
            
            # Output event parameter file:
            event.generate_exofop_data_file( output_path )
            
            # Update the transfer manifest:
            manifest.write( output_file + '\n' )
        
    # Lightcurve data file:
    
    # Model lightcurve data file:
    
    # Colour-magnitude diagrams
    
    # Finder charts:
    
    # End manifest by adding the Manifest to the list:
    manifest.write( 'MANIFEST\n' )
    manifest.close()

def ready_file( config, status ):
    """Function to remove the READY file that indicates the data are
    ready for transfer to IPAC.
    Status can be either create or remove    
    """
    
    ready_path = path.join( config['transfer_location'], 'READY' )
    
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
    # transfered:
    manifest = path.join( config['log_directory'], 'MANIFEST' )
    file_list = open( manifest, 'r' ).readlines()
    
    # Rsync everything in the Manifest:
    for f in file_list:
        file_path = path.join( config['log_directory'], f.replace('\n','') )
        #print ' -> Syncing file ' + file_path
        if path.isfile( file_path ) == True:
            rsync_file( config, file_path )
    
    # Set the READY FILE:
    ready_file( config, 'create' )
    
###############################################################################
# COMMANDLINE RUN SECTION
if __name__ == '__main__':
    
    exofop_publisher()