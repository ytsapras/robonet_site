# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 16:56:05 2017

@author: rstreet
"""

from os import getcwd, path, remove, environ, makedirs, stat
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'..'))
import artemis_subscriber
import log_utilities
import glob
from datetime import datetime, timedelta
import survey_subscriber
import event_classes

def test_ogle_download():
    """Function to test that the download of data on events discovered from the
    OGLE server works as expected"""
    
    config = {'log_directory': '.',
              'log_root_name': 'test_ogle_download',
              'ogle_ftp_server': 'ftp.astrouw.edu.pl',
              'ogle_data_local_location': './surveys/OGLE',
              'ogle_time_stamp_file': 'last.changed',
              'ogle_lenses_file': 'lenses.par',
              'subscribe_ogle': 1,
              'version': 'test',
              'update_db': 0,
              'years': '2017',
            }
    if path.isdir(config['ogle_data_local_location']) == False:
        makedirs(config['ogle_data_local_location'])
        
    log = survey_subscriber.init_log(config)
    survey_subscriber.get_ogle_parameters(config, log)
    
    file_list = glob.glob(path.join(config['ogle_data_local_location'],'*'))
    
    f = path.join(config['ogle_data_local_location'],'last.changed')
    assert f in file_list
    
    mtime = datetime.fromtimestamp(path.getmtime(f))
    tlimit = datetime.utcnow() - timedelta(minutes=2.0)
    assert mtime > tlimit
    
    year = datetime.utcnow().year
    f = path.join(config['ogle_data_local_location'],'lenses.par.'+str(year))
    assert f in file_list
    
    mtime = datetime.fromtimestamp(path.getmtime(f))
    tlimit = datetime.utcnow() - timedelta(minutes=2.0)
    assert mtime > tlimit

def test_moa_download():
    """Function to test the harvesting of data from MOA.
    MOA's alert website appears to be offline, so this is currently 
    non-functional
    """
    
    config = {'log_directory': '.',
              'log_root_name': 'test_moa_download',
              'years': '2017',
              'version': 'test',
              'update_db': 0,
              'subscribe_moa': 0
             }
    if int(config['subscribe_moa']) == 1:
        log = survey_subscriber.init_log(config)
        (events_index_data, alerts_page_data) = survey_subscriber.get_moa_parameters(config, log)
    else:
        events_index_data = []
        alerts_page_data = []

    assert len(events_index_data) == 0
    assert len(alerts_page_data) == 0
    
if __name__ == '__main__':
    test_moa_download()