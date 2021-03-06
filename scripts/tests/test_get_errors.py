# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 12:11:25 2017

@author: rstreet
"""
from os import getcwd, path
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'..'))
import get_errors
import config_parser

def test_update_errs():
    """Function to test the function to update the error reports"""
    
    config = config_parser.read_config_for_code('obs_control')
    file_out = path.join(config['log_directory'],'errors.txt')
    comment = 'TEST'
    get_errors.update_err('backup', comment)
    assert path.isfile(file_out)
    
    file_lines = open(file_out,'r').readlines()
    assert comment in file_lines[-1]

def test_read_errors():
    """Function to test the function to read the error report"""
    
    errors = get_errors.read_err()
    assert len(errors) > 0
    
    code_list = ['artemis_subscriber','obs_control_rome','obs_control_rea',\
                'run_rea_tap','reception','backup']
    e = get_errors.Error()
    for err in errors:
        assert err.codename in code_list
        assert type(err) == type(e)