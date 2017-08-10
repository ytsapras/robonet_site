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
    
    config = {'db_user_id': 'rstreet', \
                'db_pswd': 'xxx'}
                
    params = {'name': 'OGLE'}
    response = api_tools.contact_db(config,params,'query_operator',testing=True)
    print(response)
    assert '1' in response
    
    params = {'name': 'KMTNET'}
    response = api_tools.contact_db(config,params,'query_operator',testing=True)
    print(response)
    assert '3' in response
    
    params = {'name': 'FOO'}
    response = api_tools.contact_db(config,params,'query_operator',testing=True)
    print(response)
    assert '7' in response
    
if __name__ == '__main__':
    test_query_operator()