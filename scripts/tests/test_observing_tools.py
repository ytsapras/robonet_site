# -*- coding: utf-8 -*-
"""
Created on Mon Apr 16 16:52:24 2018

@author: rstreet
"""

from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
from sys import path as systempath
from os import getcwd, path
cwd = getcwd()
systempath.append(path.join(cwd,'..'))
import observing_tools

def test_get_site_location():
    
    site_code = 'lsc'

    lsc = EarthLocation(lon=70.8048 * u.deg,
                       lat=-30.1674 * u.deg,
                       height=2198.0 * u.m)

    site_location = observing_tools.get_site_location(site_code)
    
    assert site_location == lsc
    
    site_code = 'foo'
    
    site_location = observing_tools.get_site_location(site_code)
    
    assert site_location == None
    

def test_get_Moon_phase():
    
    test_phase = 0.24
    
    t = Time('2018-04-20T12:00:00', format='isot', scale='utc')
        
    target = SkyCoord(ra=17.256*15.0*u.degree, dec=-28.5*u.degree, frame='icrs')
    
    site = observing_tools.get_site_location('lsc')
    
    phase = observing_tools.get_Moon_phase(target,site,t)

    assert round(phase,2) == test_phase
    
if __name__ == '__main__':
    
    test_get_site_location()
    test_get_Moon_phase()