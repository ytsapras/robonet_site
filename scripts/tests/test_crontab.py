# -*- coding: utf-8 -*-
"""
Created on Mon Aug  7 11:51:03 2017

@author: rstreet
"""

from astropy import constants, time
from os import path, getcwd
import socket
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'../'))
from local_conf import get_conf

def test_crontab():
    """Function to test running software under the cron"""
    
    homedir = path.expanduser('~')
    host_name = socket.gethostname()
    file_path = path.join(homedir,'crontest.dat')
    ts = time.Time.now()
    f = open(file_path,'w')
    f.write('HOSTNAME: '+str(host_name)+'\n')
    config = get_conf('robonet_site')
    f.write(repr(config)+'\n')
    f.write(repr(ts)+'\n')
    f.write(str(constants.G)+'\n\n')
    f.write(str(constants.c)+'\n')
    f.close()

if __name__ == '__main__':
    test_crontab()