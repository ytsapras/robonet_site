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
import survey_subscriber
from astropy.time import Time
import numpy as np
import utilities

def exofop_publisher():
    """
    Driver function to provide a live datafeed of microlensing events within the K2C9 superstamp to ExoFOP
    """
    
    config = config_parser.read_config( '../configs/exofop_publish.xml' )
    print ' -> Read configuration'
    
    # Read back the master list of all events known to date:
    known_events = get_known_events( config )
    print ' -> Read list of known events'
    
    # Data are provided by combining datastreams from the providing surveys + ARTEMiS
    # First step is to read in a list of the event parameters from all these providers and compare
    # to ensure the list is up to date.  Produce master event dictionary events, but only include
    # those events found within the K2C9 superstamp.
    artemis_events = load_artemis_event_data( config )
    print ' -> Loaded ARTEMiS event data'
    survey_events = load_survey_event_data( config )
    print ' -> Loaded survey event data'
    
    # Select those events which are in the K2 superstamp
    # XXX what about events outside that? XXX
    # Combine all available data on them
    events = combine_K2C9_event_feed( known_events, artemis_events, \
                                               survey_events )
    print ' -> Combined data on all known events within superstamp'
    
    # Now output the combined information stream in the format agreed on for the ExoFOP transfer
    generate_exofop_output( config, events )
    print ' -> Output data for ExoFOP transfer'
    
    # Update the master list of known events:
    

###############################################################################
# SERVICE FUNCTIONS
def get_known_events( config ):
    """Function to load the list of known events within the K2 footprint.
    File format: # indicates comment line
    K2C9identifier OGLE_name MOA_name KMT_name
    All name entries may individually contain None entries, but one of
    them must be a valid, long-hand format name.
    """
    
    events_file = path.join( config['log_directory'], config['events_list'] )
    file_lines = open( events_file, 'r' ).readlines()
    
    known_events= {'identifiers': {}, \
                   'ogle': {}, \
                   'moa': {}, \
                   'kmt': {},
                   'max_index': None
                   }
    for line in file_lines:
        if len(line) > 0 and line.lstrip()[0:1] != '#':
            entries = line.split()
            event = K2C9Event()
            event.identifier = entries[0]
            if entries[1] != 'None':
                event.ogle_name = repr( entries[1] )
                known_events['ogle'][event.ogle_name] = event.identifier
            if entries[2] != 'None':
                event.moa_name = repr( entries[2] )
                known_events['moa'][event.moa_name] = event.identifier
            if entries[3] != 'None':
                event.kmt_name = repr( entries[3] )
                known_events['kmt'][event.kmt_name] = event.identifier
            known_events['identifiers'][event.identifier] = event
            idx = int(str(event.identifier).replace('K2C9',''))
            if known_events['max_index'] == None:
                known_events['max_index'] = idx
            else:
                if idx > known_events['max_index']:
                    known_events['max_index'] = idx
                    
    return known_events

def load_artemis_event_data( config ):
    """Function to load the full list of events known to ARTEMiS."""
    
    # List of keys in a K2C9Event which should be prefixed with
    # Signalmen:
    prefix_keys = [ 'a0', 't0', 'sig_t0', 'te', 'sig_te', 'u0', 'sig_u0' ]
    
    # Make a dictionary of all events known to ARTEMiS based on the 
    # ASCII-format model files in its 'models' directory.
    search_str = path.join( config['models_local_location'], '?B15????.model' )
    model_file_list = glob.glob( search_str )
    
    artemis_events = {}
    for model_file in model_file_list:
        params = artemis_subscriber.read_artemis_model_file( model_file )
        params = set_key_names( params, prefix_keys, 'signalmen' )
        if len( params ) > 0:
            event = K2C9Event()
            event.set_params( params )
            event.set_event_name( params )
            artemis_events[ params['long_name'] ] = event
            
    return artemis_events    

