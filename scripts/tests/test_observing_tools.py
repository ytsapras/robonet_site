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
from rome_fields_dict import field_dict
from datetime import datetime, timedelta
import log_utilities

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

def test_get_Moon_separation():

    test_sep = 168.64
    
    t = Time('2018-04-20T12:00:00', format='isot', scale='utc')
        
    target = SkyCoord(ra=17.256*15.0*u.degree, dec=-28.5*u.degree, frame='icrs')
    
    site = observing_tools.get_site_location('lsc')
    
    separation = observing_tools.get_Moon_separation(target,site,t)
    
    assert round(separation.value,2) == test_sep

def test_check_Moon_within_tolerance():
    
    t = Time('2018-04-20T12:00:00', format='isot', scale='utc')
        
    target = SkyCoord(ra=17.256*15.0*u.degree, dec=-28.5*u.degree, frame='icrs')
    
    site = observing_tools.get_site_location('lsc')
    
    status = observing_tools.check_Moon_within_tolerance(target, site, t,
                                                        separation_threshold=15.0,
                                                        phase_threshold=0.90)
    
    assert status == True
    
    t = Time('2018-05-02T12:00:00', format='isot', scale='utc')
     
    status = observing_tools.check_Moon_within_tolerance(target, site, t,
                                                        separation_threshold=15.0,
                                                        phase_threshold=0.90)
    assert status == False

def test_review_filters_for_observing_conditions():
    
    config = { 'log_directory': '.',
              'log_root_name': 'test_observing_tools'
             }
    log = log_utilities.start_day_log( config, 'test_observing_tools' )
    
    def get_default_site_obs_sequence(site_code):
        
        site_obs_sequence = {
                'exp_times': [300.0, 300.0, 300.0],
                'exp_counts': [ 1, 1, 1 ],
                'filters':   [ 'SDSS-g', 'SDSS-r', 'SDSS-i'],
                'defocus':  [ 0.0, 0.0, 0.0 ],
                'sites':        ['lsc'],
                'domes':        ['doma'],
                'tels':         [ '1m0' ],
                'instruments':  ['fl15'],
                'cadence_hrs': 7.0,
                'jitter_hrs': 7.0,
                'TTL_days': 6.98,
                'priority': 1.05
                }
                
        return site_obs_sequence
        
    field = field_dict['ROME-FIELD-01']
    
    site_code = 'lsc'

    site_obs_sequence = get_default_site_obs_sequence(site_code)
    
    ts_submit = datetime.strptime('2018-05-02T12:00:00',"%Y-%m-%dT%H:%M:%S")
    ts_expire = ts_submit + timedelta(seconds=(6.8*24*60*60))
    
    log.info('Testing observation sequence review between dates:')
    log.info(ts_submit.strftime("%Y-%m-%dT%H:%M:%S")+' to '+\
            ts_expire.strftime("%Y-%m-%dT%H:%M:%S"))
    
    site_obs_sequence = observing_tools.review_filters_for_observing_conditions(site_obs_sequence,field,
                                                                           ts_submit,ts_expire,
                                                                           log=log)

    assert len(site_obs_sequence['filters']) == 0
    
    log.info('\n')
    log.info('Testing observation sequence review between dates:')
    log.info(ts_submit.strftime("%Y-%m-%dT%H:%M:%S")+' to '+\
            ts_expire.strftime("%Y-%m-%dT%H:%M:%S"))
    
    site_obs_sequence = get_default_site_obs_sequence(site_code)
    
    ts_submit = datetime.strptime('2018-04-20T12:00:00',"%Y-%m-%dT%H:%M:%S")
    ts_expire = ts_submit + timedelta(seconds=(6.8*24*60*60))
    
    site_obs_sequence = observing_tools.review_filters_for_observing_conditions(site_obs_sequence,field,
                                                                           ts_submit,ts_expire,
                                                                           log=log)
                                                        
    assert len(site_obs_sequence['sites']) == 1
    assert len(site_obs_sequence['filters']) == 3
    
    log_utilities.end_day_log(log)
    
def test_get_skycoord():
    
    ra_hrs = 17.256
    dec_deg = -28.5
    
    pointing = [ra_hrs*15.0, dec_deg]
    
    test_target = SkyCoord(ra=ra_hrs*15.0*u.degree, dec=dec_deg*u.degree, frame='icrs')
    
    target = observing_tools.get_skycoord(pointing)
    
    assert type(target) == type(test_target)
    assert target.ra == test_target.ra
    assert target.dec == test_target.dec
    
if __name__ == '__main__':
    
    test_get_site_location()
    test_get_Moon_phase()
    test_get_Moon_separation()
    test_check_Moon_within_tolerance()
    test_review_filters_for_observing_conditions()
    test_get_skycoord()
    