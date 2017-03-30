#!/usr/bin/python
######################################################################################################
#                                   ARTEMiS SUBSCRIBER
#
# Script to download the latest model parameters and data from ARTEMiS
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
from datetime import datetime
import log_utilities
from numpy import array
import event_classes

##############################
# CONFIG INTERPRETATION

# Data_type -> config parameter keys, file name search key
config_pars = { 'model': { 'remote_location': 'models_remote_location',
                           'local_location': 'models_local_location',
                           'log_root_name': 'models_log_root_name',
                               'search_key': '.model' },
                'pubpars': { 'remote_location': 'pubpars_remote_location',
                             'local_location': 'pubpars_local_location',
                             'log_root_name': 'pubpars_log_root_name',
                                 'search_key': '.model' },
                'data': { 'remote_location': 'data_remote_location',
                          'local_location': 'data_local_location',
                          'log_root_name': 'data_log_root_name',
                                 'search_key': '.dat' }
                }


###############################################
# MAIN DRIVER FUNCTION
def sync_artemis():
    '''Driver function to maintain an up to date copy of the data on all microlensing events from 
        the ARTEMiS server at Univ. of St. Andrews.
    '''
    
    # Read configuration:
    config_file_path = '/home/robouser/.robonet_site/artemis_sync.xml'
    config = config_parser.read_config(config_file_path)
    log = log_utilities.start_day_log( config, __name__ )
    log.info('Started sync with ARTEMiS server')
    
    # Sync the results of ARTEMiS' own model fits for all events:
    sync_artemis_data_db(config,'model',log)

    # Sync the event parameters published by the surveys from the ARTEMiS server:
    sync_artemis_data_db(config,'pubpars',log)

    # Sync the event photometry data from the ARTEMiS server:
    sync_artemis_data_db(config,'data',log)

    # Sync ARTEMiS' internal fileset, to gain access to the anomaly indicators:
    rsync_internal_data(config)

    # Tidy up and finish:
    log_utilities.end_day_log( log )
    
###############################################
# FUNCTION TO SYNC & PROCESS ARTEMiS DATA
def sync_artemis_data_db(config,data_type,log):
    '''Function to sync a local copy of the ARTEMiS model fit files for all events from the
       server at the Univ. of St. Andrews.
    '''
    
    log.info('Syncing '+data_type+' from ARTEMiS server')
    
    # Rsync the contents of ARTEMiS' model files directory, creating a log file listing
    # all files which were updated as a result of this rsync and hence which have been
    # updated.
    rsync_log_path = rsync_data_log(config,data_type)
    log.info('-> downloaded datalog')

    # Read the list of updated models:
    event_files = read_rsync_log(config,rsync_log_path,data_type)
    log.info('-> '+str(len(event_files))+' entries have been updated')

    
    # Loop over all updated models and update the database:
    for f in event_files:
        
        # Read the fitting model parameters from the model file:
        if data_type in ['model', 'pubpars']: 
            (event, last_modified) = read_artemis_model_file(f)
        else: 
            event_params = get_artemis_data_params(f)
        
        if data_type == 'model' and int(config['update_db']) == 1:
            log.info('-> Updating database')
            event.sync_event_with_DB(last_modified)


###########################
# RSYNC FUNCTION
def rsync_data_log(config,data_type):
    """Function to rsync data using authentication from file and log the 
    output to a text file.
    """

    # Construct config parameter keys to extract data locations and appropriate log file name:
    remote_location = config_pars[data_type]['remote_location']
    local_location = config_pars[data_type]['local_location']
    log_root_name = config_pars[data_type]['log_root_name']

    # Contruct and execute rsync commandline:
    ts = Time.now()          # Defaults to UTC
    ts = ts.now().iso.split('.')[0].replace(' ','T').replace(':','').replace('-','')
    log_path = path.join( config['rsync_log_directory'], config[log_root_name] + '_' + ts + '.log' )
    command = 'rsync -azu ' + \
               config['user_id'] + '@' + config['url'] + config[remote_location] + ' ' + \
               config[local_location] + ' ' + \
               '--password-file=' + config['auth'] + ' ' + \
                '--log-file=' + log_path

    args = command.split()
    p = subprocess.Popen(args)
    p.wait()

    return log_path

def rsync_internal_data(config):
    """Function to rsync Signalmen's internal data files. 
    Note: rsync connection to the ARTEMiS server at St. Andrews has the 
    annoying habit of doing a peer-reset if the rsync of data takes longer
    than ~15min. 
    """
    
     # Construct config parameter keys to extract data locations and appropriate log file name:
    local_location = config['internal_data_local_location']
    ts = Time.now()          # Defaults to UTC
    ts = ts.now().iso.split('.')[0].replace(' ','T').replace(':','').replace('-','')
    log_path = path.join( config['rsync_log_directory'], config['log_root_name'] + '_' + ts + '.log' )

    # Contruct and execute rsync commandline:
    command = 'rsync -avzu --delete SignalmenLink@mlrsync-stand.net::Signalmen ' + \
               local_location + ' --password-file=' + config['auth_internal'] + ' ' + \
                '--log-file=' + log_path
               
    args = command.split()
    p = subprocess.Popen(args)
    p.wait()
    
    
