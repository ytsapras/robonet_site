# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 13:49:18 2016

@author: rstreet
"""

from astropy.time import Time
from os import path
import numpy as np

##################################################
# LENS CLASS DESCRIPTION
class Lens():
    """Class describing the basic parameters of a microlensing event 
    (point source point lens) as required for most purposes for the
    database"""

    def __init__(self):
        self.name = None
        self.survey_id = None
        self.ra = None
        self.dec = None
        self.t0 = None
        self.te = None
        self.u0 = None
        self.a0 = None
        self.i0 = None
        self.origin = None
        self.classification = 'microlensing'
        
    def set_par(self,par,par_value):

        if par in [ 'name', 'survey_id', 'classification' ]: 
            setattr(self,par,par_value)
        else: 
            if par_value == None or str(par_value).lower() == 'none':
                setattr(self,par,par_value)
            else:
                try:
                    setattr(self,par,float(par_value))
                except ValueError:
                    setattr(self,par,par_value)

    def summary(self):
        return self.name + ' ' + str(self.survey_id) + ' ' + \
                str(self.ra) + '  ' + str(self.dec) + '  ' + \
                str(self.t0) + ' ' + str(self.te) + ' ' + str(self.u0) + '  ' +\
                str(self.a0) + ' ' + str(self.i0) + ' ' + self.classification

    def sync_event_with_DB(self):
        '''Method to sync the latest survey parameters with the database.'''

    def get_params(self):
        """Method to return the parameters of the current event in a 
        dictionary format
        """
        key_list = [ 'name', 'survey_id', 'ra', 'dec', 't0', 'te', 'u0', \
                        'a0', 'i0', 'origin']
        params = {}
        for key in key_list:
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
        self.recommended_status = None
        self.ogle_name = None
        self.ogle_survey_id = None
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
        self.ogle_alert = None
        self.moa_name = None
        self.moa_survey_id = None
        self.moa_ra = None
        self.moa_dec = None
        self.moa_t0= None
        self.moa_sig_t0= None
        self.moa_a0 = None
        self.moa_sig_a0 = None
        self.moa_te = None
        self.moa_sig_te = None
        self.moa_u0 = None
        self.moa_sig_u0 = None
        self.moa_i0 = None
        self.moa_sig_i0 = None
        self.moa_ndata = None
        self.moa_alert = None
        self.ndata = None
        self.moa_url = None
        self.kmt_name = None
        self.kmt_survey_id = None
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
        self.kmt_alert = None
        self.classification = 'microlensing'
        self.signalmen_a0 = None
        self.signalmen_t0 = None
        self.signalmen_sig_t0 = None
        self.signalmen_te = None
        self.signalmen_sig_te = None
        self.signalmen_u0 = None
        self.signalmen_sig_u0 = None
        self.signalmen_anomaly = None
        self.tap_priority = None
        self.omega_s_now = None
        self.sig_omega_s_now = None
        self.omega_s_peak = None
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
    
    def get_params( self, key_list=None ):
        """Method to return a dictionary of all parameters"""
        
        if key_list == None:
            key_list = dir( self )
            
        params = {}
        for key in key_list:
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
    
    def set_moa_url( self, params ):
        """Method to set the MOA URL to a specific event, from its parameters"""
        
        year = str(self.moa_name).split('-')[1]
        
        self.moa_url = path.join( params['moa_root_url']+year, \
                                    'display.php?id=' + self.moa_survey_id )
    
    def set_ogle_url( self, params ):
        """Method to set the OGLE URL to a specific event page"""
        
        year = str(self.ogle_name).split('-')[1]
        number = str(self.ogle_name).split('-')[-1]
        
        self.ogle_url = path.join( params['ogle_root_url'], year, \
                            'blg-'+number+'.html')
    
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

    def generate_exofop_param_file( self, output_path ):
        """Method to output a summary file of all parameters of an 
        instance of this class
        """
                
        
        # First set timestamp of output:
        nt = Time.now()
        self.time_last_updated = nt.utc.value.strftime("%Y-%m-%dT%H:%M:%S")
        
        key_list = dir( self )
        exclude_keys = [ 'generate_exofop_data_file', \
                         'generate_exofop_param_file',\
                         'get_valid_params', \
                         'set_event_name', \
                         'set_params',\
                         'get_par',\
                         'get_params',\
                         'summary',
                         'get_location',\
                         'master_index',\
                         'check_in_k2', 'get_event_name', 'get_event_origin',\
                         'alertable', \
                         'classification', \
                         'tap_priority', 'omega_s_now', 'sig_omega_s_now', \
                         'omega_s_peak', 'set_moa_url', 'set_ogle_url'
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

    def generate_exofop_data_file( self, phot_data, output_path, log ):
        """Method to produce a data file of the public-access data to be 
        sent to ExoFOP"""
        
        providers = {   'O': 'OGLE', 'K': 'MOA', \
                        'L': 'Danish-1.54m', 'Z': 'Danish-1.54m', \
                        'P': 'MONET-North', 'Q': 'MONET-South', \
                        'H': 'LCOGT-Hawaii-2.0m', 'I': 'LCOGT-Australia-2.0m', \
                        'J': 'Liverpool-2.0m', \
                        'D': 'LCOGT-Chile-1.0m', 'E': 'LCOGT-Chile-1.0m', \
                        'F': 'LCOGT-Chile-1.0m', \
                        'R': 'LCOGT-SAfrica-1.0m', 'S': 'LCOGT-SAfrica-1.0m', \
                        'T': 'LCOGT-SAfrica-1.0m', \
                        'X': 'LCOGT-Australia-1.0m', 'Y': 'LCOGT-Australia-1.0m', \
                        'U': 'UTas-1.0m', 'W': 'Perth-0.6m', 'A': 'SAAO-1.0m', \
                        'C': 'CTIO-1.3m', 's': 'Salerno-0.35m', \
                        'y': 'CTIO-1.0m', 'z': 'Hereford-Arizona-0.35m', \
                        'l': 'Mt-Lemmon-1.0m', 'm': 'MDM-2.4m', 'o': 'Palomar-60inch', \
                        'r': 'Regent-Lane', 'd': 'Possum-11inch', 'a': 'Auckland-0.4m', \
                        'h': 'Hunters-Hill-0.35m', 't': 'Southern-Stars-11inch', \
                        'f': 'Farm-Cove-0.35m', 'k': 'Kumeu-Obs-0.35m', \
                        'v': 'Vintage-Lane-0.4m', 'p': 'CBA-Perth-0.25m', \
                        'w': 'Wise-1.0m-E2V', 'i': 'Wise-1.0m-SITe', \
                        'b': 'Bronberg-0.35m' }
        
        event_name = self.get_event_name()
        ndata = len(phot_data)
        if ndata > 0:
            fileobj = open( output_path, 'w' )
            fileobj.write('# Lightcurve data for ' + self.identifier + \
                                ' = ' + event_name + '\n')
            fileobj.write('#\n')
            fileobj.write('# Column 1: Timestamps in HJD\n')
            fileobj.write('# Column 2: Magnitudes\n')
            fileobj.write('# Column 3: Magnitude error\n')
            fileobj.write('# Column 4: Data provider\n')
            for i in range(0,ndata,1):
                entry = ' '.join( phot_data[i,0:3].tolist() )
                p = providers[ phot_data[i,3] ]
                entry = entry + ' ' + p + '\n'
                fileobj.write(entry)
            fileobj.close()
            log.info(' -> Wrote data file of available public data')
            
        else:
            log.info(' -> No available public data.  No data file produced')

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

class RTModel():
    """Class describing the parameters of a model from RTModel"""
    
    def __init__(self):
        self.event_name = None
        self.s = None
        self.sig_s = None
        self.q = None
        self.sig_q = None
        self.u0 = None
        self.sig_u0 = None
        self.t0 = None
        self.sig_t0 = None
        self.tE = None
        self.sig_tE = None
        self.theta = None
        self.sig_theta = None
        self.rho = None
        self.sig_rho = None
        self.pi_perp = None
        self.sig_pi_perp = None
        self.pi_para = None
        self.sig_pi_para = None
        self.chisq = None
        self.url = None

    def summary(self):
        output = self.event_name
        key_list = [ 's', 'q', 'u0', 't0', 'tE', 'theta', 'rho', 'pi_perp', \
                'pi_para', 'chisq']
        for key in key_list:
            (value,sigma) = self.get_par(key)
            if value != None:
                output = output + ' ' + key + ' = ' + str(value)
                if sigma != None:
                    output = output + '+/-' + str(sigma)
        return output

    def get_par(self,key):
        try:
            value = getattr(self,key)
        except AttributeError:
            value = None
        try:
            sigma = getattr(self,'sig_'+key)
        except AttributeError:
            sigma = None
        return value, sigma
        
    def get_params(self):
        params = {}
        key_list = [ 'event_name', 's', 'q', 'u0', 't0', 'tE', 'theta', \
                     'rho', 'pi_perp', 'pi_para', 'chisq', 'url' ]
        
        for key in key_list:
            (value,sigma) = self.get_par(key)
            if value != None:
                key_name = 'bozza_' + str(key).lower()
                params[key_name] = value
            if sigma != None:
                key_name = 'bozza_sig_' + str(key).lower()
                params[key_name] = sigma
        return params

class PSPL():
    
    def __init__(self):
        self.event_name = None
        self.t0 = None
        self.u0 = None
        self.te = None
        self.tstart = None
        self.tstop = None
        self.mag0 = None
        self.magt = None
        self.t = None
        self.ut = None
        self.At = None
    
    def set_params(self, params, prefix=None):
        if prefix != None:
            for key, value in params.items():
                if prefix in key:
                    entry = params.pop(key)
                    new_key = key.replace(prefix+'_','')
                    params[new_key] = value
        for key, value in params.items():
            if key not in [ 'event_name', 'magt', 't', 'ut', 'At' ]:
                setattr(self,key,float(value))
            else:
                setattr(self,key,value)
                
    def generate_lightcurve(self):
        
        # Generate the timeline for the lightcurve:
        self.t = np.arange( self.tstart, self.tstop, 0.01 )
        
        # Generate the impact parameter as a function of time
        # For PSPL, we assume a static observer.
        dt = ( self.t - self.t0 ) / self.te
        self.ut = np.sqrt( ( dt * dt ) + \
                     ( self.u0 * self.u0 ) )
        
        # Calculate the magnification as a function of time:
        self.At = ( self.ut * self.ut + 2.0 ) \
            / ( self.ut * np.sqrt( self.ut * self.ut + 4.0 ) )
        
        # Calculate the source brightness as a function of time:
        self.magt = self.mag0 - 2.5 * np.log10( self.At )
        
    def output_model_lightcurve(self, file_path, identifier, event_name):
        
        fileobj= open( file_path, 'w' )
        fileobj.write('# Model lightcurve data for ' + identifier + \
                            ' = ' + event_name + '\n')
        fileobj.write('#\n')
        fileobj.write('# Column 1: Timestamps in HJD\n')
        fileobj.write('# Column 2: Magnitudes\n')
        for i in range(0,len(self.t),1):
            fileobj.write( str(self.t[i]) + '   ' + str(self.magt[i]) + '\n' )
        fileobj.close()
        
            