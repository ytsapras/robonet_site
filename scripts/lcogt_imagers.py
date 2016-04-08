# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 16:57:47 2016

@author: rstreet
"""
import utilities
import numpy as np

class CameraFootprint:
    """Class describing the on-sky footprint of an imager"""
    
    def __init__( self, fov ):
        self.camera_class = None
        self.ra_fov = float( fov[0] )
        self.dec_fov = float( fov[1] )
        self.ra_dfov = self.ra_fov / 2.0
        self.dec_dfov = self.dec_fov / 2.0
    
    def calc_footprint( self, pointing ):
        """Method to calculate the corners of the footprint outline for a
        pointing given as a tuple of ( ra_centre, dec_centre )
        Coordinates can be given in sexigesimal or decimal degree format.
        """

        if ':' in str(pointing[0]):
            (ra_cen, dec_cen) = utilities.sex2decdeg( pointing )
        else:
            (ra_cen, dec_cen) = pointing
     
        corners = [
            [ (ra_cen + self.ra_dfov), (dec_cen + self.dec_dfov) ], 
            [ (ra_cen - self.ra_dfov), (dec_cen + self.dec_dfov) ],
            [ (ra_cen - self.ra_dfov), (dec_cen - self.dec_dfov) ],
            [ (ra_cen + self.ra_dfov), (dec_cen - self.dec_dfov) ],
            [ (ra_cen + self.ra_dfov), (dec_cen + self.dec_dfov) ]
            ]
        return np.array(corners)

def load_lcogt_footprints(camera=None, tel=None):
    """Function to provide the footprints of the different LCOGT camera classes
    Optional argument camera = {'spectral', 'sinistro', 'sbig' }
    Optional argument tel = { '2m', '1m', '0.4m' }
    If no argument is given, a dictionary is returned with all available
    camera footprints
    """
    
    def fov_degrees( fov ):
        dra = fov[0] / 60.0
        ddec = fov[1] / 60.0
        return (dra,ddec)
        
    specs = { '2m': { 'spectral': (10.0, 10.0) }, 
              '1m': { 'sinistro': (26.0, 26.0), 'sbig': (15.8, 15.8) }, 
              '0.4m': { 'sbig': (29.0,19.0) }
             }
    instruments = {}
    
    if camera == None or tel == None:
        for spec_tel, spec_cameras in specs.items():
            if tel not in instruments.keys():
                instruments[tel] = {}
            for cam, fov in spec_cameras.items():
                c = CameraFootprint( fov_degrees(fov) )
                instruments[spec_tel][cam] = c
    
        return instruments
        
    else:
        if tel in specs.keys():
            spec_cameras = specs[tel]
            if camera in spec_cameras.keys():
                fov = spec_cameras[camera]
                c = CameraFootprint( fov_degrees(fov) )
                return c
            else:
                print 'No specification for camera ' + camera + \
                    ' on ' + tel + '-class telescopes'
                return None
        else:
            print 'No telescope class ' + tel
            return None
        