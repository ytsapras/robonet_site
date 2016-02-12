#!/usr/bin/python
######################################################################################################
#                                   SURVEY SUBSCRIBER
#
# Script to download the latest model parameters and data from the microlensing surveys and
# cross-check it against the contents of the DB
######################################################################################################

#########################
# PACKAGE IMPORT
import config_parser
from astropy.time import Time
import subprocess
from sys import exit
from os import path, stat
#import update_db
import utilities
from datetime import datetime, timedelta
import ftplib

#################################################
# MAIN DRIVER FUNCTION
def sync_surveys():
    '''Driver function to subscribe to the alerts of microlensing events produced by surveys OGLE, MOA
    and KMTNet.  The function downloads their model parameters and data wherever available. 
    '''

    # Read script configuration:
    config_file_path = '../configs/surveys_sync.xml'
    config = config_parser.read_config(config_file_path)
    verbose(config,'Started sync of survey data')

    # Harvest parameters of lenses detected by OGLE
    (ogle_last_update, ogle_lens_params) = get_ogle_parameters(config)


# Sync against database

    # Harvest MOA information
    (moa_last_update, moa_lens_params) = get_moa_parameters(config)

# Sync against database

    # Harvest KMTNet information
    # KMTNet are not producing alerts yet
    #get_kmtnet_parameters(config)

##################################################
# LENS CLASS DESCRIPTION
class Lens():
    '''Class describing a microlensing event with point source point lens parameters'''

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


##################################################
# FUNCTION GET OGLE PARAMETERS
def get_ogle_parameters(config):
    '''Function to download the parameters of lensing events from the OGLE survey. 
    OGLE make these available via anonymous FTP from ftp.astrouw.edu.pl in the form of two files.
    ogle/ogle4/ews/last.changed   contains a yyyymmdd.daydecimal timestamp of the time of last update
    ogle/ogle4/ews/<year>/lenses.par   contains a list of all known lenses with the following columns:
        Event     Field   StarNo  RA(J2000)   Dec(J2000)   Tmax(HJD)   Tmax(UT)      tau     umin  Amax  Dmag   fbl  I_bl    I0
    
    This function returns the parameters of all the lenses as a dictionary, plus a datetime object of the last changed date.
    '''

    verbose(config,'Syncing data from OGLE')

    # Fetch the parameter files from OGLE via anonymous FTP
    ftp = ftplib.FTP( config['ogle_ftp_server'] )
    ftp.login()
    ftp_file_path = path.join( 'ogle', 'ogle4', 'ews' )
    ts_file_path = path.join( config['ogle_data_local_location'], 'last.changed' )
    ftp.cwd(ftp_file_path)
    ftp.retrbinary('RETR last.changed', open( ts_file_path, 'w').write )
    ts = Time.now()
    ftp_file_path = path.join( str(ts.utc.now().value.year) )
    ftp.cwd(ftp_file_path)
    par_file_path = path.join( config['ogle_data_local_location'], 'lenses.par' )
    ftp.retrbinary('RETR lenses.par', open( par_file_path, 'w').write )
    ftp.quit()

    ( last_update, lens_params ) = read_ogle_param_files( config )

    return last_update, lens_params

def read_ogle_param_files( config ):
    """Method to read the listing of OGLE data"""
    
    ts_file_path = path.join( config['ogle_data_local_location'], \
                            config['ogle_time_stamp_file'] )
    par_file_path = path.join( config['ogle_data_local_location'], \
                            config['ogle_lenses_file'] )
    
    # Parse the timestamp in the last.changed file. The timestamp is given in yyyymmdd.daydecimal format:
    t = open( ts_file_path, 'r' ).readline()
    ts = datetime.strptime(t.split('.')[0],'%Y%m%d')
    dt = timedelta(days=float('0.'+t.split('.')[-1]))
    last_update = ts + dt
    verbose(config,'--> Last udpated at: '+t.replace('\n',''))

    # Parse the lenses parameter file.
    # First 2 lines are header, so skipped:
    file_lines = open( par_file_path, 'r' ).readlines()
    lens_params = {}
    for line in file_lines[2:]:
        (event_id, field, star, ra, dec, t0_hjd, t0_utc, tE, u0, A0, dmag, fbl, I_bl, I0) = line.split()
        if 'OGLE' not in event_id: event_id = 'OGLE-'+event_id
        (ra_deg, dec_deg) = utilities.sex2decdeg(ra,dec)
        event = Lens()
        event.set_par('name',event_id)
        event.set_par('ra',ra_deg)
        event.set_par('dec',dec_deg)
        event.set_par('t0',t0_hjd)
        event.set_par('te',tE)
        event.set_par('u0',u0)
        event.set_par('a0',A0)
        event.set_par('i0',I0)
        event.origin = 'OGLE'
        lens_params[event_id] = event
    verbose(config,'--> Downloaded index of ' + str(len(lens_params)) + ' events')

    return last_update, lens_params

