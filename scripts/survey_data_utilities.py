# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 19:40:59 2016

@author: robouser
"""

#############################################################################
#               SURVEY DATA UTILITIES
#############################################################################

from os import path
from sys import argv, exit

def read_ogle_param_files( config ):
    """Function to read the listing of OGLE data"""
    
    ts_file_path = path.join( config['ogle_data_local_location'], \
                            config['ogle_time_stamp_file'] )
    par_file_path = path.join( config['ogle_data_local_location'], \
                            config['ogle_lenses_file'] )
    
    # Parse the timestamp in the last.changed file. The timestamp is given in yyyymmdd.daydecimal format:
    t = open( ts_file_path, 'r' ).readline()
    ts = datetime.strptime(t.split('.')[0],'%Y%m%d')
    dt = timedelta(days=float('0.'+t.split('.')[-1]))
    last_update = ts + dt
    verbose(config,'--> Last udpated at: '+t.replace('\n',''))

    # Parse the lenses parameter file.
    # First 2 lines are header, so skipped:
    file_lines = open( par_file_path, 'r' ).readlines()
    lens_params = {}
    for line in file_lines[2:]:
        (event_id, field, star, ra, dec, t0_hjd, t0_utc, tE, u0, A0, dmag, fbl, I_bl, I0) = line.split()
        if 'OGLE' not in event_id: event_id = 'OGLE-'+event_id
        (ra_deg, dec_deg) = utilities.sex2decdeg(ra,dec)
        event = Lens()
        event.set_par('name',event_id)
        event.set_par('ra',ra_deg)
        event.set_par('dec',dec_deg)
        event.set_par('t0',t0_hjd)
        event.set_par('te',tE)
        event.set_par('u0',u0)
        event.set_par('a0',A0)
        event.set_par('i0',I0)
        event.origin = 'OGLE'
        lens_params[event_id] = event
    verbose(config,'--> Downloaded index of ' + str(len(lens_params)) + ' events')

    return last_update, lens_params

def read_moa_param_files( config ):
    """Function to read the listing of MOA events"""
    
    ts_file_path = path.join( config['moa_data_local_location'], \
                            config['moa_time_stamp_file'] )
    par_file_path = path.join( config['moa_data_local_location'], \
                            config['moa_lenses_file'] )
 
    # Parse the timestamp in the last.changed file:
    t = open( ts_file_path, 'r' ).readline()
    ts = datetime.strptime(t.split('.')[0],'%Y%m%d')
    dt = timedelta(days=float('0.'+t.split('.')[-1]))
    last_update = ts + dt
    verbose(config,'--> Last udpated at: '+t.replace('\n',''))

def time_stamp_file( ts_file_path, format_string ):
    """Function to parse an ASCII file containig a single time stamp on line 1.
    format_string should indicate the expected structure of the timestamp in 
    the usual datetime notation, with the date and time separated by T.
    If the time is in decimal days, the format string should be ...TD
    Returns a datetime object
    """
    
    ts = None
    
    ( date_format, time_format ) = format_string.split('T')
    
    if path.isfile( ts_file_path ) == None:
        return ts
        
    t = open( ts_file_path, 'r' ).readline()
    
    if time_format == 'D':
        ts = datetime.strptime( t.split('.')[0], date_format )
        dt = timedelta(days=float('0.'+t.split('.')[-1]))
        ts = ts + dt

    else:
        ts = datetime.strptime( t, format_string )
    
    return ts
    