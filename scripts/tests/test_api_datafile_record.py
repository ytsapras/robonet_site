# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 14:03:37 2017

@author: ytsapras, rstreet
"""

from os import getcwd, path, remove, environ
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'../..'))
systempath.append(path.join(cwd,'..'))
from datetime import datetime, timedelta
import api_tools

def test_api_datafile_record():
    """Function to test the recording of a new ARTEMiS DataFile 
    request (submitted to the LCO network) by submitting it to the ROME/REA
    database via API. 
    Required parameters:
        config    dict    script configuration parameters
        params    dict    datafile parameters, including
        event     		str
	datafile		str
	last_upd		str
	last_hjd		float
	last_mag		float
	tel			str
	ndata			int
	inst			str		
	filt			str
	baseline		float
	g			float
      """
    
    params = {'event': '985',\
              'datafile': '../../data/OOB170570I.dat',\
              'last_upd': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),\
	      'last_hjd':2457862.83112,\
	      'last_mag':round(16.923,2),\
	      'ndata':610,\
	      'tel':'OGLE 1.4m',\
	      'inst':'OGLE-IV camera',\
	      'filt':'I',\
	      'baseline':19.0,\
	      'g':0.0
             }
    config = {'db_user_id': 'rstreet', \
                'db_pswd': 'xxx'
                }
    response = api_tools.contact_db(config,params,'add_datafile',testing=True)
    
    assert bool(response.split(' ')[0]) == True
    
if __name__ == '__main__':
    test_api_datafile_record()
