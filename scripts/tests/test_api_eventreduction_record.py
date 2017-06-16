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
from local_conf import get_conf
robonet_site = get_conf('robonet_site')
systempath.append(robonet_site)
environ.setdefault('DJANGO_SETTINGS_MODULE', 'robonet_site.settings')
from django.core import management
from django.conf import settings
from django.utils import timezone
from django import setup
setup()
from events.models import Operator, Event
from datetime import datetime, timedelta
import api_tools

def test_api_eventreduction_record():
    """Function to test the recording of a new Event Reduction 
    by submitting it to the ROME/REA
    database via API. """
    
    params = {'event':'1',\
             'lc_file':'/test/lc/filepath/lc.t',\
             'ref_image':'name_of_refimage.fits',\
             'timestamp':datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),\
             'ron':0.0,\
             'gain':1.0,\
             'oscanx1':1,\
             'oscanx2':50,\
             'oscany1':1,\
             'oscany2':500,\
             'imagex1':51,\
             'imagex2':1000,\
             'imagey1':1,\
             'imagey2':1000,\
             'minval':1.0,\
             'maxval':55000.0,\
             'growsatx':0,\
             'growsaty':0,\
             'coeff2':0.0,\
             'coeff3':0.0,\
             'sigclip':4.5,\
             'sigfrac':0.5,\
             'flim':2.0,\
             'niter':4,\
             'use_reflist':0,\
             'max_nimages':1,\
             'max_sky':5000.0,\
             'min_ell':0.8,\
             'trans_type':'P',\
             'trans_auto':0,\
             'replace_cr':0,\
             'min_scale':0.99,\
             'max_scale':1.01,\
             'fov':0.1,\
             'star_space':30,\
             'init_mthresh':1.0,\
             'smooth_pro':2,\
             'smooth_fwhm':3.0,\
             'var_deg':1,\
             'det_thresh':2.0,\
             'psf_thresh':8.0,\
             'psf_size':8.0,\
             'psf_comp_dist':0.7,\
             'psf_comp_flux':0.1,\
             'psf_corr_thresh':0.9,\
             'ker_rad':2.0,\
             'lres_ker_rad':2.0,\
             'subframes_x':1,\
             'subframes_y':1,\
             'grow':0.0,\
             'ps_var':0,\
             'back_var':1,\
             'diffpro':0}
    config = {'db_user_id': 'ytsapras', \
                'db_pswd': 'xxxx'
                }
    response = api_tools.submit_eventreduction_record(config,params)
    
if __name__ == '__main__':
    test_api_eventreduction_record()
