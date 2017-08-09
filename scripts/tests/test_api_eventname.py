# -*- coding: utf-8 -*-
"""
Created on Tue Aug  8 15:02:57 2017

@author: rstreet
"""

from os import getcwd, path, remove, environ
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'../..'))
systempath.append(path.join(cwd,'..'))
import api_tools

def test_api_eventname():
    """Function to test the recording of a new event 
    by submitting it to the ROME/REA
    database via API. """
    
    params = {'name': 'OGLE-2017-BLG-1516'}
    config = {'db_user_id': 'rstreet', \
                'db_pswd': 'skynet1186'}
    response = api_tools.query_eventname(config,params,testing=True)
    print(response)
    
if __name__ == '__main__':
    test_api_eventname()
