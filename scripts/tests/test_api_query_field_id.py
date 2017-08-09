# -*- coding: utf-8 -*-
"""
Created on Tue Aug  8 10:22:02 2017

@author: rstreet
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
from events.models import Field
import api_tools

def test_query_field_id():
    """Function to test the API query for Field ID
    Response is a single string containing the name of the field and the
    field DB primary key.  If the field is outside the ROME footprint, -1 
    key is returned.     
    """
    
    params = {'field_ra': '17:54:50.3369',\
              'field_dec': '-29:11:12.2107'}
              
    config = {'db_user_id': 'rstreet', \
                'db_pswd': 'xxxx'}
    response = api_tools.query_field_id(config,params,testing=True)
    print(response)
    
if __name__ == '__main__':
    test_query_field_id()