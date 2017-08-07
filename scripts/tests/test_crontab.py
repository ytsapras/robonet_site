# -*- coding: utf-8 -*-
"""
Created on Mon Aug  7 11:51:03 2017

@author: rstreet
"""

from astropy import constants, time
from os import path

def test_crontab():
    """Function to test running software under the cron"""
    
    homedir = path.expanduser('~')
    file_path = path.join(homedir,'crontest.dat')
    ts = time.Time.now()
    f = open(file_path,'w')
    f.write(repr(ts)+'\n')
    f.write(str(constants.G)+'\n\n')
    f.write(str(constants.c)+'\n')
    f.close()

if __name__ == '__main__':
    test_crontab()