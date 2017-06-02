# -*- coding: utf-8 -*-
"""
Created on Sat Mar 18 12:16:03 2017

@author: rstreet
"""

from os import getcwd, path
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'..'))
import config_parser

def test_config_has_content():
    """Test that when we parse a standard-format config file, the
    dictionary returned has non-zero-length content"""
    
    config_file_path = path.join('../../configs','obscontrol_config.xml')
    config = config_parser.read_config(config_file_path)
    assert len(config) > 0

def test_config_params():
    """Test that example parameters are being correctly read from 
    the XML config file"""
    
    config_file_path = path.join('../../configs','obscontrol_config.xml')
    config = config_parser.read_config(config_file_path)
    
    assert 'log_directory' in config.keys()

def test_config_for_code():
    """Test the function to resolve the name of a piece of software and
    pick up the correct configuration file
    """
    
    config = config_parser.read_config_for_code('obs_control')
    assert len(config) > 0
    assert 'log_directory' in config.keys()
    