def load_survey_event_data( config ):
    """Method to load the parameters of all events known from the surveys.
    """
    
    (ogle_last_update, ogle_lens_params) = survey_subscriber.read_ogle_param_files( config )
    (moa_last_update, moa_lens_params) = survey_subscriber.get_moa_parameters( config )
    
    # Combine the data from both sets of events into a single 
    # dictionary of K2C9Event objects.
    # Cross-match by position to identify objects detected by multiple surveys
    
    # Start by working through OGLE events since this is usually a superset
    # of those detected by the other surveys:
    survey_events = {}
    prefix_keys = [ 'a0', 't0', 'sig_t0', 'te', 'sig_te', 'u0', 'sig_u0', \
                'ra', 'dec' ]
    for ogle_id, lens in ogle_lens_params.items():
        event = K2C9Event()
        params = lens.get_params()
        params = set_key_names( params, prefix_keys, 'ogle' )
        event.set_event_name( params )
        event.set_params( params )
        survey_events[ event.ogle_name ] = event
    
    ogle_id_list = survey_events.keys()
    ogle_id_list.sort()
    
    # Now work through MOA events, adding them to the dictionary:
    for moa_id, lens in moa_lens_params.items():
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
            event = K2C9Event()
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
    
    events = {}
    prefix_keys = [ 'a0', 't0', 'sig_t0', 'te', 'sig_te', 'u0', 'sig_u0', \
                'ra', 'dec' ]
    
    # First review all events known to ARTEMiS: 
    for event_id, event in artemis_events.items():
        
        # First check whether the event is within the K2C9 superstamp:
        in_superstamp = True
        
        if in_superstamp == True: 
            # Does this event already have a K2C9 identifier?:
            origin = str(event_id.split('-')[0]).lower()
            if event_id in known_events[origin].keys():
                event.identifier = known_events[origin][event_id]
            else:
                ( event.identifier, known_evnets ) = set_identifier( known_events )
            
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
            
            events[ event.identifier ] = event
            
    # Now review all events reported by the survey as a double-check
    # that ARTMEMiS isn't out of sync:
    for event_id, event in survey_events.items():
        
        # First check whether the event is within the K2C9 superstamp:
        in_superstamp = True
        if in_superstamp == True:
            
            # Does this event already have a K2C9 identifier?:
            origin = str(event_id.split('-')[0]).lower()
            #print origin, event_id
            if event_id in known_events[origin].keys():
                event.identifier = known_events[origin][event_id]
            else:
                ( event.identifier, known_events ) = set_identifier( known_events )
                
            events[ event.identifier ] = event
        
    
    return events
            
def set_identifier( known_events ):
    """Function to assign a new identifier by incrementing the maximum
    index found in the known_events dictionary
    """
    idx = known_events['max_index']
    idx = idx + 1
    known_events['max_index'] = idx
    
    sidx = str( idx )
    while len(sidx) < 3:
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


def generate_exofop_output( config, events ):
    """Function to output datafiles for all events in the format agreed 
    with ExoFOP
    """
    
    # Verify output directory exists:
    
    # Loop over all events, creating a summary output file for each one:
    for event_id, event in events.items():
        
        output_file = str( event_id ) + '.param'
        output_path = path.join( config['log_directory'], output_file )
        event.generate_exofop_data_file( output_path )
        

