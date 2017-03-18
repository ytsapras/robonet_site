# -*- coding: utf-8 -*-
"""
Created on Sat Mar 18 12:16:03 2017

@author: rstreet
"""

import unittest
from os import getcwd, path
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'..'))
import config_parser

class TestConfigParser(unittest.TestCase):
    """Tests of the configuration parser"""
    
    def test_config_has_content(self):
        """Test that when we parse a standard-format config file, the
        dictionary returned has non-zero-length content"""
        
        config_file_path = path.join('../../configs','obscontrol_config.xml')
        config = config_parser.read_config(config_file_path)
        self.assertTrue(len(config) > 0)
    
    def test_config_params(self):
        """Test that example parameters are being correctly read from 
        the XML config file"""
        
        config_file_path = path.join('../../configs','obscontrol_config.xml')
        config = config_parser.read_config(config_file_path)
        
        self.assertIn('logdir',config.keys())


if __name__ == '__main__':
    unittest.main()