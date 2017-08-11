# -*- coding: utf-8 -*-
"""
Created on Wed Jun 8 18:45 2017

@author: ytsapras
"""

from os import getcwd, path, remove, environ
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'../..'))
systempath.append(path.join(cwd,'..'))
from datetime import datetime, timedelta
import api_tools

def test_api_eventname_record():
    """Function to test the recording of a new eventname 
    by submitting it to the ROME/REA
    database via API. """

    config = {'db_user_id': 'rstreet', 'db_pswd': 'xxx'}
    client = api_tools.connect_to_db(config,testing=True,verbose=False)
        
    params = {'event': '1',\
              'operator': '1',\
              'name': 'OGLE-2525-BLG-9999'
    
         }
    ts1 = datetime.utcnow()
    response = api_tools.contact_db(client,config,params,
                                                 'add_eventname',testing=True)
    ts2 = datetime.utcnow()
    print(response+', time taken for query: '+str((ts2-ts1).total_seconds())+'s')
    
if __name__ == '__main__':
    test_api_eventname_record()
