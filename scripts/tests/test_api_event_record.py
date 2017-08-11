# -*- coding: utf-8 -*-
"""
Created on Wed Jun 7 09:45 2017

@author: ytsapras, rstreet
"""

from os import getcwd, path, remove, environ
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'../..'))
systempath.append(path.join(cwd,'..'))
from datetime import datetime, timedelta
import api_tools

def test_api_event_record():
    """Function to test the recording of a new event 
    by submitting it to the ROME/REA
    database via API. 
    Required parameters:
        config    dict    script configuration parameters
        params    dict    event request parameters, including
        field_name       str
        operator_name    str
        ev_ra            str
        ev_dec           str
        status           str
        anomaly rank     float
        year             str
    """
    config = {'db_user_id': 'rstreet', 'db_pswd': 'xxx'}
    client = api_tools.connect_to_db(config,testing=True,verbose=False)

    params = {'field': '21',\
              'operator': '1',\
              'ev_ra': '18:00:00',\
	      'ev_dec': '-30:00:00',\
	      'status':'NF',\
	      'anomaly_rank': -1.0,\
	      'year': '2017'
    
         }
    ts1 = datetime.utcnow()
    response = api_tools.contact_db(client,config,params,'add_event',
                                    testing=True)
    ts2 = datetime.utcnow()
    print(response+', time taken for query: '+str((ts2-ts1).total_seconds())+'s')
    
if __name__ == '__main__':
    test_api_event_record()
