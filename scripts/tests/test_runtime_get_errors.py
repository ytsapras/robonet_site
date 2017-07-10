# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 15:39:18 2017

@author: rstreet
"""

from os import getcwd, path
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'..'))
import get_errors

def test_get_errors_runtime():
    """Function to test get_errors at runtime"""
    
    get_errors.update_err('obs_control_rea', 'FOO')
    errors = get_errors.read_err()
    for err in errors:
        print err.summary()

if __name__ == '__main__':
    test_get_errors_runtime()