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

def exofop_publisher():
    """
    Driver function to provide a live datafeed of microlensing events within the K2C9 superstamp to ExoFOP
    """
    
    config = config_parser.read_config( '../configs/exofop_publish.xml' )  
    
    # Data are provided by combining datastreams from the providing surveys + ARTEMiS
    # First step is to read in a list of the event parameters from all these providers and compare
    # to ensure the list is up to date.  Produce master event dictionary events, but only include
    # those events found within the K2C9 superstamp.
    artemis_events = load_artemis_event_data()
    survey_events = load_survey_event_data()
    
    events = combine_event_feeds( artemis_events, survey_events )
    
    # Now output the combined information stream in the format agreed on for the ExoFOP transfer
    generate_exofop_output( events )
    

###############################################################################
# SERVICE FUNCTIONS
def load_artemis_event_data( config ):
    """Function to load the full list of events known to ARTEMiS."""
    
    # Make a dictionary of all events known to ARTEMiS based on the 
    # ASCII-format model files in its 'models' directory.
    search_str = path.join( config['models']['local_location'], '*.model' )
    model_file_list = glob.glob( search_str )
    
    artemis_events = {}
    for model_file in model_file_list:
        params = read_artemis_model_file(f)
        artemis_events[ params['short_name'] ] = params

    return artemis_events    



def generate_exofop_output( config, events ):
    """Function to output datafiles for all events in the format agreed 
    with ExoFOP
    """
    
    # Verify output directory exists:
    
    # Loop over all events, creating a summary output file for each one:
    for event_id, params in events:
        
        output_file = str( event_id ) + '.model'
        output_path = path.join( config['exofop_directory'], output_file )
        output = open( output_path, 'w' )
        
        
        output.close()

Class K2C9Event():
    """Class describing the parameters to be output for a microlensing event 
    within the K2/Campaign 9 field
    """
    def __init__():
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

    def generate_exofop_data_file( self, output_path ):
        """Method to output a summary file of all parameters of an 
        instance of this class
        """
        
        f = open( output_path, 'w' )
        
        
        
        f.close()
        

###############################################################################
# COMMANDLINE RUN SECTION
if __name__ == '__main__':
    
    exofop_publisher()