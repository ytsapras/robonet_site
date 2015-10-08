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

    print ogle_lens_params

# Sync against database

# Harvest MOA information

# Harvest KMTNet information

##################################################
# LENS CLASS DESCRIPTION
class Lens():
    '''Class describing a microlensing event with point source point lens parameters'''

    def __init__(self):
        self.name = None
        self.ra = None
        self.dec = None
        self.t0 = None
        self.tE = None
        self.u0 = None
        self.A0 = None
        self.I0 = None

    def set_par(self,par,par_value):

        if par in [ 'name', 'ra', 'dec' ]: setattr(self,par,par_value)
        else: setattr(self,par,float(par_value))

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

    # Parse the timestamp in the last.changed file. The timestamp is given in yyyymmdd.daydecimal format:
    t = open( ts_file_path, 'r' ).readline()
    ts = datetime.strptime(t.split('.')[0],'%Y%m%d')
    dt = timedelta(days=float('0.'+t.split('.')[-1]))
    last_update = ts + dt

    # Parse the lenses parameter file.
    # First 2 lines are header, so skipped:
    file_lines = open( par_file_path, 'r' ).readlines()
    lens_params = {}
    for line in file_lines[2:]:
        (event_id, field, star, ra, dec, t0_hjd, t0_utc, tE, u0, A0, dmag, fbl, I_bl, I0) = line.split()
        if 'OGLE' not in event_id: event_id = 'OGLE-'+event_id
        event = Lens()
        event.set_par('name',event_id)
        event.set_par('ra',ra)
        event.set_par('dec',dec)
        event.set_par('t0',t0_hjd)
        event.set_par('tE',tE)
        event.set_par('u0',u0)
        event.set_par('A0',A0)
        event.set_par('I0',I0)
        lens_params[event_id] = event

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

