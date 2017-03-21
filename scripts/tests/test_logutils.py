# -*- coding: utf-8 -*-
"""
Created on Sat Mar 18 16:06:03 2017

@author: rstreet
"""

from os import getcwd, path, remove
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'..'))
import config_parser, log_utilities
from astropy.time import Time

def test_log_start():
    """Verify that the initialization function correctly starts
    a date-stamped log file"""
    
    config = {'log_directory': '.',
              'log_root_name': 'test'}
    log = log_utilities.start_day_log( config, 'test' )
    
    ts = Time.now()    
    ts = ts.iso.split()[0]
    log_file = path.join( config['log_directory'], \
                config['log_root_name'] + '_' + ts + '.log' )
                
    assert path.isfile(log_file) == True
    log_utilities.end_day_log( log )
    remove(log_file)
        
def test_log_name():
    """Function to verify that the logs are correctly date-stamped"""
    
    config = {'log_directory': '.',
              'log_root_name': 'test'}
    ts = Time.now()    
    ts = ts.iso.split()[0]
    log_file = path.join( config['log_directory'], \
                config['log_root_name'] + '_' + ts + '.log' )
    chk_log_file = log_utilities.get_log_path(config, config['log_root_name'])
    assert log_file == chk_log_file
    
def test_lock_functions():
    """Test the function that creates and checks for a lockfile"""

    config = {'log_directory': '.',
              'log_root_name': 'test',
              'lock_file': 'test.lock'}
    log = log_utilities.start_day_log( config, 'test' )
    
    lock_state = log_utilities.lock( config, 'check', log )
    assert lock_state=='unlocked'
    
    log_path = log_utilities.get_log_path(config, config['log_root_name'])
    log_data = open(log_path,'r').readlines()
    assert 'Checked for clashing locks; found none' in log_data[-1]
    
    lock_state = log_utilities.lock( config, 'lock', log )
    assert lock_state=='lock_created'
    assert path.isfile(path.join(config['log_directory'],config['lock_file']))

    lock_state = log_utilities.lock( config, 'check', log )
    assert lock_state=='clashing_lock'
    
    lock_state = log_utilities.lock( config, 'unlock', log )
    assert lock_state=='lock_removed'
    assert path.isfile(path.join(config['log_directory'],config['lock_file'])) == False
    log_utilities.end_day_log( log )
    remove(log_path)
    
def test_obsrecord_start():
    """Verify that the initialization function correctly starts
    a date-stamped log file"""
    
    config = {'log_directory': '.',
              'log_root_name': 'Obsrecord'}
    log = log_utilities.start_obs_record( config )
    
    ts = Time.now()    
    ts = ts.iso.split()[0]
    log_file = path.join( config['log_directory'], \
                config['log_root_name'] + '_' + ts + '.log' )
                
    assert path.isfile(log_file) == True
    remove(log_file)
    