# -*- coding: utf-8 -*-
"""
Created on Mon Apr 16 16:45:55 2018

@author: rstreet
"""

from astropy import units as u
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, get_sun, get_moon
from astropy.time import Time
import numpy as np
import observing_classes

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

def check_Moon_within_tolerance(pointing, site, obs_date,
                                separation_threshold=15.0,
                                phase_threshold=0.90):
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
    
    status = True
    
    if separation.value <= separation_threshold or phase >= phase_threshold:
        
        status = False
    
    return status
    
def get_skycoord(pointing):
    """Function to return a SkyCoord object for a given RA, Dec pointing"""
    
    if type(pointing[0]) == type(1.0):
        ra_deg = pointing[0]
        dec_deg = pointing[1]
    else:
        (ra_deg, dec_deg) = utilities.sex2decdeg(pointing[0], pointing[1])

    target = SkyCoord(ra=ra_deg*u.degree, dec=dec_deg*u.degree, frame='icrs')
    
    return target
    
def review_filters_for_observing_conditions(obs_sequence,field,
                                            ts_submit,ts_expire,
                                            log=None):
    """Function to review the default list of filters to be observed, 
    and ammend the list if the Moon is outside tolerances at any point
    during the lifetime of the observing request."""
    
    target = observing_tools.get_skycoord(field)
    
    sites = []
    site_filters = []
    
    for s,site_code in enumerate(obs_sequence['sites']):
    
        site = observing_tools.get_site_location(site_code)
    
        use_filters = []
        
        for f in obs_sequence['filters'][s]:

            sep_thresh = 15.0
            phase_thresh = 0.98
            
            if f == 'SDSS-g':
                
                sep_thresh = 40.0
                phase_thresh = 0.90
            
            moon_ok = True
            
            t = ts_submit
            while t <= ts_expire:
                            
                ts = Time(ts_submit.strftime("%Y-%m-%dT%H:%M:%S"),
                     format='isot', scale='utc')

                moon_chk = observing_tools.check_Moon_within_tolerance(target, site, ts,
                                                        separation_threshold=sep_thresh,
                                                        phase_threshold=phase_thresh)
                
                if not moon_chk:
                    
                    moon_ok = moon_chk
        
            if moon_ok:
                
                use_filters.append(f)
                
        if len(use_filters) > 0:
            
            site_filters.append( use_filters )
            sites.append(site_code)
        
    obs_sequence['sites'] = sites
    obs_sequence['filters'] = site_filters
    
    return obs_sequence
    