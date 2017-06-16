# -*- coding: utf-8 -*-
"""
Created on Mon Jun 12 14:44:30 2017

@author: rstreet
"""

import ephem
from sys import argv

def calc_lunar_separation():
    
    (date, target) = get_user_params()
    
    moon = ephem.Moon()
    
    target.compute(date)
    moon.compute(date)
    sep = ephem.separation(target, moon)
    print 'Separation between target and the Moon on '+\
        ephem.localtime(date).strftime("%Y-%m-%d")+': '+\
        str(ephem.degrees(sep))+' deg'

def get_user_params():
    """Function to harvest user-specific parameters by commandline prompt or
    commandline argument, if provided"""
    
    if len(argv) == 1:
        date = raw_input('Please enter the date required [YYYY/MM/DD]: ')
        ra = raw_input('Please enter the RA of the target [J2000.0]: ')
        dec = raw_input('Please enter the Dec of the target [J2000.0]: ')
    else:
        date = argv[1]
        ra = argv[2]
        dec = argv[3]
    
    date = ephem.Date(date+' 00:00:00')
    target = ephem.readdb('ENTRY,f|M|F7,' + str(ra) + ',' + str(dec) + \
                       ',0.0,2000')
    return date, target

if __name__ == '__main__':
    calc_lunar_separation()
    