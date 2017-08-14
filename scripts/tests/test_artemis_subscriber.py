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
import pytest
import api_tools

def test_read_config():
    """Function to verify that the artemis subscriber software can read its
    own config file correctly"""
    
    config = artemis_subscriber.read_config()
    assert len(config) > 0
    assert type(config) == type({})
    assert 'log_directory' in config.keys()
        
@pytest.mark.skip(reason="Rsync datalog test is time consuming")
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

@pytest.mark.skip(reason="Rsync all data test is time consuming")
def test_sync_artemis_data_db():
    
    config = artemis_subscriber.read_config()
    
    log = log_utilities.start_day_log( config, 'test_artemis_subscriber' )
    
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

def test_read_artemis_align_file():
    
    f = '../../data/OB170570.align'
    filt = 'I'
    params = artemis_subscriber.read_artemis_align_params(f,filt)
    assert params['g'] == 7.12221288e+01
    assert params['baseline'] == 19.16817
    assert params['name_code'] == 'OI'

    f = '../../data/OB171284.align'
    filt = 'I'
    params = artemis_subscriber.read_artemis_align_params(f,filt)
    assert params['g'] == 1.04522426e+04
    assert params['baseline'] == 15.43316
    assert params['name_code'] == 'OI'
    
def test_check_rsync_config():
    
    config = artemis_subscriber.read_config()
    
    log = log_utilities.start_day_log( config, 'test_artemis_subscriber' )
    
    status = artemis_subscriber.check_rsync_config(config,log=log)
    
    assert(status==True)
    
    log_utilities.end_day_log( log )

def test_list_data_files():
    
    config = artemis_subscriber.read_config()
    
    log = log_utilities.start_day_log( config, 'test_artemis_subscriber' )

    for data_type in ['model','data']:
        file_list = artemis_subscriber.list_data_files(config,data_type,log=log)
        assert data_type in file_list[0]
    
    log_utilities.end_day_log( log )

def test_event_data_check():
    
    config = artemis_subscriber.read_config()
    
    log = log_utilities.start_day_log( config, 'test_artemis_subscriber' )

    align_file = '../../data/OB170570.align'
    data_file = '../../data/OOB170570I.dat'
    model_file = '../../data/OB170570.model'
    status = artemis_subscriber.event_data_check(config,model_file=model_file,
                                                         log=log)
    assert status == True
    status = artemis_subscriber.event_data_check(config,align_file=align_file,
                                                         log=log)
    assert status == True
    status = artemis_subscriber.event_data_check(config,data_file=data_file,
                                                         log=log)
    assert status == True

    log_utilities.end_day_log( log )
    
def test_sync_data_align_files_with_db():
    
    config = artemis_subscriber.read_config()
    
    log = log_utilities.start_day_log( config, 'test_artemis_subscriber' )

    client = api_tools.connect_to_db(config,testing=config['testing'],
                                             verbose=config['verbose'])

    align_file = '../../data/OB170570.align'
    data_file = '../../data/OOB170570I.dat'
    
    response = artemis_subscriber.sync_data_align_files_with_db(client,config,
                                                                data_file,
                                                                align_file,log)
    
    assert 'True' in response
    
    log_utilities.end_day_log( log )

if __name__ == '__main__':
    test_sync_data_align_files_with_db()
    