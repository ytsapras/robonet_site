# -*- coding: utf-8 -*-
"""
Created on Fri Aug 11 17:30:46 2017

@author: rstreet
"""

from os import getcwd, path, remove, environ
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'../..'))
systempath.append(path.join(cwd,'..'))
import api_tools
from datetime import datetime

def test_api_query_eventname():
    """Function to test the recording of a new event 
    by submitting it to the ROME/REA
    database via API. 
    
    Input parameters:
        event_pk    int   Event primary key
        eventname_pk   int   EventName primary key
    Returns:
        response    str    eventname_pk
    eventname_pk = -1 if the name is not recognized
    """

    config = {'db_user_id': 'rstreet', 'db_pswd': 'xxx'}
    client = api_tools.connect_to_db(config,testing=True,verbose=False)
    
    params = {'name': 'OGLE-2017-BLG-1516'}
    event_pk = 2289
    
    ts1 = datetime.utcnow()
    response = api_tools.contact_db(client,config,params,'query_eventname',testing=True)
    ts2 = datetime.utcnow()
    print(response+', time taken for query: '+str((ts2-ts1).total_seconds())+'s')
    assert int(response) == event_pk
    
if __name__ == '__main__':
    test_api_query_eventname()
