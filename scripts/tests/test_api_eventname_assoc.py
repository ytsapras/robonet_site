# -*- coding: utf-8 -*-
"""
Created on Tue Aug  8 22:58:52 2017

@author: rstreet
"""

from os import getcwd, path, remove, environ
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'../..'))
systempath.append(path.join(cwd,'..'))
import api_tools
from datetime import datetime

def test_api_eventname_assoc():
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
    
    params = {'name': 'OGLE-2017-BLG-1515',\
              'ev_ra': '17:28:03.84', 'ev_dec': '-29:01:25.20'}
    
    ts1 = datetime.utcnow()
    response = api_tools.contact_db(client,config,params,'query_eventname_assoc',testing=True)
    ts2 = datetime.utcnow()
    print(response+', time taken for query: '+str((ts2-ts1).total_seconds())+'s')
    
if __name__ == '__main__':
    test_api_eventname_assoc()
