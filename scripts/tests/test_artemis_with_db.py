# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 15:57:50 2017

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

def test_sync_model_file_with_db():
    
    config = artemis_subscriber.read_config()
    
    log = log_utilities.start_day_log( config, '_test_artemis_subscriber' )
    
    f = '../../data/OB120970.model'
    log.info('Using test model file: '+f)
    
    artemis_subscriber.sync_model_file_with_db(config,f,log,debug=True)
    
    log_utilities.end_day_log( log )
    

if __name__ == '__main__':
    
    test_sync_model_file_with_db()