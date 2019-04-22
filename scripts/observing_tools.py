# -*- coding: utf-8 -*-
"""
Created on Mon Apr 16 16:45:55 2018

@author: rstreet
"""

from astropy import units as u
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, get_sun, get_moon
from astropy.time import Time
import numpy as np
import observation_classes
from datetime import datetime, timedelta
import utilities

def get_site_location(site_code):
    """Function to return an LCO site location as an astropy EarthLocation.
    
    Returns None if given a non-existent site_code.
    
    Input:
        :param string site_code: 3-digit code for LCO site (lower case)
    
    Output:
        :param EarthLocation site_location: Location of the site
    """
    
    site_code = site_code.lower()
    
    # Locations of LCO telescope sites in (lat[deg],long[deg],altitude[m])
    # South and West are considered to be negative.
    lco_site_locations = { 'coj': (-31.2733, 149.071, 1116.0),
                           'cpt': (-32.38, 20.81, 1460.0),
                           'tfn': (28.3, -16.5097222222, 2330.0),
                            'lsc': (-30.1674, 70.8048, 2198.0),
                            'elp': (30.67, -104.02, 2070.0),
                            'ogg': (20.7075, -156.256, 3055.0),
                            'tlv': (30.5958333333, 34.7633333333, 875.0),
                            'ngq': (32.3166666667, 80.0166666667, 5100.0)
                          }

    if site_code in lco_site_locations.keys():
        
        (latitude,longitude,altitude) = lco_site_locations[site_code]
        
        earth_location = EarthLocation(lon=longitude * u.deg,
                                       lat=latitude * u.deg,
                                       height=altitude * u.m)
    else:
        
        earth_location = None
    
    return earth_location
    
def get_Moon_phase(target,earth_location,obs_date):
    """Function to compute the illumination phase of the Moon for a date
    given as an astropy.Time object.
    
    Code adapted from pyLIMA by E. Bachelet.

    Inputs:
        :param SkyCoord target: Target object location
        :param EarthLocation earth_location: Location of observer on Earth
        :param Time obs_date: Date to calculate separation
    
    Output:
        :param float phase: Illumination phase in percent.
    """

    altazframe = AltAz(obstime=Time(obs_date.jd, format='jd').isot, 
                       location=earth_location)
    
    sun = get_sun(Time(obs_date.jd, format='jd')).transform_to(altazframe)
    moon = get_moon(Time(obs_date.jd, format='jd')).transform_to(altazframe)

    geocentric_elongation = sun.separation(moon).rad
    selenocentric_elongation = np.arctan2(sun.distance * np.sin(geocentric_elongation),
                                          moon.distance - sun.distance * np.cos(geocentric_elongation))

    phase = (1 + np.cos(selenocentric_elongation)) / 2.0

    return phase
    
def get_Moon_separation(target,earth_location,obs_date):
    """Function to calculate the angular separation of a target from the Moon 
    for the given date.
    
    Code adapted from pyLIMA by E. Bachelet.
    
    Inputs:
        :param SkyCoord target: Target location
        :param EarthLocation earth_location: Location of observer on Earth
        :param Time obs_date: Date to calculate separation
    
    Output:
        :param float separation: Angular separation in decimal degrees
    """
    
    altazframe = AltAz(obstime=Time(obs_date.jd, format='jd').isot, 
                       location=earth_location)
    
    moon = get_moon(Time(obs_date.jd, format='jd')).transform_to(altazframe)
        
    separation = target.separation(moon)
    
    return separation

def check_Moon_within_tolerance(pointing, site, obs_date, obs_filter, 
                                tolerances, log=None):
    """Function to check whether the Moon is outside an acceptable threshold
    in angular separation and of illumination level less than the allowed
    limit.
    
    Inputs:
        :param SkyCoord target: Target location
        :param EarthLocation earth_location: Location of observer on Earth
        :param Time obs_date: Date to calculate separation
    
    Output:
        :param Bool status: Whether or not Moon is within tolerances.
    """

    target = SkyCoord(ra=17.256*15.0*u.degree, dec=-28.5*u.degree, frame='icrs')
    
    separation = get_Moon_separation(target,site,obs_date)
    phase = get_Moon_phase(target,site,obs_date)
    
    if obs_filter in tolerances.keys():
    
        criteria = tolerances[obs_filter]
        
        if log!=None:
            log.info('Selected observing conditions criteria for filter '+obs_filter)
            
    else:
        
        if log!=None:
            log.info('WARNING: No matching observing conditions criteria found for filter '+obs_filter)
            log.info('Using default criteria')
        
        criteria = {'phase_ranges': [ (0.0, 0.98), (0.98, 1.0) ],
                    'separation_minimums': [ 15.0, 30.0 ] }
    
    if log!=None:
        for p,prange in enumerate(criteria['phase_ranges']):
            log.info('-> phases '+str(prange[0])+' to '+str(prange[1])+\
                    ', require Moon separation > '+\
                    str(criteria['separation_minimums'][p]))
        log.info('Observations disallowed for other conditions')
        
    obs_ok = False
    moon_sep_min = 30.0
    
    for p,prange in enumerate(criteria['phase_ranges']):
        
        if phase.value >= prange[0] and phase.value <= prange[1] \
            and separation.value > criteria['separation_minimums'][p]:
                
                obs_ok = True
                moon_sep_min = criteria['separation_minimums'][p]
                
    if log!=None:
        log.info('Observation conditions:')
        log.info('-> '+obs_date.value+' Moon separation = '+str(separation))
        log.info('-> '+obs_date.value+' Moon illumination = '+str(phase))
        log.info('-> '+obs_date.value+' Moon separation minimum = '+str(moon_sep_min))
        log.info('-> OK to observe? '+repr(obs_ok))
        log.info('\n')

    return obs_ok, moon_sep_min
    
