# -*- coding: utf-8 -*-
"""
Created on Tue Aug  8 14:08:06 2017

@author: rstreet
"""


from os import getcwd, path, remove, environ
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'../..'))
systempath.append(path.join(cwd,'..'))
import api_tools
from datetime import datetime

def test_api_event_by_coords():
    """Function to test the recording of a new event 
    by submitting it to the ROME/REA
    database via API. 
    Input parameters:
        ra      str   RA in sexigesimal format
        dec     str   Dec in sexigesimal format
    Returns:
        response    str    event_pk
    event_pk = -1 if no event is known at those coordinates.     
    """
    config = {'db_user_id': 'rstreet', \
                'db_pswd': 'xxx'}
    client = api_tools.connect_to_db(config,testing=True,verbose=False)
    
    params = {'ev_ra': '18:00:00',\
	      'ev_dec': '-30:00:00'}
    ts1 = datetime.utcnow()
    response = api_tools.contact_db(client,config,params,'query_event_by_coords',testing=True)
    ts2 = datetime.utcnow()
    print(response+', time taken for query: '+str((ts2-ts1).total_seconds())+'s')
    assert '386' in response


    params = {'ev_ra': '17:53:44.39',\
	      'ev_dec': '-34:13:16.63'}
    ts1 = datetime.utcnow()
    response = api_tools.contact_db(client,config,params,'query_event_by_coords',testing=True)
    ts2 = datetime.utcnow()
    print(response+', time taken for query: '+str((ts2-ts1).total_seconds())+'s')
    assert '2' in response
    
    search = False
    if search == True:
        params = {'ev_ra': '-17:26:49.06',\
    	      'ev_dec': '-29:33:59.00'}
        ts1 = datetime.utcnow()
        response = api_tools.contact_db(client,config,params,'query_event_by_coords',testing=True)
        ts2 = datetime.utcnow()
        print(response+', time taken for query: '+str((ts2-ts1).total_seconds())+'s')
        assert response == -1

if __name__ == '__main__':
    test_api_event_by_coords()
