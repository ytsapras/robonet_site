#!/usr/bin/python
######################################################################################################
#                            ARTEMiS MODEL SUBSCRIBER
#
# Script to download the latest model parameters from ARTEMiS
######################################################################################################

#########################
# PACKAGE IMPORT
import config_parser
from astropy.time import Time
import subprocess
from sys import exit
from os import path
#import update_db
import utilities
from datetime import datetime

#########################
# MAIN FUNCTION
def sync_artemis_models():
    '''Function to sync a local copy of the ARTEMiS model fit files for all events from the
       server at the Univ. of St. Andrews.
    '''

    # Read configuration:
    config_file_path = '../configs/artemis_sync.xml'
    config = config_parser.read_config(config_file_path)

    # Rsync the contents of ARTEMiS' model files directory, creating a log file listing
    # all files which were updated as a result of this rsync and hence which have been
    # updated.
    rsync_log_path = rsync_data_log(config)

    # Read the list of updated models:
    event_model_files = read_rsync_log(config,rsync_log_path)
    
    # Loop over all updated models and update the database:
    for model_file in event_model_files:
        
        # Read the fitting model parameters from the model file:
        event_params = read_artemis_model_file(model_file)

        # Query the DB to check whether the event exists in the database already:
        event_exists = update_db.check_exists(event_params['long_name'])

        # If event is known to the DB, submit the updated model parameters as a new model object:
        if event_exists == True: update_db.single_lens_par( event_params['long_name'],
                                                            event_params['t0'],
                                                            event_params['sig_t0'],
                                                            event_params['tE'],
                                                            event_params['sig_tE'],
                                                            event_params['u0'],
                                                            event_params['sig_u0'],
                                                            event_params['last_modified'] )

    # If the event is unknown to the DB, create an entry for it, updating it with all
    # currently known information:

    # Log the update in the script log:

###########################
# RSYNC FUNCTION
def rsync_data_log(config):
    '''Function to rsync data using authentication from file and log the output to a text file.
    '''

    # Contruct and execute rsync commandline:
    ts = Time.now()          # Defaults to UTC
    ts = ts.now().iso.split('.')[0].replace(' ','T').replace(':','').replace('-','')
    log_path = path.join( config['log_directory'], config['log_root_name'] + '_' + ts + '.log' )
    command = 'rsync -azu ' + \
               config['user_id'] + '@' + config['url'] + config['remote_location'] + ' ' + \
               config['model_data_directory'] + ' ' + \
               '--password-file=' + config['auth'] + ' ' + \
                '--log-file=' + log_path

    args = command.split()
    p = subprocess.Popen(args)
    p.wait()

    return log_path

###########################
# READ RSYNC LOG
def read_rsync_log(config,log_path):
    '''Function to parse the rsync -azu log output and return a list of event model file paths with updated parameters.
    '''

    # Initialize, returning an empty list if no log file is found:
    event_model_files = []
    if path.isfile(log_path) == False: return event_model_files

    # Read the log file, parsing the contents into a list of model files to be updated.
    file = open(log_path,'r')
    file_lines = file.readlines()
    file.close()

    for line in file_lines:
        if 'model' in line:
            file_name = line.split(' ')[-1].replace('\n','')
            event_model_files.append( path.join( config['model_data_directory'], file_name ) )

    return event_model_files

###########################
# READ ARTEMIS MODEL FILE
def read_artemis_model_file(model_file_path):
    '''Function to read an ARTEMiS model file and parse the contents'''

    params = {}
    
    if path.isfile(model_file_path) == True:
        file = open(model_file_path, 'r')
        line = file.readlines()
        file.close()
        
        entries = line[0].split()
        
        params['ra'] = entries[0]
        params['dec'] = entries[1]
        params['short_name'] = entries[2]
        params['long_name'] = utilities.short_to_long_name( params['short_name'] )
        params['t0'] = entries[3]
        params['sig_t0'] = entries[4]
        params['tE'] = entries[5]
        params['sig_tE'] = entries[6]
        params['u0'] = entries[7]
        params['sig_u0'] = entries[8]
        params['chi2'] = entries[9]
        params['ndata'] = entries[10]
    
        ts = path.getmtime(model_file_path)
        ts = datetime.fromtimestamp(ts)
        params['last_modified'] = ts
    
    return params

###########################
# COMMANDLINE RUN SECTION:
if __name__ == '__main__':

    sync_artemis_models()
