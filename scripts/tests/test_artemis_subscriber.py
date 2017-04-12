# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 14:25:45 2017

@author: rstreet
"""

from os import getcwd, path, remove, environ
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'..'))
import artemis_subscriber
import log_utilities
import glob
from datetime import datetime
import event_classes

def test_read_config():
    """Function to verify that the artemis subscriber software can read its
    own config file correctly"""
    
    config = artemis_subscriber.read_config()
    assert len(config) > 0
    assert type(config) == type({})
    assert 'log_directory' in config.keys()
        
def test_rsync_data_log():
    """Function to verify that data can be downloaded from ARTEMiS"""
    
    config = artemis_subscriber.read_config()
    
    clear_test_directory(config['models_local_location'])
    
    artemis_subscriber.rsync_data_log(config,'model')
    
    file_list = glob.glob(path.join(config['models_local_location'],'*.model'))
    
    assert len(file_list) > 0

def clear_test_directory(dir_path):
    file_list = glob.glob(path.join(dir_path,'*'))
    if len(file_list) > 0:
        for f in file_list:
            remove(f)
    
def test_sync_artemis_data_db():
    
    config = artemis_subscriber.read_config()
    
    log = log_utilities.start_day_log( config, '_test_artemis_subscriber' )
    
    clear_test_directory(config['models_local_location'])
    
    artemis_subscriber.sync_artemis_data_db(config,'model',log)
    
    file_list = glob.glob(path.join(config['models_local_location'],'*.model'))
    
    log_utilities.end_day_log( log )
    
    assert len(file_list) > 0

def test_read_artemis_model_file():
    
    f = '../../data/OB120970.model'
    (event, last_modified) = artemis_subscriber.read_artemis_model_file(f)
    test_event = event_classes.Lens()
    ts = datetime.utcnow()
    
    assert type(event) == type(test_event)
    assert type(last_modified) == type(ts)

def test_sync_model_file_with_db():
    
    config = artemis_subscriber.read_config()
    
    log = log_utilities.start_day_log( config, '_test_artemis_subscriber' )
    
    f = '../../data/OB120970.model'

    artemis_subscriber.sync_model_file_with_db(config,f,log)
    
    log_utilities.end_day_log( log )
    
    assert 1 == 2