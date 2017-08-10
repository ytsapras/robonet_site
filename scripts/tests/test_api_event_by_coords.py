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
    
    params = {'ev_ra': '18:00:00',\
	      'ev_dec': '-30:00:00'}
    config = {'db_user_id': 'rstreet', \
                'db_pswd': 'xxx'
                }
    response = api_tools.contact_db(config,params,'query_event_by_coords',testing=True)
    assert '386' in response
    print(response)

    search = False
    if search == True:
        params = {'ev_ra': '-17:26:49.06',\
    	      'ev_dec': '-29:33:59.00'}
        response = api_tools.contact_db(config,params,'query_event_by_coords',testing=True)
        assert response == -1

if __name__ == '__main__':
    test_api_event_by_coords()
