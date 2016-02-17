# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 00:00:05 2016

@author: robouser
"""

#############################################################################
#                       LOGGING UTILITIES
#############################################################################

import logging
from os import path

def start_day_log( config ):
    """Function to initialize a new log file.  The naming convention for the
    file is [log_name]_[UTC_date].log.  A new file is automatically created 
    if none for the current UTC day already exist, otherwise output is appended
    to an existing file.
    This function also configures the log file to provide timestamps for 
    all entries.  
    """
    
    log_file = path.join( config['log_directory'], config['log_root_name'] )

    logging.basicConfig( filename=log_file, \
                            format='%(asctime)s %(message)s', \
                            datefmt='%Y-%m-%dT%H:%M:%S', \
                            level=logging.INFO )

    logging.info( '\n------------------------------------------------------\n')
