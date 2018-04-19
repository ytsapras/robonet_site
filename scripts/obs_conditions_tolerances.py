# -*- coding: utf-8 -*-
"""
Created on Thu Apr 19 14:13:32 2018

@author: rstreet
"""

def get_obs_tolerances():
    """Function to return the criteria used to determine acceptable observing
    conditions"""
    
    tolerances = { 'SDSS-g': {'phase_ranges': [ (0.0, 0.98) ],
                  'separation_minimums': [ 40.0 ]},
           'SDSS-r': {'phase_ranges': [ (0.0, 0.98), (0.98, 1.0) ],
                  'separation_minimums': [ 15.0, 30.0 ]},
           'SDSS-i': {'phase_ranges': [ (0.0, 0.98), (0.98, 1.0) ],
                  'separation_minimums': [ 15.0, 30.0 ]},
          }

    return tolerances