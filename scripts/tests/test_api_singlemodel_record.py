# -*- coding: utf-8 -*-
"""
Created on Mon Jun 12 09:45 2017

@author: ytsapras
"""

from os import getcwd, path, remove, environ
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'../..'))
systempath.append(path.join(cwd,'..'))
from datetime import datetime, timedelta
import api_tools

def test_api_singlemodel_record():
    """Function to test the recording of a new Single Model 
    by submitting it to the ROME/REA
    database via API. """
    
    params = {'event': '1',\
	      'Tmax':2457916.8491,\
	      'e_Tmax':10.0,\
	      'tau':30.0,\
	      'e_tau':1.0,\
	      'umin':0.1,\
	      'e_umin':0.001,\
	      'modeler':'TESTER',\
	      'last_updated':datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
             }
    config = {'db_user_id': 'rstreet', \
                'db_pswd': 'xxx'
                }
    response = api_tools.contact_db(config,params,'add_singlemodel',testing=True)
    print(response)
    
if __name__ == '__main__':
    test_api_singlemodel_record()
