# -*- coding: utf-8 -*-
"""
Created on Fri Apr 22 19:05:24 2016

@author: robouser
"""

import k2_footprint_class
import exofop_publisher
from os import path

def plot_k2_events_map():
    """Function to plot maps of the locations of events in and around the 
    K2 Campaign footprint"""
    
    config= { 
            'log_directory': '/science/robonet/rob/Operations/ExoFOP', \
            'master_events_list': 'master_events_list',\
            'k2_campaign': 9, \
            'k2_footprint_data': '/home/robouser/Software/robonet_site/data/k2-footprint.json',\
            'k2_year': 2016,\
            }
    
    known_events = exofop_publisher.get_known_events( config )
    k2_campaign = k2_footprint_class.K2Footprint( config )
    
    plotname = path.join( config['log_directory'], 'k2_events_map.png' )
    k2_campaign.plot_footprint( plot_file=plotname, \
                                targets=known_events['master_index'] )
    
if __name__ == '__main__':
    plot_k2_events_map()