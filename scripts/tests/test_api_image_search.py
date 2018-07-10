# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 21:30:44 2018

@author: rstreet
"""


from os import getcwd, path
from sys import path as systempath
from sys import argv
cwd = getcwd()
systempath.append(path.join(cwd,'../..'))
systempath.append(path.join(cwd,'..'))
import api_tools

def test_check_image_in_db():
    """Function to test the DB API to verify whether or not an image is 
    known to the DB based on its name"""
    
    
    config = {}
    
    if len(argv) == 1:
        config['db_token'] = raw_input('Please enter DB token: ')
    else:
        config['db_token'] = argv[1]
    
    params = {'image_name': 'cpt1m010-fl16-20170814-0065-e91.fits'}
    
    message = api_tools.check_image_in_db(config,params,
                                          testing=True,
                                          verbose=True)
        
    assert 'true' in str(message).lower()
    
    
    params['image_name'] = 'cpt1m010-fl16-20170814-9999-e91.fits'
    
    message = api_tools.check_image_in_db(config,params,
                                          testing=True,
                                          verbose=True)
        
    assert 'false' in str(message).lower()


if __name__ == '__main__':
    
    test_check_image_in_db()
    