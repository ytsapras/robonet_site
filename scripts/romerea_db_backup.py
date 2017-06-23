from os import path, makedirs, chdir, getcwd
from sys import exit, stdout
import logging
import subprocess
from datetime import datetime
import log_utilities
import config_parser
import socket
import get_errors

def backup_database():
    """Function to automatically back-up the ROMEREA database"""
    
    config = read_config()
    
    log = log_utilities.start_day_log( config, config['log_root_name'] )

    log.info('Executing rsync command: '+config['rsync_command'])
    child = subprocess.Popen(config['rsync_command'].split(' '),
                                  shell=False, stderr=subprocess.PIPE)
    while True:
        err = child.stderr.readlines()
        for e in err:
            log.info(e)
            
            get_errors.update_err('backup', \
                            'ERROR encountered backing-up ROME/REA database')
        if child.poll() != None:
            break
    if len(err) == 0:
        get_errors.update_err('backup', \
                            'Status OK')
    
    log.info('Completed DB back-up')
    log_utilities.end_day_log(log)

def read_config():
    """Function to read the back-up script configuration file.
    Returns a dictionary of the config parameters from the XML file. 
    """
    
    host_name = socket.gethostname()
    if 'rachel' in host_name:
        cwd = getcwd()
        config_file_path = path.join(path.expanduser('~'),'.robonet_site','backup_config.xml')
    else:
        config_file_path = '/var/www/robonetsite/configs/backup_config.xml'
        
    if path.isfile(config_file_path) == False:
        raise IOError('Cannot find configuration file, looking for:'+config_file_path)
    
    config = config_parser.read_config(config_file_path)

    ts = datetime.utcnow()
    ts = ts.strftime("%Y-%m-%dT%H:%M:%S")
    db_path = config['db_location']
    db_file = path.basename(db_path)+'_'+ts
    bkup_path = path.join(config['backup_dir'], db_file)
    config['rsync_command'] = 'rsync -a ' + db_path + ' ' + bkup_path

    if path.isdir(config['backup_dir']) == False:
        makedirs(config['backup_dir'])
    if path.isdir(config['log_directory']) == False:
        makedirs(config['log_directory'])

    return config

if __name__ == '__main__':
    backup_database()