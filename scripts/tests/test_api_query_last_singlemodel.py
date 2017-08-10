# -*- coding: utf-8 -*-
"""
Created on Wed Aug  9 23:25:20 2017

@author: rstreet
"""

from os import getcwd, path, remove, environ
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'../..'))
systempath.append(path.join(cwd,'..'))
import api_tools

def test_api_query_last_singlemodel():
    """Function to test the API to return the last known singlemodel
    for an event from the DB.  
    
    Input parameters:
        event    int   Event
        modeler   str   Name of modeler
    Returns:
        response    str    singlemodel_pk<space>datetime
    eventname_pk = -1 if the name is not recognized
    """
    
    params = {'event': 2016,\
              'modeler': 'ARTEMiS'}
    config = {'db_user_id': 'rstreet', \
                'db_pswd': 'xxx'}
    response = api_tools.contact_db(config,params,'query_last_singlemodel',testing=True)
    print(response)
    
if __name__ == '__main__':
    test_api_query_last_singlemodel()
