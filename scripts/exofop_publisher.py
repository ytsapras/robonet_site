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

from os import path
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

def exofop_publisher():
    """
    Driver function to provide a live datafeed of microlensing events within the K2C9 superstamp to ExoFOP
    """
    
    config = config_parser.read_config( '../configs/exofop_publish.xml' )
    print ' -> Read configuration'
    
    init = lock( config, state='create' )    
    
    # Read back the master list of all events known to date:
    known_events = get_known_events( config )
    print ' -> Read list of known events'
    
    # Instantiate a K2 footprint object:
    k2_campaign = k2_footprint_class.K2Footprint( config['k2_campaign'], \
                                                    config['k2_year'] )
    
    # Data are provided by combining datastreams from the providing surveys + 
    # ARTEMiS.  First step is to read in a list of the event parameters from 
    # all these providers and compare to ensure the list is up to date.  
    # Produce master event dictionary events, but only include
    # those events found within the K2C9 superstamp.
    artemis_events = load_artemis_event_data( config )
    print ' -> Loaded ARTEMiS event data'
    survey_events = load_survey_event_data( config )
    print ' -> Loaded survey event data'
    
    # Select those events which are in the K2 footprint
    # Combine all available data on them
    print ' -> Combining data on all known events'
    known_events = \
            combine_K2C9_event_feed( known_events, artemis_events, \
                                               survey_events )
    
    # Identify which events are within the K2 campaign footprint & dates:
    events = known_events['master_index']
    events = k2_campaign.targets_in_footprint( events, verbose=True )
    if config['k2_campaign'] == str(9):    
        events = 
            k2_campaign.targets_in_superstamp( events, verbose=True )
    events = k2_campaign.targets_in_campaign( events, verbose=True )
    known_events['master_index']= events
        
    # Now output the combined information stream in the format agreed on for 
    # the ExoFOP transfer
    generate_exofop_output( config, known_events )
    print ' -> Output data for ExoFOP transfer'
    
    # Update the master list of known events:
    update_known_events( config, known_events )
    
    init = lock( config, state='remove' ) 

###############################################################################
# SERVICE FUNCTIONS
def lock( config, state=None ):
    """Function to create or remove the scripts lockfile"""
    
    lock_file = path.join( config['log_directory'], \
                            config['master_events_list'], \
                                'exofop_lock' )
    if state == None:
        return 0
    elif state = 'create':
        fileobj = open( lock_file, 'w' )
        ts = datetime.utcnow()
        fileobj.write( ts.strftime("%Y-%m-%dT%H:%M:%S")+'\n' )
        fileobj.close()
        return 0
    elif state = 'remove':
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
    
    events_file = path.join( config['log_directory'], config['events_list'] )
    
    if path.isfile( events_file ) == False:
        print 'Error: Missing events file, ' + events_file
        exit()
        
    file_lines = open( events_file, 'r' ).readlines()
    
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
            event = event_classes.K2C9Event()
            event.master_index = int(entries[0])
            event.identifier = entries[1]
            event.in_footprint = bool(entries[2])
            event.in_superstamp = bool(entries[3])
            event.during_campaign = bool(entries[4])
            if entries[5] != 'None':
                event.ogle_name = repr( entries[5] )
                known_events['ogle'][event.ogle_name] = event.master_index
            if entries[6] != 'None':
                event.moa_name = repr( entries[6] )
                known_events['moa'][event.moa_name] = event.master_index
            if entries[7] != 'None':
                event.kmt_name = repr( entries[7] )
                known_events['kmt'][event.kmt_name] = event.master_index
            known_events['identifiers'][event.master_index] = event.identifier
            known_events['master_index'][event.master_index] = event
            if str(event.identifier).lower() != 'none'
                idx = int(str(event.identifier).replace('K2C9',''))
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
    fileobj.write('# Event_index   K2C9_ID   In_footprint  In_superstamp  During_campaign OGLE_ID MOA_ID KMTNET_ID' )
    for master_index, event in known_events['master_index']:
        line = str(master_index) + ' ' + str(event.identifier) + ' ' + \
                str(event.in_footprint) + ' ' + str(event.in_superstamp) + ' '\
                + str(event.during_campaign) + ' ' + str(event.ogle_name) + \
                ' ' + str(event.moa_name) + ' ' + str(event.kmt_name) + '\n'
        fileobj.write( line )
    fileobj.close()
    
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

def load_survey_event_data( config ):
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
                ogle_event.set_params( moa_params )
                survey_events[ ogle_id_list[i] ] = ogle_event
                survey_events[ moa_params['name'] ] = ogle_event
            
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
    
    
def match_events_by_position( coords1, coords2 ):
    """Function to match events by location given tuples of their
    coordinates from two data providers.
    If the coordinates fall within 0.5arcsec, True is returned, 
    otherwise False
    """
    
    match = False
    threshold = 0.5
    
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
        
    return match

def combine_K2C9_event_feed( known_events, artemis_events, survey_events ):
    """Function to produce a dictionary of just those events identified
    within the superstamp of K2C9."""
    
    prefix_keys = [ 'a0', 't0', 'sig_t0', 'te', 'sig_te', 'u0', 'sig_u0', \
                'ra', 'dec' ]
    
    # First review all events known to ARTEMiS: 
    for event_id, event in artemis_events.items():
        
        # Does this event already have a K2C9 identifier?:
        origin = str(event_id.split('-')[0]).lower()
        if event_id in known_events[origin].keys():
            event.master_index = known_events[origin][event_id]
            if event.master_index in known_events['identifiers'].keys():
                event.identifier = known_events['identifiers'][event.master_index]
        else:
            # Generate a new master_index and add to the known_events index:
            event.master_index = len(known_events['master_index'])
            known_events['master_index'][event.master_index] = event
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
    for event_id, event in survey_events.items():
        
        # Does this event already have a K2C9 identifier?:
        origin = str(event_id.split('-')[0]).lower()
        #print origin, event_id
        if event_id in known_events[origin].keys():
            event.master_index = known_events[origin][event_id]
            if event.master_index in known_events['identifiers'].keys():
                event.identifier = known_events['identifiers'][event.master_index]
        else:
            # Generate a new master_index and add to the known_events index:
            event.master_index = len(known_events['master_index'])
            known_events['master_index'][event.master_index] = event
            known_events[origin][event_id] = event.master_index
            
        
        if event.master_index not in events.keys():
            known_events[ event.master_index ] = event
        
        
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
    identifier = 'K2C9' + sidx
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


def generate_exofop_output( config, known_events ):
    """Function to output datafiles for all events in the format agreed 
    with ExoFOP
    """
    
    # Loop over all events, creating a summary output file for each one:
    for event_id, event in known_events['master_index'].items():
        
        if event.in_footprint  == True and event.during_campaign == True:
            output_file = str( event_id ) + '.param'
            print event_id, output_file
            output_path = path.join( config['log_directory'], output_file )
            event.generate_exofop_data_file( output_path )
        
    # Create manifest for data transfer:
    

###############################################################################
# COMMANDLINE RUN SECTION
if __name__ == '__main__':
    
    exofop_publisher()