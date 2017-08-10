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
    database via API. 
    
    Input parameters:
        name    str   Event name in long format
    Returns:
        response    str    eventname_pk
    eventname_pk = -1 if the name is not recognized
    """
    
    params = {'name': 'OGLE-2017-BLG-1516',
              'event': 2016,
              'operator': 1}
    config = {'db_user_id': 'rstreet', \
                'db_pswd': 'xxx'}
    response = api_tools.contact_db(config,params,'add_eventname',testing=True)
    print(response)
    
if __name__ == '__main__':
    test_api_eventname()
