# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 21:57:57 2016

@author: robouser
"""
import k2_footprint_class
from datetime import datetime
import log_utilities
from os import chdir, environ
from commands import getstatusoutput

def test_cron():
    
    fileobj = open('/home/robouser/cron_test.dat','w')
    t = datetime.utcnow()
    fileobj.write( t.strftime("%Y-%m-%dT%H:%M:%S") + '\n' )
    fileobj.write('Completed imports\n')
    fileobj.flush()
    
    config = { 'k2_footprint_data': \
                '/home/robouser/Software/robonet_site/data/k2-footprint.json',
               'xsuperstamp_target_data': \
               '/home/robouser/Software/robonet_site/data/xsuperstamp_targets.json', 
               'ddt_target_data': \
               '/home/robouser/Software/robonet_site/data/c9-ddt-targets-preliminary.csv',
               'tmp_location': \
               '/science/robonet/rob/Operations/ExoFOP', \
               'k2_campaign': 9, \
               'k2_year': 2016, \
               'log_directory': '/science/robonet/rob/Operations/ExoFOP', \
               'log_root_name': 'test_cron'
              }
    fileobj.write('Set up config\n')
    log = log_utilities.start_day_log( config, __name__, console=False )
    fileobj.write('Started logging\n')
    log.info('Started logging')
    environ['DISPLAY'] = ':99'
    environ['PWD'] = '/science/robonet/rob/Operations/ExoFOP/'
    chdir(environ['PWD'])
    log.info(str(environ.items()))
    fileobj.write( str(environ.items())+ '\n')
    
    #pkg_path = '/opt/anaconda.2.5.0/bin/K2onSilicon'
    #chdir('/science/robonet/rob/Operations/ExoFOP')
    #target_file = 'target.csv'
    #output_file = '/science/robonet/rob/Operations/ExoFOP/targets_siliconFlag.cav'
    comm = '/opt/anaconda.2.5.0/bin/K2onSilicon /science/robonet/rob/Operations/ExoFOP/target.csv 9'
    #( iexec, coutput ) = getstatusoutput( pkg_path + ' ' + target_file + \
     #               ' ' + str(config['k2_campaign']) )
    ( iexec, coutput ) = getstatusoutput( comm )
    log.info(coutput + '\n')
    log.info('Loaded K2 data')
    
    fileobj.write(coutput + '\n')
    fileobj.write('Loaded K2 Campaign data\n')   
    fileobj.flush() 
    
    fileobj.close()
    log_utilities.end_day_log( log )
    
if __name__ == '__main__':
    test_cron()