def get_skycoord(pointing):
    """Function to return a SkyCoord object for a given RA, Dec pointing"""
    
    if type(pointing[0]) == type(1.0):
        ra_deg = pointing[0]
        dec_deg = pointing[1]
    else:
        (ra_deg, dec_deg) = utilities.sex2decdeg(pointing[0], pointing[1])

    target = SkyCoord(ra=ra_deg*u.degree, dec=dec_deg*u.degree, frame='icrs')
    
    return target
    
def review_filters_for_observing_conditions(site_obs_sequence,field,
                                            ts_submit,ts_expire,tolerances,
                                            log=None):
    """Function to review the default list of filters to be observed, 
    and ammend the list if the Moon is outside tolerances at any point
    during the lifetime of the observing request."""
    
    if log!=None:
        log.info('Reviewing observing sequence in light of current Moon separation and illumination')
        
    target = get_skycoord(field)
            
    if log!=None:
        log.info('Reviewing observations for site '+site_obs_sequence['sites'][0])
        
    site = get_site_location(site_obs_sequence['sites'][0])
        
    site_filters = []
    site_nexp = []
    site_exptime = []
    site_defocus = []
    site_moon_sep = []
        
    for i,f in enumerate(site_obs_sequence['filters']):
        
        moon_ok = True
    
        t = ts_submit
        while t <= ts_expire:
                        
            ts = Time(t.strftime("%Y-%m-%dT%H:%M:%S"),
                 format='isot', scale='utc')

            (moon_chk,moon_sep_min) = check_Moon_within_tolerance(target, site, ts, f, 
                                                   tolerances, log=log)
            
            if not moon_chk:
                
                moon_ok = moon_chk
            
            t = t + timedelta(seconds=(1.0*24*60*60))
            
        if moon_ok:
            
            site_filters.append(f)
            site_moon_sep.append(moon_sep_min)
            if 'exp_times' in site_obs_sequence.keys():
                site_nexp.append(site_obs_sequence['exp_counts'][i])
                site_exptime.append(site_obs_sequence['exp_times'][i])
                site_defocus.append(site_obs_sequence['defocus'][i])
                
    site_obs_sequence['filters'] = site_filters
    try:
        site_obs_sequence['moon_sep_min'] = (np.array(site_moon_sep)).min()
    except ValueError:
        site_obs_sequence['moon_sep_min'] = 15.0
        
    if 'exp_times' in site_obs_sequence.keys() and len(site_exptime) > 0:
        site_obs_sequence['exp_counts'] = site_nexp
        site_obs_sequence['exp_times'] = site_exptime
        site_obs_sequence['defocus'] = site_defocus
    else:
        site_obs_sequence['exp_counts'] = []
        site_obs_sequence['exp_times'] = []
        site_obs_sequence['defocus'] = 0.0
        
    if log!=None:
        
        if len(site_obs_sequence['filters']) == 0:

            log.info('-> No observations possible due to lunar proximity')

        else:
            
            log.info('Revised observation sequence:')
            log.info(site_obs_sequence['sites'][0]+' '+repr(site_obs_sequence['filters']))
        
        log.info('\n')
        
    return site_obs_sequence

def calculate_exptime_romerea(magin, snrin=25):
    """
    This function calculates the required exposure time
    for a given iband magnitude (e.g. OGLE I which also
    roughly matches SDSS i) based on a fit to the empiric
    RMS diagram of DANDIA light curves from 2016. The
    output is in seconds.
    
    Ported in from code by Y. Tsapras
    
    R.Street: Added maximum exposure time
    """

    if magin < 14.7:
        mag = 14.7
    else:
        mag = magin
    lrms = 0.14075464 * mag * mag - 4.00137342 * mag + 24.17513298
    snr = 1.0 / np.exp(lrms)
    # target 4% -> snr 25
    expt = round((snrin / snr)**2 * 300., 1)
    expt = min(300.0, expt)
    
    return expt

def estimate_moon_separation_from_bulge():
    """Function to estimate the approximate angular separation of the Moon
    from the Bulge"""
    
    survey_centre = ['17:56:11.6396', '-28:38:38.643']
    
    target = get_skycoord(survey_centre)
    
    site = get_site_location('lsc')
    
    ts = Time(datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
                 format='isot', scale='utc')
    
    separation = get_Moon_separation(target, site, ts)
    
    return round(separation.value,1)
    