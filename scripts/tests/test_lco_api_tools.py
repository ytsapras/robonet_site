# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 16:23:33 2018

@author: rstreet
"""

import sys
import os
cwd = os.getcwd()
sys.path.append(os.path.join(cwd,'..'))
import lco_api_tools

def run_tests():
    """Function to run the suite of tests.  Since access to LCO's API 
    requires a user token, these tests require this token as input and so
    don't conform to the usual pytest format.
    """
    
    if len(sys.argv) > 1:
        
        token = sys.argv[1]
        
    else:
        
        token = raw_input('Please enter your LCO API token: ')
   
    test_get_subrequests_status(token)
 
 
def test_get_subrequests_status(token):
    
    track_id = 624354
    
    (states, completed_ts, windows) = lco_api_tools.get_subrequests_status(token,track_id)

    for i in range(0,len(states),1):
        print states[i], completed_ts[i], windows[i]

    assert type(states) == type([])
    assert type(completed_ts) == type([])
    assert len(states) > 0
    
if __name__ == '__main__':
    
    run_tests()
    