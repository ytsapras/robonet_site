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
import survey_data_utilities
import event_classes
import survey_classes

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
    ogle_data = get_ogle_parameters(config)


# Sync against database

    # Harvest MOA information
    ogle_data = get_moa_parameters(config)

# Sync against database

    # Harvest KMTNet information
    # KMTNet are not producing alerts yet
    #get_kmtnet_parameters(config)

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
    ogle_data = survey_classes.SurveyData()
    years = [ '2015', '2016' ]
    
    # Fetch the parameter files from OGLE via anonymous FTP
    ftp = ftplib.FTP( config['ogle_ftp_server'] )
    ftp.login()
    ftp_file_path = path.join( 'ogle', 'ogle4', 'ews' )
    ts_file_path = path.join( config['ogle_data_local_location'], 
                             config['ogle_time_stamp_file'] )
    ftp.cwd(ftp_file_path)
    ftp.retrbinary('RETR last.changed', open( ts_file_path, 'w').write )
    ts = Time.now()
    for year in years:    
        ftp_file_path = path.join( str(year) )
        ftp.cwd(ftp_file_path)
        par_file_path = path.join( config['ogle_data_local_location'], \
                                    config['ogle_lenses_file']+'.'+str(year) )
        ftp.retrbinary('RETR lenses.par', open( par_file_path, 'w').write )
        ftp.cwd('../')
    ftp.quit()
    
    ogle_data = survey_data_utilities.read_ogle_param_files( config )
        
    verbose(config,'--> Last updated at: ' + \
            ogle_data.last_changed.strftime("%Y-%m-%dT%H:%M:%S"))
    verbose(config,'--> Downloaded index of ' + str(len(ogle_data.lenses)) + \
                        ' events')


    update_file_path = path.join( config['ogle_data_local_location'], \
                                        config['ogle_updated_file']  )
    ogle_data.last_updated = \
        survey_data_utilities.write_update_file( update_file_path )
        
    return ogle_data

###################################################
# FUNCTION GET MOA PARAMETERS
def get_moa_parameters(config):
    '''Function to download the parameters of lensing events detected by the MOA survey.  
        MOA make these available via their websites:
        https://it019909.massey.ac.nz/moa/alert<year>/alert.html
        https://it019909.massey.ac.nz/moa/alert<year>/index.dat
        '''
    
    verbose(config,'Syncing data from MOA')
    moa_data = survey_classes.SurveyData()
    years = [ '2015', '2016' ]
    
    # Download the website with MOA alerts, which contains the last updated date.
    # Note that although the URL prefix has to be https, this isn't actually a secure page
    # so no login is required.
    ts = Time.now()
    for year in years: 
        
        # For the last year only, fetch the last-updated timestamp:
        if year == years[-1]:
            url = 'https://it019909.massey.ac.nz/moa/alert' + year + '/alert.html'
            (alerts_page_data,msg) = utilities.get_http_page(url)

            # The last updated timestamp is one of the last lines in this file:
            alerts_page_data = alerts_page_data.split('\n')
            i = len(alerts_page_data) - 1
            while i >= 0:
                if 'last updated' in alerts_page_data[i]:
                    t = alerts_page_data[i].split(' ')[-2]
                    last_changed = datetime.strptime(t.split('.')[0],'%Y-%m-%dT%H:%M:%S')
                    i = -1
                    i = i - 1
            ts_file_path = path.join( config['moa_data_local_location'], \
                                config['moa_time_stamp_file'] )
            fileobj = open( ts_file_path, 'w' )
            fileobj.write( t + '\n' )
            fileobj.close()
            verbose(config,'--> Last updated at: '+t)
            moa_data.last_changed = \
                survey_data_utilities.time_stamp_file( ts_file_path, \
                                                "%Y-%m-%dT%H:%M:%S" )

        # Download the index of events:
        url = 'https://it019909.massey.ac.nz/moa/alert' + year + '/index.dat'
        (events_index_data,msg) = utilities.get_http_page(url)
        events_index_data = events_index_data.split('\n')
    
        # Parse the index of events
        for entry in events_index_data:
            if len(entry.replace('\n','').replace(' ','')) > 0:
                (event_id, field, ra_deg, dec_deg, t0_hjd, tE, A0, \
                        I0, tmp1, tmp2) = entry.split()
                if ':' in ra_deg or ':' in dec_deg: 
                    (ra_deg, dec_deg) = utilities.sex2decdeg(ra_deg,dec_deg)
                event = event_classes.Lens()
                event.set_par('name','MOA-' + event_id)
                event.set_par('ra',ra_deg)
                event.set_par('dec',dec_deg)
                event.set_par('t0',t0_hjd)
                event.set_par('te',tE)
                event.set_par('i0',I0)
                event.set_par('a0',A0)
                event.origin = 'MOA'
                moa_data.lenses[event_id] = event
    verbose(config,'--> Downloaded index of ' + str(len(moa_data.lenses)) + \
                        ' events')
                        
    # The MOA download is read directly from the website and thus produces
    # no record on disc.  Therefore we output one here in a more readable 
    # format than HTML:
    file_path = path.join( config['moa_data_local_location'], \
                          config['moa_lenses_file'] )
    fileobj = open(file_path,'w')
    fileobj.write('# Name       RA      Dec     T0       TE      u0      A0    i0\n')
    for event_id, event in moa_data.lenses.items():
        fileobj.write( event.summary() + '\n' )
    fileobj.close()

    update_file_path = path.join( config['moa_data_local_location'], \
                                        config['moa_updated_file']  )
    moa_data.last_updated = \
        survey_data_utilities.write_update_file( update_file_path )

    return moa_data

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
            event = event_classes.Lens()
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