class K2C9Event():
    """Class describing the parameters to be output for a microlensing event 
    within the K2/Campaign 9 field
    """
    def __init__( self ):
        self.identifier = None
        self.status = 'NEW'
        self.recommended_status = 'NEW'
        self.ogle_name = None
        self.ogle_ra = None 
        self.ogle_dec = None
        self.ogle_t0 = None
        self.ogle_sig_t0 = None
        self.ogle_a0 = None
        self.ogle_sig_a0 = None
        self.ogle_te = None
        self.ogle_sig_te = None
        self.ogle_u0 = None
        self.ogle_sig_u0 = None
        self.ogle_i0 = None
        self.ogle_sig_i0 = None
        self.ogle_ndata = None
        self.ogle_url = None
        self.moa_name = None
        self.moa_ra = None
        self.moa_dec = None
        self.moa_t0= None
        self.moa_sig_t0= None
        self.moa_a0 = None
        self.moa_sig_a0 = None
        self.moa_te = None
        self.moa_sig_te = None
        self.moa_u0 = None
        self.sig_u0 = None
        self.i0 = None
        self.sig_i0 = None
        self.ndata = None
        self.moa_url = None
        self.kmt_name = None
        self.kmt_ra = None
        self.kmt_dec = None
        self.kmt_t0 = None
        self.kmt_sig_t0 = None
        self.kmt_a0 = None
        self.kmt_sig_a0 = None
        self.kmt_te = None
        self.kmt_sig_te = None
        self.kmt_u0 = None
        self.kmt_sig_u0 = None
        self.kmt_i0 = None
        self.kmt_sig_i0 = None
        self.kmt_ndata = None
        self.kmt_url = None
        self.signalmen_a0 = None
        self.signalmen_t0 = None
        self.signalmen_sig_t0 = None
        self.signalmen_te = None
        self.signalmen_sig_te = None
        self.signalmen_u0 = None
        self.signalmen_sig_u0 = None
        self.signalmen_anomaly = None
        self.pylima_a0 = None
        self.pylima_sig_a0 = None
        self.pylima_te = None
        self.pylima_sig_te = None
        self.pylima_t0 = None
        self.pylima_sig_t0 = None
        self.pylima_u0 = None
        self.pylima_sig_u0 = None
        self.pylima_rho = None
        self.pylima_sig_rho = None
        self.bozza_a0 = None
        self.bozza_sig_a0 = None
        self.bozza_te = None
        self.bozza_sig_te = None
        self.bozza_t0 = None
        self.bozza_sig_t0 = None
        self.bozza_u0 = None
        self.bozza_sig_u0 = None
        self.bozza_rho = None
        self.bozza_sig_rho = None
        self.bozza_s = None
        self.bozza_sig_s = None
        self.bozza_q = None
        self.bozza_sig_q = None
        self.bozza_theta = None
        self.bozza_sig_theta = None
        self.bozza_pi_perp = None
        self.bozza_sig_pi_perp = None
        self.bozza_pi_para = None
        self.bozza_sig_pi_para = None
        self.bozza_url = None
        self.nnewdata = 0
        self.time_last_updated = None
        self.in_footprint = None
        self.in_superstamp = None
        self.during_campaign = None
        self.alertable = None

    def set_params( self, params ):
        """Method to set the parameters of the current instance from a 
        a dictionary containing some or all of the parameters of the class.
        Key names in the input dictionary must match those used in the class.
        """

        for key, value in params.items():
            if key in dir( self ):
                setattr( self, key, value )
    
    def get_params( self ):
        """Method to return a dictionary of all parameters"""
        
        params = {}
        for key in dir( self ):
            params[key] = getattr(self,key)
        return params
        
    def set_event_name( self, params ):
        """Method to set the name of an event based on the given names
        allocated by survey.
        """
        
        # Identify the originating survey:
        if 'name' in params.keys(): name_key = 'name'
        else: name_key = 'long_name'
            
        prefix = (str( params[name_key] ).split('-')[0]).lower()
        
        key = prefix + '_name'
        if key in dir( self ):
            setattr(self, key, params[ name_key ] )
    
    def summary( self, key_list ):
        """Method to print a customizible summary of the information on
        a given K2C9Event instance, given a list of keys to output.
        """

        # An event may be discovered by multiple surveys and hence
        # have multiple event names:
        name = ''
        for key in [ 'ogle_name', 'moa_name', 'kmt_name' ]:
            if getattr(self, key) != None: 
                name = name + str( getattr( self, key ) )
        
        output = str( self.identifier ) + ' ' + name + ' '
        for key in key_list:
            if key in dir( self ):
                output = output + str( getattr(self,key) ) + ' '
        return output

    def generate_exofop_data_file( self, output_path ):
        """Method to output a summary file of all parameters of an 
        instance of this class
        """
        
        # First set timestamp of output:
        nt = Time.now()
        self.time_last_updated = nt.utc.value.strftime("%Y-%m-%dT%H:%M:%S")
        
        key_list = dir( self )
        exclude_keys = [ 'generate_exofop_data_file', \
                         'get_valid_params', \
                         'set_event_name', \
                         'set_params',\
                         'get_par',\
                         'get_params',\
                         'summary',\
                         'in_superstamp',\
                         'in_footprint',\
                         'during_campaign',\
                         'get_location',
                         ]
        for key in exclude_keys:
            if key in key_list or '__' in key:
                key_list.remove( key )
        key_list.sort()
        
        f = open( output_path, 'w' )
        
        for attr in key_list:
            key = str(attr).lower()
            if '__' not in key[0:2]: 
                value = str( getattr(self,key) )
                f.write( key.upper() + '    ' + value + '\n' )
        
        f.close()
    
    def get_location( self ):
        """Return coordinates of event"""
        
        ra = None
        dec = None
        if self.ogle_ra != None and self.ogle_dec != None:
            ra = self.ogle_ra
            dec = self.ogle_dec
        elif self.moa_ra != None and self.moa_dec != None:
            ra = self.moa_ra
            dec= self.moa_dec
        return (ra, dec)

    def get_par( self, param_name ):
        """Return indicated parameter value for an event"""
        
        value = None
        if getattr( self, 'ogle_' + param_name ) != None:
            value = getattr( self, 'ogle_' + param_name )
        elif getattr( self, 'moa_' + param_name ) != None:
            value = getattr( self, 'moa_' + param_name )
        return value

###############################################################################
# COMMANDLINE RUN SECTION
if __name__ == '__main__':
    
    exofop_publisher()