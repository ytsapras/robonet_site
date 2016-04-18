# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 21:14:21 2016

@author: robouser
"""

import glob
from os import path

def load_pylima_output( configs, log=None, renamed=None ):
    """Function to load the output of PyLIMA's fits. 
    Note the event naming convention follows ARTEMiS, so renamed events 
    must be parsed    
    """
    
    pylima_data = {}
    
    file_list = glob.glob( path.join( configs['pylima_directory'], '*.params' ) )
        
    for par_file in file_list:
        event_name = path.basename(par_file).split('_')[0]
        if renamed != None and event_name in renamed.keys():
            event_name = renamed[event_name]
            log.info('-> Switched name of event renamed by ARTEMiS to '+\
                             event_name)
        params = read_pylima_par_file( par_file )
        
        pylima_data[event_name] = params
    
    if log != None:
        log.info('Read PyLIMA model parameters for ' + str(len(pylima_data)) \
                        + 'events')
                        
    return pylima_data 
    
def read_pylima_par_file( par_file ):
    """Function to read the PyLIMA parameter files"""
    
    parse_keys = { 'AO': 'A0', 'TO': 'T0', 'UO': 'U0' }    
    
    params = {}
    file_lines = open( par_file, 'r' ).readlines()
    for line in file_lines:
        if line[0:1] != '#':
            (key, value) = line.replace('\n','').split()
            key = key.replace('.','_')
            for ikey, replace_key in parse_keys.items():
                if ikey in key:
                    key = key.replace(ikey,replace_key)
            value = float(value)
            if key == 'PYLIMA_TO': value = value + 2450000.0
            params[key] = value
    return params

if __name__ == '__main__':
    configs = {}
    configs['pylima_directory'] = '/science/robonet/rob/Operations/PyLIMA'
    
    pylima_data = load_pylima_output( configs )
    
    for event, data in pylima_data.items():
        print event, ': ',data