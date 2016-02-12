# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 13:49:18 2016

@author: rstreet
"""

##################################################
# LENS CLASS DESCRIPTION
class Lens():
    """Class describing the basic parameters of a microlensing event 
    (point source point lens) as required for most purposes for the
    database"""

    def __init__(self):
        self.name = None
        self.ra = None
        self.dec = None
        self.t0 = None
        self.te = None
        self.u0 = None
        self.a0 = None
        self.i0 = None
        self.origin = None

    def set_par(self,par,par_value):

        if par in [ 'name' ]: setattr(self,par,par_value)
        else: setattr(self,par,float(par_value))

    def summary(self):
        return self.name + ' ' + str(self.ra) + '  ' + str(self.dec) + '  ' + \
                str(self.t0) + ' ' + str(self.te) + ' ' + str(self.u0) + '  ' +\
                str(self.a0) + ' ' + str(self.i0)

    def sync_event_with_DB(self):
        '''Method to sync the latest survey parameters with the database.'''

    def get_params(self):
        """Method to return the parameters of the current event in a 
        dictionary format
        """
        
        params = {}
        for key in dir( self ):
            params[ key ] = getattr( self, key )
        return params
        
# Check event is known by name to the DB
# (possible outcomes: True or False)

# Check event is known by coordinates to the DB
# (possible outcomes: - event is known and has this survey's ID
#                     - event is known at these coordinates with ID from other survey(s)
#                     - event is unknown

# If event is unknown:
# - create a new entry in Event table
# - create a new entry in the Single_Model table for this model provider

# If event is known by this survey's ID:
# - fetch the Event PK index
# - fetch the Modeler PK for this survey
# - fetch the most recent Single_Model for this Event from this Modeler and return its timestamp and parameters
# - check whether the self.last_updated timestamp is more recent than the DB'd latest model
# - check whether the parameter values have changed
# - if self.last_updated > model_timestamp and parameter values != model_parameters then
#   create a new Single_Model entry

# If event is know but by another survey(s) ID:
# - fetch the Event PK index by coordinate search
# - fetch the Survey PK index
# - fetch the Modeler PK index
# - create a new entry in Event_Names table for this Event and Survey
# - create a new Single_Model entry for this Event and Modeler with the parameters given


