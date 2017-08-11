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
from datetime import datetime

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
    config = {'db_user_id': 'rstreet', 'db_pswd': 'xxx'}
    client = api_tools.connect_to_db(config,testing=True,verbose=False)
    
    params = {'event': 2016,\
              'modeler': 'ARTEMiS'}
              
    ts1 = datetime.utcnow()
    response = api_tools.contact_db(client,config,params,'query_last_singlemodel',testing=True)
    ts2 = datetime.utcnow()
    print(response+', time taken for query: '+str((ts2-ts1).total_seconds())+'s')
    
if __name__ == '__main__':
    test_api_query_last_singlemodel()
