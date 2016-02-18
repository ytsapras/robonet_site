# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 13:49:18 2016

@author: rstreet
"""

from astropy.time import Time

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
        else: 
            if par_value == None or str(par_value).lower() == 'none':
                setattr(self,par,par_value)
            else:
                setattr(self,par,float(par_value))

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


class K2C9Event():
    """Class describing the parameters to be output for a microlensing event 
    within the K2/Campaign 9 field
    """
    def __init__( self ):
        self.identifier = None
        self.master_index = None
        self.status = 'NEW'
        self.recommended_status = 'NEW'
        self.ogle_name = None
        self.ogle_ra = None 
        self.ogle_dec = None
        self.ogle_t0 = None
        self.ogle_sig_t0 = None
        self.ogle_a0 = None
        self.ogle_sig_a0 = None
        self.ogle_te = None
        self.ogle_sig_te = None
        self.ogle_u0 = None
        self.ogle_sig_u0 = None
        self.ogle_i0 = None
        self.ogle_sig_i0 = None
        self.ogle_ndata = None
        self.ogle_url = None
        self.moa_name = None
        self.moa_ra = None
        self.moa_dec = None
        self.moa_t0= None
        self.moa_sig_t0= None
        self.moa_a0 = None
        self.moa_sig_a0 = None
        self.moa_te = None
        self.moa_sig_te = None
        self.moa_u0 = None
        self.sig_u0 = None
        self.i0 = None
        self.sig_i0 = None
        self.ndata = None
        self.moa_url = None
        self.kmt_name = None
        self.kmt_ra = None
        self.kmt_dec = None
        self.kmt_t0 = None
        self.kmt_sig_t0 = None
        self.kmt_a0 = None
        self.kmt_sig_a0 = None
        self.kmt_te = None
        self.kmt_sig_te = None
        self.kmt_u0 = None
        self.kmt_sig_u0 = None
        self.kmt_i0 = None
        self.kmt_sig_i0 = None
        self.kmt_ndata = None
        self.kmt_url = None
        self.signalmen_a0 = None
        self.signalmen_t0 = None
        self.signalmen_sig_t0 = None
        self.signalmen_te = None
        self.signalmen_sig_te = None
        self.signalmen_u0 = None
        self.signalmen_sig_u0 = None
        self.signalmen_anomaly = None
        self.pylima_a0 = None
        self.pylima_sig_a0 = None
        self.pylima_te = None
        self.pylima_sig_te = None
        self.pylima_t0 = None
        self.pylima_sig_t0 = None
        self.pylima_u0 = None
        self.pylima_sig_u0 = None
        self.pylima_rho = None
        self.pylima_sig_rho = None
        self.bozza_a0 = None
        self.bozza_sig_a0 = None
        self.bozza_te = None
        self.bozza_sig_te = None
        self.bozza_t0 = None
        self.bozza_sig_t0 = None
        self.bozza_u0 = None
        self.bozza_sig_u0 = None
        self.bozza_rho = None
        self.bozza_sig_rho = None
        self.bozza_s = None
        self.bozza_sig_s = None
        self.bozza_q = None
        self.bozza_sig_q = None
        self.bozza_theta = None
        self.bozza_sig_theta = None
        self.bozza_pi_perp = None
        self.bozza_sig_pi_perp = None
        self.bozza_pi_para = None
        self.bozza_sig_pi_para = None
        self.bozza_url = None
        self.nnewdata = 0
        self.time_last_updated = None
        self.in_footprint = 'Unknown'
        self.in_superstamp = 'Unknown'
        self.during_campaign = 'Unknown'
        self.alertable = None

    def set_params( self, params ):
        """Method to set the parameters of the current instance from a 
        a dictionary containing some or all of the parameters of the class.
        Key names in the input dictionary must match those used in the class.
        """

        for key, value in params.items():
            if key in dir( self ):
                setattr( self, key, value )
    
    def get_params( self ):
        """Method to return a dictionary of all parameters"""
        
        params = {}
        for key in dir( self ):
            params[key] = getattr(self,key)
        return params
        
    def set_event_name( self, params ):
        """Method to set the name of an event based on the given names
        allocated by survey.
        """
        
        # Identify the originating survey:
        if 'name' in params.keys(): name_key = 'name'
        else: name_key = 'long_name'
            
        prefix = (str( params[name_key] ).split('-')[0]).lower()
        
        key = prefix + '_name'
        if key in dir( self ):
            setattr(self, key, params[ name_key ] )
    
    def get_event_name( self ):
        """Return the survey-allocated name of an event"""
        
        if self.ogle_name != None:
            return self.ogle_name
        elif self.moa_name != None:
            return self.moa_name
        elif self.kmt_name != None:
            return self.kmt_name
        else:
            return None
    
    def get_event_origin( self ):
        """Return the originating survey name in lower case"""
        
        if self.ogle_name != None:
            return 'ogle'
        elif self.moa_name != None:
            return 'moa'
        elif self.kmt_name != None:
            return 'kmt'
        else:
            return None
    
    def summary( self, key_list ):
        """Method to print a customizible summary of the information on
        a given K2C9Event instance, given a list of keys to output.
        """

        # An event may be discovered by multiple surveys and hence
        # have multiple event names:
        name = ''
        for key in [ 'ogle_name', 'moa_name', 'kmt_name' ]:
            if getattr(self, key) != None: 
                name = name + str( getattr( self, key ) )
        
        output = str( self.identifier ) + ' ' + name + ' '
        for key in key_list:
            if key in dir( self ):
                output = output + str( getattr(self,key) ) + ' '
        return output

    def generate_exofop_data_file( self, output_path ):
        """Method to output a summary file of all parameters of an 
        instance of this class
        """
        
        # First set timestamp of output:
        nt = Time.now()
        self.time_last_updated = nt.utc.value.strftime("%Y-%m-%dT%H:%M:%S")
        
        key_list = dir( self )
        exclude_keys = [ 'generate_exofop_data_file', \
                         'get_valid_params', \
                         'set_event_name', \
                         'set_params',\
                         'get_par',\
                         'get_params',\
                         'summary',\
                         'in_superstamp',\
                         'in_footprint',\
                         'during_campaign',\
                         'get_location',\
                         'master_index',
                         ]
        for key in exclude_keys:
            if key in key_list or '__' in key:
                key_list.remove( key )
        key_list.sort()
        
        f = open( output_path, 'w' )
        
        for attr in key_list:
            key = str(attr).lower()
            if '__' not in key[0:2]: 
                value = str( getattr(self,key) )
                f.write( key.upper() + '    ' + value + '\n' )
        
        f.close()
    
    def get_location( self ):
        """Return coordinates of event"""
        
        ra = None
        dec = None
        if self.ogle_ra != None and self.ogle_dec != None:
            ra = self.ogle_ra
            dec = self.ogle_dec
        elif self.moa_ra != None and self.moa_dec != None:
            ra = self.moa_ra
            dec= self.moa_dec
        return (ra, dec)

    def get_par( self, param_name ):
        """Return indicated parameter value for an event"""
        
        value = None
        if getattr( self, 'ogle_' + param_name ) != None:
            value = getattr( self, 'ogle_' + param_name )
        elif getattr( self, 'moa_' + param_name ) != None:
            value = getattr( self, 'moa_' + param_name )
        return value

    def check_in_k2( self, k2_campaign ):
        """Method to check whether an event is in a K2 campaign"""
    
        events = {}
        events[ self.identifier ] = self    
        events = k2_campaign.targets_in_footprint( events )
        events = k2_campaign.targets_in_superstamp( events )
        events = k2_campaign.targets_in_campaign( events )