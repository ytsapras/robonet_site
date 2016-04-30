# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 17:42:22 2016

@author: rstreet
"""
import k2_footprint_class
import lcogt_imagers
from sys import argv, exit
from os import path
import utilities

def lcogt_pointings(tel, camera, pointings_file):
    """Function to over plot the LCOGT camera footprints on the K2 footprint"""
    
    # Config:
    config =     {'k2_campaign': 9, 'k2_year': 2016, \
                    'k2_footprint_data': '../data/k2-footprint.json',\
                    'xsuperstamp_target_data': '../data/xsuperstamp_targets_C9b.json'
                }
    
    # Load the K2C9 footprint
    k2_campaign = k2_footprint_class.K2Footprint( config )
    k2_campaign.load_xsuperstamp_targets( config )
    
    # Load the requested camera footprint:
    sinistro = lcogt_imagers.load_lcogt_footprints(tel='1m',camera='sinistro')
    
    # Load the list of pointings and convert into camera overlays:
    pointings = read_pointings(pointings_file)
    overlays = {}
    for name,coords in pointings.items():
        corners = sinistro.calc_footprint( coords )
        overlays[name] = corners
    
    # Plot the K2 footprint with overlays:
    k2_campaign.plot_footprint(plot_file='test_k2_footprint.png', targets= \
                k2_campaign.xsuperstamp_targets, overlays=overlays)
    
    
def read_pointings(pointings_file):
    """Function to read a file of pointings, which may be in sexigesimal or
    decimal degrees"""
    
    if path.isfile(pointings_file) == False:
        print 'ERROR: Cannot find file ' + pointings_file
        exit()
        
    file_lines = open(pointings_file,'r').readlines()
    pointings = {}
    for line in file_lines:
        (ra, dec, name) = line.replace('\n','').split()
        if ':' in str(ra):
            (ra, dec) = utilities.sex2decdeg(ra, dec)
        pointings[name] = (ra, dec)
    return pointings
    
if __name__ == '__main__':
    if len(argv) == 1:
        tel = raw_input('Please enter an LCOGT telescope class: ')
        camera = raw_input('Please enter an imager class on that telescope: ')
        pointings_file = raw_input('Please enter the path to a pointings file: ')
    else:
        tel = argv[1]
        camera = argv[2]
        pointings_file = argv[3]
    
    lcogt_pointings(tel, camera, pointings_file)
    