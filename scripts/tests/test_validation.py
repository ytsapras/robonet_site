# -*- coding: utf-8 -*-
"""
Created on Tue Mar 21 15:36:47 2017

@author: rstreet
"""

from os import getcwd, path, remove
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'..'))
import validation

def test_test_type():
    """Function to test the function to test the type of a set of parameters"""
    
    par_list = ['foo', 'bar', 'wibble']
    params = {'foo': 'george', 'bar': 'paul', 'wibble': 'ringo'}
    t = str
    (status, msg) = validation.test_type(par_list,t,params)
    assert status == True