###################################################
# FUNCTION GET MOA PARAMETERS
def get_moa_parameters(config):
    '''Function to download the parameters of lensing events detected by the MOA survey.  
        MOA make these available via their websites:
        https://it019909.massey.ac.nz/moa/alert<year>/alert.html
        https://it019909.massey.ac.nz/moa/alert<year>/index.dat
        '''
    
    verbose(config,'Syncing data from MOA')
    
    # Download the website with MOA alerts, which contains the last updated date.
    # Note that although the URL prefix has to be https, this isn't actually a secure page
    # so no login is required.
    ts = Time.now()
    year_string = str(ts.utc.now().value.year)
    url = 'https://it019909.massey.ac.nz/moa/alert' + year_string + '/alert.html'
    (alerts_page_data,msg) = utilities.get_http_page(url)

    # The last updated timestamp is one of the last lines in this file:
    alerts_page_data = alerts_page_data.split('\n')
    i = len(alerts_page_data) - 1
    while i >= 0:
        if 'last updated' in alerts_page_data[i]:
            t = alerts_page_data[i].split(' ')[-2]
            last_update = datetime.strptime(t.split('.')[0],'%Y-%m-%dT%H:%M:%S')
            i = -1
        i = i - 1
    file_path = path.join( config['moa_data_local_location'], 'last.changed' )
    fileobj = open( file_path, 'w' )
    fileobj.write( t + '\n' )
    fileobj.close()
    verbose(config,'--> Last udpated at: '+t)
    

    # Download the index of events:
    url = 'https://it019909.massey.ac.nz/moa/alert' + year_string + '/index.dat'
    (events_index_data,msg) = utilities.get_http_page(url)
    events_index_data = events_index_data.split('\n')
    
    # Parse the index of events
    lens_params = {}
    for entry in events_index_data:
        if len(entry.replace('\n','').replace(' ','')) > 0:
            (event_id, field, ra_deg, dec_deg, t0_hjd, tE, A0, \
                        I0, tmp1, tmp2) = entry.split()
            if ':' in ra_deg or ':' in dec_deg: (ra_deg, dec_deg) = \
                                utilities.sex2decdeg(ra_deg,dec_deg)
            event = Lens()
            event.set_par('name','MOA-' + event_id)
            event.set_par('ra',ra_deg)
            event.set_par('dec',dec_deg)
            event.set_par('t0',t0_hjd)
            event.set_par('te',tE)
            event.set_par('i0',I0)
            event.set_par('a0',A0)
            event.origin = 'MOA'
            lens_params[event_id] = event
    verbose(config,'--> Downloaded index of ' + str(len(lens_params)) + \
                        ' events')

    # The MOA download is read directly from the website and thus produces
    # no record on disc.  Therefore we output one here in a more readable 
    # format than HTML:
    file_path = path.join( config['moa_data_local_location'], 'moa_lenses.par' )
    fileobj = open(file_path,'w')
    fileobj.write('# Name       RA      Dec     T0       TE      u0      A0    i0\n')
    for event_id, event in lens_params.items():
        fileobj.write( event.summary() + '\n' )
    fileobj.close()

    return last_update, lens_params

####################################################
# FUNCTION GET KMTNET PARAMETERS
def get_kmtnet_parameters(config):
    '''Function to retrieve all available information on KMTNet-detected events from the HTML table at:
    http://astroph.chungbuk.ac.kr/~kmtnet/<year>.html'''

    verbose(config,'Syncing data from KMTNet')

    # Download the website indexing KMTNet-discovered events for the current year:
    ts = Time.now()
    year_string = str(ts.utc.now().value.year)
    url = 'http://astroph.chungbuk.ac.kr/~kmtnet/' + year_string + '.html'
    events_index_data = utilities.get_secure_url(url,(None,None))

    events_index_data = events_index_data.split('\n')

    # Parse the index of events.  KMTNet don't provide very much information on their discoveries yet.
    lens_params = {}
    i = 0
    while i < len(events_index_data):
        entry = events_index_data[i]
        if 'KMT' in entry:
            entry = [ entry ] + events_index_data[i+1].split()
            event_id = entry[0].replace(' ','')
            (ra_deg, dec_deg) = utilities.sex2decdeg( entry[1], entry[2] )
            event = Lens()
            event.set_par('name',event_id)
            event.set_par('ra',ra_deg)
            event.set_par('dec',dec_deg)
            event.origin = 'KMTNET'
            lens_params[event_id] = event
            i = i + 2
        else:
            i = i + 1

    # KMTNet do not provide a last-updated timestamp anywhere, so setting this to
    # the current time for now:
    last_update = datetime.utcnow()
    
    verbose(config,'--> Last udpated at: ' + last_update.strftime("%Y-%m-%dT%H:%M:%S"))
    verbose(config,'--> Downloaded index of ' + str(len(lens_params)) + ' events')


    return last_update, lens_params

################################
# VERBOSE OUTPUT FORMATTING
def verbose(config,record):
    '''Function to output logging information if the verbose config flag is set'''
    
    if bool(config['verbose']) == True:
        ts = Time.now()          # Defaults to UTC
        ts = ts.now().iso.split('.')[0].replace(' ','T')
        print ts+': '+record

###########################
# COMMANDLINE RUN SECTION:
if __name__ == '__main__':
    
    sync_surveys()

