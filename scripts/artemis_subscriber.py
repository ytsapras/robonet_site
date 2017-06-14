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
import pwd
#import update_db
import utilities
from datetime import datetime
import pytz
import log_utilities
from numpy import array
import event_classes
import update_db_2
import socket
import mmap
import pytz
import get_errors

version = 1.0

def sync_artemis():
    """Driver function to maintain an up to date copy of the data on all microlensing events from 
    the ARTEMiS server at Univ. of St. Andrews.
    
    This function downloads all the various data products from ARTEMiS:
    - the results of ARTEMiS' own model fits for all events ('model'),
    - the event parameters published by the surveys ('pubpars'),
    - the event photometry data from the ARTEMiS server ('data'),
    - ARTEMiS' internal fileset, to gain access to the anomaly indicators
    """

    config = read_config()

    log = init_log(config)
    
    status = check_rsync_config(config,log=log)
    
    if status == True:
        sync_artemis_data_db(config,'model',log)
        
        sync_artemis_data_db(config,'pubpars',log)
        
        sync_artemis_data_db(config,'data',log)
        
        rsync_internal_data(config)
    
    log_utilities.end_day_log( log )


def read_config():
    """Function to establish the configuration of this script from the users
    local XML file"""
    
    host_machine = socket.gethostname()
    if 'cursa' in host_machine:
        config_file_path = '/home/Tux/ytsapras/robonet_site/configs/artemis_sync.xml'
    elif 'rachel' in host_machine or 'Rachel' in host_machine:
        config_file_path = '/Users/rstreet/.robonet_site/artemis_sync.xml'
    else:
        config_file_path = '/var/www/robonetsite/configs/artemis_sync.xml'
    
    if path.isfile(config_file_path) == False:
        print 'ERROR: Cannot find configuration file, looked for '+config_file_path
        exit()

    config = config_parser.read_config(config_file_path)
    
    config['data_locations'] = {
                 'model': { 'remote_location': 'models_remote_location',
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
    config['version'] = 'artemis_subscriber_'+str(version)
    config['update_db'] = bool(config['update_db'])
    config['verbose'] = bool(config['verbose'])
    
    return config

def init_log(config):
    """Function to initialize the artemis subscriber log with relevant 
    script configguration info"""
    
    log = log_utilities.start_day_log(config, __name__)

    log.info('Started sync with ARTEMiS server\n')
    log.info('Script version: '+config['version'])
    if config['update_db'] == False:
        log.info('\nWARNING: Database update switched OFF in configuration!\n')
    else:
        log.info('Database update switched ON, normal operation')
    return log

def check_rsync_config(config,log=None):
    """Function to verify that the rsync configuration to ARTEMiS is OK"""
    
    status = True
    for file_path in [config['auth'], config['auth_internal']]:
        uidcode = stat(file_path).st_uid
        uid = pwd.getpwuid(uidcode).pw_name
        if uid != 'root':
            error_report = 'ERROR with rsync authorization file permissions'
            if log!=None:
                log.info(path.basename(file_path)+': '+error_report)
            get_errors.update_err('artemis_subscriber', error_report)
            status = False
    if status == True:
        get_errors.update_err('artemis_subscriber', 'Status OK')
        
    return status

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
    event_files = read_rsync_log(config,rsync_log_path,data_type,log=log)
    log.info('-> '+str(len(event_files))+' entries have been updated')
    
    
    # Loop over all updated models and update the database:
    if data_type == 'model' and int(config['update_db']) == 1:
        if config['verbose'] == True:
            log.info('Syncing contents of ARTEMiS model files with DB:')
        for f in event_files:
            sync_model_file_with_db(config,f,log)

    # Loop over all updated data files and update the database:
    if data_type == 'data' and int(config['update_db']) == 1:
        if config['verbose'] == True:
            log.info('Syncing contents of ARTEMiS data files with DB:')
        for f in event_files:
            a = path.basename(f).split('.')[0][1:-1]+'.align'
            a = path.join(config['models_local_location'],a)
            if config['verbose'] == True:
                log.info(' -> '+f+' '+a)
            sync_data_align_files_with_db(config,f,a,log)

def sync_model_file_with_db(config,model_file,log):
    """Function to read an ARTEMiS-format .model file and sync its contents
    with the database"""
    
    (event, last_modified) = read_artemis_model_file(model_file)
    log.info('Read details of event '+str(event.name)+' from file '+model_file)
    
    if event.ra != None and event.dec != None:
        if int(config['update_db']) == 1:
            if config['verbose'] == True:
                log.info('-> Updating '+path.basename(model_file))
            event.sync_event_with_DB(last_modified,log=log,debug=config['verbose'])
        else:
            log.info('-> Warning: Database update switched off in configuration')
    else:
        log.info('-> ERROR: could not parse model file.  Old format?')

def sync_data_align_files_with_db(config,data_file,align_file,log):
    """Function to ensure the DB record of the latest data is up to date"""
    
    if log!=None:
        log.info('Syncing ARTEMiS data and align parameters with DB')
    short_name = path.basename(data_file).split('.')[0][1:-1]
    filt = path.basename(data_file).split('.')[0][-1:]
    origin = path.basename(data_file).split('.')[0][0:1]
    tel = look_up_origin(origin)
    ndata = mapcount_file_lines(data_file)
    if ndata > 0:
        (first, last) = read_first_and_last(data_file)
        last_mag = float(last.split()[0])
        last_hjd = float(last.split()[2])
        if last_hjd < 2450000.0:
            last_hjd = last_hjd + 2450000.0
    else:
        last_mag = 0.0
        last_hjd = 0.0
    last_upd = datetime.fromtimestamp(path.getmtime(data_file))
    last_upd = last_upd.replace(tzinfo=pytz.UTC)
    align_pars = read_artemis_align_params(align_file,filt)

    params = {'event_name': utilities.short_to_long_name(short_name),
              'datafile': data_file,
              'last_mag': last_mag,
              'last_hjd': last_hjd,
              'tel': tel,
              'filt': filt,
              'baseline': align_pars['baseline'],
              'g': align_pars['g'],
              'ndata': mapcount_file_lines(data_file),
              'last_upd': last_upd,
              }
    (status,message) = update_db_2.add_datafile_via_api(params)
    if log!=None:
        log.info(' -> Status: '+repr(status)+', '+message)
    
def look_up_origin(origin):
    """Function to return the full telescope ID for common survey names"""
    
    tel_codes = { 'O': 'OGLE 1.3m', 
                 'K': 'MOA 1.8m',
                 'L': 'Danish LuckyCam 1.54m' }
    if origin in tel_codes.keys():
        tel = tel_codes[origin]
    else:
        tel = origin
    return tel

def read_first_and_last(file_path):
    """Function (thank you Stack Overflow) to read the first and last
    line of a file"""
    
    with open(file_path, "rb") as f:
        first = f.readline()
        if '#' in first[0:1]:
            first = f.readline()
        f.seek(-2, 2)             # Jump to the second last byte.
        try:
            while f.read(1) != b"\n": # Until EOL is found...
                f.seek(-2, 1)         # ...jump back the read byte plus one more.
        except IOError:
            print file_path
        last = f.readline()       # Read last line.
    return first, last

def mapcount_file_lines(file_path):
    """Function (thank you again Stack Overflow) to count the number of 
    lines in a file efficiently by using memory mapping.
    Function counts all lines of the file, subtracting the assumed 1-line header
    """
    f = open(file_path, "r+")
    buf = mmap.mmap(f.fileno(), 0)
    lines = 0
    readline = buf.readline
    while readline():
        lines += 1
    lines -= 1
    return lines

###########################
# RSYNC FUNCTION
def rsync_data_log(config,data_type):
    """Function to rsync data using authentication from file and log the 
    output to a text file.
    """
    
    # Construct config parameter keys to extract data locations and appropriate log file name:
    remote_location = config['data_locations'][data_type]['remote_location']
    local_location = config['data_locations'][data_type]['local_location']
    log_root_name = config['data_locations'][data_type]['log_root_name']
    
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
    command = 'rsync -azu --delete SignalmenLink@mlrsync-stand.net::Signalmen ' + \
               local_location + ' --password-file=' + config['auth_internal'] + ' ' + \
                '--log-file=' + log_path
          
    args = command.split()
    p = subprocess.Popen(args)
    p.wait()
    
    
###########################
# READ RSYNC LOG
def read_rsync_log(config,log_path,data_type,log=None):
    '''Function to parse the rsync -azu log output and return a list of event model file paths with updated parameters.
    '''
    
    # Initialize, returning an empty list if no log file is found:
    event_model_files = []
    local_location = config['data_locations'][data_type]['local_location']
    search_key = config['data_locations'][data_type]['search_key']
    if path.isfile(log_path) == False: 
        if log!=None:
            log.info('ERROR: cannot find log path: '+log_path)
        return event_model_files
    
    # Read the log file, parsing the contents into a list of model files to be updated.
    file = open(log_path,'r')
    file_lines = file.readlines()
    file.close()
    if log!=None:
        log.info('Read list of '+str(len(file_lines))+' model files')
        
    for line in file_lines:
        if search_key in line:
            file_name = line.split(' ')[-1].replace('\n','')
            if file_name[0:1] != '.' and len(file_name.split('.')) == 2 and \
                'index.dat' not in file_name:
                event_model_files.append( path.join( config[local_location], file_name ) )
    if log!=None:
        log.info('Extracted list of '+str(len(event_model_files))+' model files to be processed')
    
    return event_model_files

###########################
# READ ARTEMIS MODEL FILE
def read_artemis_model_file(model_file_path):
    '''Function to read an ARTEMiS model file and parse the contents'''
    
    event = event_classes.Lens()
    last_modified = None
    
    if path.isfile(model_file_path) == True:
        file = open(model_file_path, 'r')
        lines = file.readlines()
        file.close()
        
        if len( lines ) > 0 and len( lines[0] ) > 0 \
            and lines[0].lstrip()[0:1] != '$':
            
            try: 
                entries = lines[0].split()
                # Catch to avoid ingesting old-format ARTEMiS model files which
                # do not contain the RA, Dec info
                if ':' in entries[0] and ':' in entries[1]:
                    ra = entries[0]
                    dec = entries[1]
                    event.set_par('ra',ra)
                    event.set_par('dec',dec)
                    short_name = entries[2]
                    event.set_par('name',utilities.short_to_long_name(short_name))
                    event.set_par('t0',float(entries[3]) + 2450000.0)
                    event.set_par('e_t0',float(entries[4]))
                    event.set_par('te',float(entries[5]))
                    event.set_par('e_te',float(entries[6]))
                    event.set_par('u0',float(entries[7]))
                    event.set_par('e_u0',float(entries[8]))
    
                    survey_code = path.basename(model_file_path)[0:2]
                    if survey_code == 'OB':
                        event.set_par('origin','OGLE')
                    elif survey_code == 'KB':
                        event.set_par('origin','MOA')
                    event.modeler = 'ARTEMiS'
                    
                    ts = path.getmtime(model_file_path)
                    ts = datetime.fromtimestamp(ts)
                    ts = ts.replace(tzinfo=pytz.UTC)
                    last_modified = ts
                    event.set_par('last_updated',ts)
                
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

def read_artemis_align_params(data_file,filt):
    """Function to read the parameters from the ARTEMiS' format .align file"""
    
    params = {'name_code': '', 
              'baseline': 0.0,
              'g': 0.0
              }
    if 'OB' in path.basename(data_file):
        origin = 'O'
    elif 'KB' in path.basename(data_file):
        origin = 'K'
    else:
        origin  = 'U'
    code = origin+filt
    
    if path.isfile(data_file) == True:
        file_lines = open(data_file,'r').readlines()
        for line in file_lines:
            entries = line.split()
            if entries[0] == code:
                params['name_code'] = entries[0]
                params['baseline'] = float(entries[1])
                params['g'] = float(entries[2])
    
    return params

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
