# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 00:00:05 2016

@author: robouser
"""

#############################################################################
#                       LOGGING UTILITIES
#############################################################################

import logging
from os import path, remove
from sys import exit
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
    
    Parameters:
        config    dictionary    Script configuration including parameters
                                log_directory  Directory path
                                log_root_name  Name of the log file
        log_name  string        Name applied to the logger Object 
                                (not to be confused with the log_root_name)
        console   Boolean       Switch to capture logging data from the 
                                stdout.  Normally set to False.
    Returns:
        log       open logger object
    """

    log_file = get_log_path( config )

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

def get_log_path( config ):
    """Function to determine the path and name of the log file, giving it
    a date-stamp in UTC.
    
    Parameters:
        config    dictionary    Script configuration including parameters
                                log_directory  Directory path
                                log_root_name  Name of the log file   
    Returns:
        log_file  string        Path/log_name string
    """
    
    ts = Time.now()    
    ts = ts.iso.split()[0]
    
    log_file = path.join( config['log_directory'], \
                    config['log_root_name'] + '_' + ts + '.log' )
    return log_file

def end_day_log( log ):
    """Function to cleanly shutdown logging functions with last timestamped
    entry.
    Parameters:
        log     logger Object
    Returns:
        None
    """
    
    log.info( 'Processing complete\n' )
    logging.shutdown()

def lock( config, state, log ):
    """Method to create and release this script's lockfile and also to determine
    whether another lock file exists which may prevent this script operating.  
    
    Parameters:
        config    dictionary    Script configuration including parameters
                                log_directory  Directory path
                                lock_file      Name of the lock file
        state     string        Action to take, one of:
                                { lock, unlock, check }
        log       logger object Open logger
    
    Returns:
        state     string        Action taken, one of:
                                { lock_created, lock_removed, clashing_lock }
    """

    lock_file = path.join( config['log_directory'], config['lock_file'] )    

    if state == 'lock':
        lock = open(lock_file,'w')
        ts = datetime.utcnow()
        lock.write( ts.strftime("%Y-%m-%dT%H:%M:%S") )
        lock.close()
        log.info('Created lock file')
        return 'lock_created'
        
    elif state == 'unlock':
        if path.isfile(lock_file) == True:
            remove( lock_file )
            log.info('Removed lock file')
            return 'lock_removed'
            
    elif state == 'check':
        lock_list = [ config['lock_file'] ]
        for lock_name in lock_list:
            lock_file = path.join( config['log_directory'],lock_name )
            if path.isfile( lock_file ) == True:
                log.info('Clashing lock file encountered ( ' + lock_name + \
                                ' ), halting')
                end_day_log( log )
                return 'clashing_lock'
                
        log.info('Checked for clashing locks; found none')
        return 'unlocked'
        
def start_obs_record( config ):
    """Function to initialize or open a daily record of submitted observations"""
    
    log_file = get_log_path( config )
    
    tnow = datetime.utcnow()
    
    if path.isfile(log_file) == True:
        obsrecord = open(log_file,'a')
    else:
        obsrecord = open(log_file,'w')
        obsrecord.write('# Log of Requested Observation Groups\n')
        obsrecord.write('#\n')
        obsrecord.write('# Log started: ' + tnow.strftime("%Y-%m-%dT%H:%M:%S") + '\n')
        obsrecord.write('# Running at sba\n')
        obsrecord.write('#\n')
        obsrecord.write('# GrpID  TrackID  ReqID  Site  Obs  Tel  Instrum  Target  ReqType  RA(J2000)  Dec(J2000)  Filter  ExpTime  ExpCount  Cadence  Priority  TS_Submit  TS_Expire  TTL  FocusOffset  ReqOrigin  RCS_Report\n')
    return obsrecord
