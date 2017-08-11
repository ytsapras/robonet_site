# -*- coding: utf-8 -*-
"""
Created on Wed Aug  9 17:10:58 2017

@author: rstreet
"""

from os import getcwd, path, remove, environ
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'../..'))
systempath.append(path.join(cwd,'..'))
import api_tools
from datetime import datetime

def test_query_operator():
    """Function to test the API query for the ID of the survey operator
    providing the event detections.
    
    Response is a single string containing the operator's primary key and name.
    If the operator is not one of the main recognized surveys, 'OTHER' 
    is returned.
    
    Input parameters:
        name     str     Survey name from the prefix of a long-format event name
    Returns:
        response    str   operator_id<space>operator_name
    """
    config = {'db_user_id': 'rstreet', 'db_pswd': 'xxx'}
    client = api_tools.connect_to_db(config,testing=True,verbose=False)
    
    params = {'name': 'OGLE'}
    ts1 = datetime.utcnow()
    response = api_tools.contact_db(client,config,params,'query_operator',testing=True)
    ts2 = datetime.utcnow()
    print(response+', time taken for query: '+str((ts2-ts1).total_seconds())+'s')
    assert '1' in response
    
    params = {'name': 'KMTNET'}
    ts1 = datetime.utcnow()
    response = api_tools.contact_db(client,config,params,'query_operator',testing=True)
    ts2 = datetime.utcnow()
    print(response+', time taken for query: '+str((ts2-ts1).total_seconds())+'s')
    assert '3' in response
    
    params = {'name': 'FOO'}
    ts1 = datetime.utcnow()
    response = api_tools.contact_db(client,config,params,'query_operator',testing=True)
    ts2 = datetime.utcnow()
    print(response+', time taken for query: '+str((ts2-ts1).total_seconds())+'s')
    assert '7' in response
    
if __name__ == '__main__':
    test_query_operator()