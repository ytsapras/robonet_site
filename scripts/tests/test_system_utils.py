# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 09:30:36 2019

@author: rstreet
"""

from os import getcwd, path, remove, environ
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'..'))
import system_utils
from datetime import datetime

def test_check_for_running_code():
    
    time_running = system_utils.check_for_running_code('test_system_utils.py')

    assert type(time_running) == type(datetime.now())

    time_running = system_utils.check_for_running_code('no_such_code')
    
    assert time_running == None

    time_running = system_utils.check_for_running_code('no_such_code')

def test_check_for_multiple_instances():
    
    result = system_utils.check_for_multiple_instances('/usr')
    
    assert result == True
    
    result = system_utils.check_for_multiple_instances('test_system_utils.py')
    
    assert result == False
    
    
if __name__ == '__main__':
    
    #test_check_for_running_code()
    test_check_for_multiple_instances()