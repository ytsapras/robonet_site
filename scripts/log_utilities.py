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
from astropy.time import Time
from datetime import datetime
import glob

def start_day_log( config, log_name, console=False ):
    """Function to initialize a new log file.  The naming convention for the
    file is [log_name]_[UTC_date].log.  A new file is automatically created 
    if none for the current UTC day already exist, otherwise output is appended
    to an existing file.
    This function also configures the log file to provide timestamps for 
    all entries.  
    """

    ts = Time.now()    
    ts = ts.iso.split()[0]
    
    log_file = path.join( config['log_directory'], \
                    config['log_root_name'] + '_' + ts + '.log' )

    # Look for previous logs and rollover the date if the latest log
    # isn't from the curent date:


    # To capture the logging stream from the whole script, create
    # a log instance together with a console handler.  
    # Set formatting as appropriate.
    log = logging.getLogger( log_name )
    
    if len(log.handlers) == 0:
        log.setLevel( logging.INFO )
        file_handler = logging.FileHandler( log_file )
        file_handler.setLevel( logging.INFO )
        
        if console == True:
            console_handler = logging.StreamHandler()
            console_handler.setLevel( logging.INFO )
    
        formatter = logging.Formatter( fmt='%(asctime)s %(message)s', \
                                    datefmt='%Y-%m-%dT%H:%M:%S' )
        file_handler.setFormatter( formatter )

        if console == True:        
            console_handler.setFormatter( formatter )
    
        log.addHandler( file_handler )
        if console == True:            
            log.addHandler( console_handler )
    
    log.info( '\n------------------------------------------------------\n')
    return log
    
def end_day_log( log ):
    """Function to cleanly shutdown logging functions with last timestamped
    entry"""
    
    log.info( 'Processing complete\n' )
    logging.shutdown()

def lock( script_config, state, log ):
    """Method to create and release this script's lockfile and also to determine
    whether another lock file exists which may prevent this script operating.    
    """

    lock_file = path.join( script_config['logdir'], 'obscontrol.lock' )    

    if state == 'lock':
        lock = open(lock_file,'w')
        ts = datetime.utcnow()
        lock.write( ts.strftime("%Y-%m-%dT%H:%M:%S") )
        lock.close()
        log.info('Created lock file')
    
    elif state == 'unlock':
        if path.isfile(lock_file) == True:
            remove( lock_file )
            log.info('Removed lock file')
    
    elif state == 'check':
        lock_list = [ 'obscontrol.lock' ]
        for lock_name in lock_list:
            lock_file = path.join( config['logdir'],lock_name )
            if path.isfile( lock_file ) == True:
                log.info('Clashing lock file encountered ( ' + lock_name + \
                                ' ), halting')
                log_utilities.end_day_log( log )
                exit()
        log.info('Checked for clashing locks; found none')
      