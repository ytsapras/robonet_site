# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 10:51:37 2017

@author: ytsapras
"""

from os import getcwd, path, remove, environ
from sys import path as systempath
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
    
    params = {'field': '1',\
              'image_name': 'test_image.fits',\
              'date_obs': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),\
	      'timestamp':datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),\
	      'tel':'LCOGT SAAO A 1m',\
	      'inst':'SAAO 1.0m CCD camera',\
	      'filt':'SDSS-i',\
	      'grp_id':'SOMEGRPID',\
	      'track_id':'SOMETRACKID',\
	      'req_id':'SOMEREQID',\
	      'airmass':1.2,\
	      'avg_fwhm': 3.4,\
	      'avg_sky': 2300.0,\
	      'avg_sigsky': 340.0,\
	      'moon_sep': 22.0,\
	      'moon_phase': 10,\
	      'moon_up': False,\
	      'elongation': 0.6,\
	      'nstars': 1043,\
	      'ztemp': 15.0,\
	      'shift_x': 32,\
	      'shift_y': 24,\
	      'quality': 'Image OK'
             }
    config = {'db_user_id': 'ytsapras', \
                'db_pswd': 'xxxx'
                }
    response = api_tools.submit_image_record(config,params)
    
if __name__ == '__main__':
    test_api_image_record()
