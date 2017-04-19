# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 11:18:51 2017

@author: rstreet
"""

from os import getcwd, path, remove, environ
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'..'))
import utilities

def test_coord_convert():
    """Function to test the coordinate utility functions"""
    
    ra_str = '17:23:24.5'
    dec_str = '-30:23:24.5'
    ra_deg = 260.8520833333333
    dec_deg = -30.390138888888888
    
    (test_ra_deg,test_dec_deg) = utilities.sex2decdeg(ra_str,dec_str)
    assert test_ra_deg == ra_deg
    assert test_dec_deg == dec_deg
    
    (test_ra_str, test_dec_str) = utilities.decdeg2sex(ra_deg,dec_deg)
    assert test_ra_str == ra_str
    assert test_dec_str == dec_str