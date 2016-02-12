# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 20:15:01 2016

@author: rstreet
"""

##############################################################################
#                       K2 TARGETS
##############################################################################

import k2_footprint_class
import config_parser
import exofop_publisher
from os import path
        
def k2_events(campaign=9, year=2016):
    """Function to analyse and select events from K2 field"""
    
    # Parse script's own config
    config_file_path = '../configs/surveys_sync.xml'
    config = config_parser.read_config(config_file_path)
        
    # Read in data from surveys
    survey_events = exofop_publisher.load_survey_event_data( config )

    # Initialize K2-footprint data:
    k2_footprint = k2_footprint_class.K2Footprint( campaign, year )    
    
    # Plot events relative to the K2 footprint:
    plot_file = path.join( config['log_directory'], \
                    'K2C9_targets_in_footprint.png' )
    k2_footprint.targets_in_footprint( survey_events )
    k2_footprint.targets_in_superstamp( survey_events )
    k2_footprint.targets_in_campaign( survey_events )
    k2_footprint.plot_footprint( plot_file=plot_file, \
            targets=survey_events, year=2016 )
    
##############################################################################
# COMMANDLINE RUN SECTION
if __name__ == '__main__':
    
    k2_events()
    