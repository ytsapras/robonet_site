# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 19:40:59 2016

@author: robouser
"""

from os import path
from sys import argv, exit
import utilities
from datetime import datetime, timedelta
import event_classes
import survey_classes
import glob

def read_ogle_param_files( config ):
    """Function to read the listing of OGLE data"""
    
    ts_file_path = path.join( config['ogle_data_local_location'], \
                            config['ogle_time_stamp_file'] )
    par_file_path = path.join( config['ogle_data_local_location'], \
                            config['ogle_lenses_file']+'.*' )
    lens_file_list = glob.glob( par_file_path )
    updated_file_path = path.join( config['ogle_data_local_location'], \
                            config['ogle_updated_file'] )
    ogle_data = survey_classes.SurveyData()
                            
    # Parse the timestamp in the last.changed file. The timestamp is given in yyyymmdd.daydecimal format:
    ogle_data.last_changed = time_stamp_file( ts_file_path, "%Y%m%dTD" )
    
    # Parse the lenses parameter file.
    # First 2 lines are header, so skipped:
    ogle_data.lenses = {}
    for par_file in lens_file_list:
        file_lines = open( par_file, 'r' ).readlines()
        for line in file_lines[2:]:
            (event_id, field, star, ra, dec, t0_hjd, t0_utc, tE, u0, A0, \
            dmag, fbl, I_bl, I0) = line.split()
            if 'OGLE' not in event_id: event_id = 'OGLE-'+event_id
            event = event_classes.Lens()
            event.set_par('name',event_id)
            event.set_par('survey_id',field)
            event.set_par('ra',ra)
            event.set_par('dec',dec)
            event.set_par('t0',t0_hjd)
            event.set_par('te',tE)
            event.set_par('u0',u0)
            event.set_par('a0',A0)
            event.set_par('i0',I0)
            event.origin = 'OGLE'
            ogle_data.lenses[event_id] = event
                
    ogle_data.last_updated = read_update_file( updated_file_path )
    
    return ogle_data

def read_moa_param_files( config ):
    """Function to read the listing of MOA events"""
    
    ts_file_path = path.join( config['moa_data_local_location'], \
                            config['moa_time_stamp_file'] )
    par_file_path = path.join( config['moa_data_local_location'], \
                            config['moa_lenses_file'] )
    updated_file_path = path.join( config['moa_data_local_location'], \
                            config['moa_updated_file'] )
    moa_data = survey_classes.SurveyData()
 
    # Parse the timestamp in the last.changed file:
    moa_data.last_changed = time_stamp_file( ts_file_path, "%Y-%m-%dT%H:%M:%S" )
    
    # Parse the moa_lenses parameter file:
    file_lines = open( par_file_path, 'r' ).readlines()
    moa_data.lenses = {}
    for line in file_lines:
        if line.lstrip()[0:1] != '#': 
            (event_id, field, ra, dec, t0_hjd, tE, u0, A0, I0, c) = line.split()
            if type(ra) == type(1.0):
                (ra_str, dec_str) = utilities.decdeg2sex(ra,dec)
            else:
                ra_str = ra
                dec_str = dec
            event = event_classes.Lens()
            event.set_par('name',event_id)
            event.set_par('survey_id',field)
            event.set_par('ra',ra_str)
            event.set_par('dec',dec_str)
            event.set_par('t0',t0_hjd)
            event.set_par('te',tE)
            event.set_par('u0',u0)
            event.set_par('a0',A0)
            event.set_par('i0',I0)
            event.set_par('classification',c)
            event.origin = 'MOA'
            moa_data.lenses[event_id] = event
    
    moa_data.last_updated = read_update_file( updated_file_path )
    
    return moa_data
    
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
    t = t.replace('\n','').lstrip()
    
    if time_format == 'D':
        ts = datetime.strptime( t.split('.')[0], date_format )
        dt = timedelta(days=float('0.'+t.split('.')[-1]))
        ts = ts + dt

    else:
        ts = datetime.strptime( t, format_string )
    
    return ts

def write_update_file( file_path ):
    """Function to write a timestamp file containing the timestamp at which
    the data for a given survey was last downloaded"""
    
    fileobj = open( file_path, 'w' )
    ts = datetime.utcnow()
    fileobj.write( ts.strftime("%Y-%m-%dT%H:%M:%S") + ' UTC\n' )
    fileobj.close()
    
    return ts
    
def read_update_file( file_path ):
    """Function to read the timestamp of when a survey's data was last
    downloaded"""
    
    if path.isfile( file_path ) == True:
        fileobj = open( file_path, 'r' )
        line = fileobj.readline()
        fileobj.close()
        ts = datetime.strptime( line.split()[0], "%Y-%m-%dT%H:%M:%S" )
    else:
        ts = None
        
    return ts