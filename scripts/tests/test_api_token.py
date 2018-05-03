# -*- coding: utf-8 -*-
"""
Created on Tue May  1 14:56:15 2018

@author: rstreet
"""

from os import getcwd, path
from sys import path as systempath
from sys import argv
cwd = getcwd()
systempath.append(path.join(cwd,'../..'))
systempath.append(path.join(cwd,'..'))
import api_tools
from datetime import datetime, timedelta

def test_api_token(token):
    """Function to test the retrieval of observation sets from the DB
    that match specific parameter sets given."""
    
    data = {}
    end_point = 'test_token'
    
    response = api_tools.talk_to_db(data,end_point,token,
                                    testing=True,verbose=True)
    
    print response
    
if __name__ == '__main__':
    
    if len(argv) == 1:
        
        token = raw_input('Please enter user token: ')
        
    else:
        
        token = argv[1]
    
    test_api_token(token)