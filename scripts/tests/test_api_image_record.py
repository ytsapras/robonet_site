# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 10:51:37 2017

@author: ytsapras
"""

from os import getcwd, path, remove, environ
from sys import path as systempath
from sys import argv
cwd = getcwd()
systempath.append(path.join(cwd,'../..'))
systempath.append(path.join(cwd,'..'))
from local_conf import get_conf
robonet_site = get_conf('robonet_site')
systempath.append(robonet_site)
environ.setdefault('DJANGO_SETTINGS_MODULE', 'robonet_site.settings')
from django.core import management
from django.conf import settings
from django.utils import timezone
from django import setup
setup()
from events.models import Field, Event
from datetime import datetime, timedelta
import api_tools

def test_api_image_record():
    """Function to test the recording of a new image 
    request (submitted to the LCO network) by submitting it to the ROME/REA
    database via API. """

    config = {}
    if len(argv) == 1:
        config['db_token'] = raw_input('Please enter DB token: ')
    else:
        config['db_token'] = argv[1]

    params = {'field_name': 'ROME-FIELD-01',
              'image_name': 'cpt1m005-fl03-20180701-9999_e91.fits',
              'date_obs': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
	      'timestamp':datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
	      'tel':'LCOGT SAAO A 1m',
	      'inst':'fl16',
	      'filt':'SDSS-i',
	      'grp_id':'ROME20170813T4.1535179',
	      'track_id':'0000471120',
	      'req_id':'0001253913',
	      'airmass':1.2,
	      'avg_fwhm': 3.4,
	      'avg_sky': 2300.0,
	      'avg_sigsky': 340.0,
	      'moon_sep': 22.0,
	      'moon_phase': 10,
	      'moon_up': False,
	      'elongation': 0.6,
	      'nstars': 1043,
	      'ztemp': 15.0,
	      'shift_x': 32,
	      'shift_y': 24,
	      'quality': 'No sky level variations measured! ; No maximum sky level measured! ; Bad seeing'
             }
    
    response = api_tools.submit_image_record(config,params,
                                             testing=True,
                                             verbose=True)
    
    assert 'Successfully added image' in response
    
    
    response = api_tools.submit_image_record(config,params,
                                             testing=True,
                                             verbose=True)
    
    assert 'Successfully updated image' in response
    
if __name__ == '__main__':
    test_api_image_record()