###########################
# READ RSYNC LOG
def read_rsync_log(config,log_path,data_type):
    '''Function to parse the rsync -azu log output and return a list of event model file paths with updated parameters.
    '''

    # Initialize, returning an empty list if no log file is found:
    event_model_files = []
    local_location = config_pars[data_type]['local_location']
    search_key = config_pars[data_type]['search_key']
    if path.isfile(log_path) == False: return event_model_files

    # Read the log file, parsing the contents into a list of model files to be updated.
    file = open(log_path,'r')
    file_lines = file.readlines()
    file.close()
    
    for line in file_lines:
        if search_key in line:
            file_name = line.split(' ')[-1].replace('\n','')
            if file_name[0:1] != '.' and len(file_name.split('.')) == 2:
                event_model_files.append( path.join( config[local_location], file_name ) )

    return event_model_files

###########################
# READ ARTEMIS MODEL FILE
def read_artemis_model_file(model_file_path):
    '''Function to read an ARTEMiS model file and parse the contents'''

    event = event_classes.Lens()
    
    if path.isfile(model_file_path) == True:
        file = open(model_file_path, 'r')
        lines = file.readlines()
        file.close()
        
        if len( lines ) > 0 and len( lines[0] ) > 0 \
            and lines[0].lstrip()[0:1] != '$':
            
            try: 
                entries = lines[0].split()
                ra = entries[0]
                dec = entries[1]
                (ra_deg, dec_deg) = utilities.sex2decdeg(ra,dec)
                event.set_par('ra',ra_deg)
                event.set_par('dec',dec_deg)
                short_name = entries[2]
                event.set_par('name',utilities.short_to_long_name(short_name)
                event.set_par('t0',float(entries[3]) + 2450000.0)
                event.set_par('e_t0',float(entries[4]))
                event.set_par('te',float(entries[5]))
                event.set_par('e_te',float(entries[6]))
                event.set_par('umin',float(entries[7]))
                event.set_par('e_umin',float(entries[8]))
        
                ts = path.getmtime(model_file_path)
                ts = datetime.fromtimestamp(ts)
                last_modified = ts
            
            # In case of a file with zero content
            except IndexError: 
                pass
            
            # In case of mal-formed file content:
            except ValueError:
                pass
                
    return event, last_modified

###############################
# ARTEMIS PHOTOMETRY FILE IO
def read_artemis_data_file(data_file_path):
    """Function to read and parse the contents of an ARTEMiS-format 
    photometry file.
    """
    allowed_providers = [ 'D', 'E', 'F', 'R', 'S', 'T', 'X', 'Y', \
                        's', 'L', 'Z', 'P', 'Q' ]
    ndata = {}
    data = []
    if path.isfile(data_file_path) == True:
        file_lines = open(data_file_path,'r').readlines()
        
        for line in file_lines:
            entries = line.split()
            provider = entries[3]
            ts = entries[5]
            mag = entries[6]
            merr = entries[7]
            if provider in allowed_providers:
                data.append( [ ts, mag, merr, provider] )
            if provider not in ndata.keys():
                ndata[provider] = 1
            else:
                ndata[provider] = ndata[provider] + 1
    data = array(data)
    
    return ndata, data

def get_artemis_data_params(data_file_path):
    '''Function to obtain information about the ARTEMiS-format photometry data file,
    without reading the whole file.'''

    params = {}
    if path.isfile(data_file_path) == True:
        params['short_name'] = path.basename(data_file_path).split('.')[0]
        params['long_name'] = utilities.short_to_long_name( params['short_name'] )
    
        # Find and read the last entry in the file, without reading the whole file
        st_results = stat(data_file_path)
        st_size = max(0,(st_results[6] - 200))
        data_file = open(data_file_path,'r')
        data_file.seek(st_size)
        last_lines = data_file.readlines()
        params['last_JD'] = float(last_lines[-1].split()[2])
        params['last_mag'] = float(last_lines[-1].split()[0])
    
        # Ask the OS how many datapoints are in the file.
        # Turns out there isn't an easy Python way to do this without
        # reading the whole file, so ask the OS.  Then decrement the number
        # of lines to account for the 1-line header.
        command = 'wc -l '+data_file_path
        args = command.split()
        p = subprocess.Popen(args,stdout=subprocess.PIPE, bufsize=1)
        p.wait()
        params['ndata'] = int(str(p.stdout.readline()).split()[0]) - 1
        
    return params

def check_anomaly_status(internal_data_path, params, log=None, debug=False):
    """Function to check the ARTEMiS anomaly flag.  Adds parameter anomaly to 
    the input dictionary, set to 0 for no anomaly or 1.  Input dictionary
    requires short_name parameter.
    """
    
    anomaly_file = path.join( internal_data_path, params['short_name']+'.anomaly' )
    if log != None and debug == True:
        log.info('Checking for ARTEMiS anomaly flag with file name: '+anomaly_file)
        
    if path.isfile(anomaly_file) == True:
        params['anomaly'] = 1
    else:
        params['anomaly'] = 0
        
    if log != None and params['anomaly'] == 1 and debug == True:
        log.info(' -> Got anomaly status = ' + str(params['anomaly']) )
        
    return params

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

    sync_artemis()
