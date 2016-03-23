# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 21:57:57 2016

@author: robouser
"""
import config_parser
from astropy.time import Time
import subprocess
from sys import exit
from os import path, stat
#import update_db
import utilities
import log_utilities
from datetime import datetime, timedelta
import ftplib
import survey_data_utilities
import event_classes
import survey_classes


def test_cron():
    
    fileobj = open('/home/robouser/cron_test.dat','w')
    t = datetime.utcnow()
    fileobj.write( t.strftime("%Y-%m-%dT%H:%M:%S") + '\n' )
    fileobj.write('Completed imports\n')
    
    # Read configuration:
    config_file_path = '/home/robouser/.robonet_site/surveys_sync.xml'
    fileobj.write('Found config file: ' + str(path.isfile(config_file_path))+'\n')
    config = config_parser.read_config(config_file_path)
    fileobj.write('Parsed config\n')
    log = log_utilities.start_day_log( config, __name__ )
    fileobj.write('Started log\n')
    log.info('Started sync with surveys server')
    log_utilities.end_day_log( log )
    fileobj.write('Parsed config, started log')    
    
    fileobj.close()
    
if __name__ == '__main__':
    test_cron()