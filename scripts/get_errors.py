# Function to update the errors.txt file

from datetime import datetime
import re
import config_parser
from shutil import move
from os import remove, close, path
import socket
import uuid

# Get hostname and set paths
# RAS: This section moved into a function call because it cannot work in the
# container environment
#host_name = socket.gethostname()
#if 'cursa' in host_name:
#    log_path = '/work/Tux8/ytsapras/Data/RoboNet/Logs/2017'
#else:
#    config = config_parser.read_config("/var/www/robonetsite/configs/obscontrol_config.xml")
#    log_path = config['log_directory']

# process_name can be one of the following:
# 'artemis_subscriber', 'obs_control_rome', 'obs_control_rea', 'run_rea_tap', 'reception'

# comments is just a string

# date_updated is in the format 2017-05-31T14:10:19
class Error:
    def __init__(self):
        self.codename = None
        self.ts = None
        self.status = None
    
    def summary(self):
        return self.codename+' '+self.ts+' '+self.status
    
def read_err():
    """Function to the errors file and return a dictionary of the contents
    in the format:
    Output:
        errors = { code_name: [datetime, status] }
    """
    errors = []
    config = config_parser.read_config_for_code('obs_control')
    errfile = path.join(config['log_directory'],'errors.txt')
    if path.isfile(errfile) == True:
        file_lines = open(errfile,'r').readlines()
        for line in file_lines:
            entries = line.replace('\n','').split(';')
            if len(entries) == 3:
                e = Error()
                e.codename = entries[0]
                e.ts = entries[1]
                e.status = entries[2]
                errors.append(e)
    return errors

def update_err(process_name, comments, date_updated=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")):
    """Function to add to a central file containing current errors within the 
    system
        process_name can be one of the following:
            'artemis_subscriber', 'obs_control_rome', 'obs_control_rea', 
            'run_rea_tap', 'reception', 'backup'
        comments is a string
        date_updated is in the format 2017-05-31T14:10:19
    """
    config = config_parser.read_config_for_code('obs_control')
    tempfile = str(uuid.uuid4())+'.txt'
    filepath_new = path.join(config['log_directory'],tempfile)
    filepath_old = path.join(config['log_directory'],'errors.txt')
    errfile_new = open(filepath_new,"a")
    if path.isfile(filepath_old) == True:
        errfile_old = open(filepath_old).readlines()
    else:
        errfile_old= []
    replaced = False
    for line in errfile_old:
        if (process_name in line):
            timestr = line.split('; ')[1]
            commentstr = line.split('; ')[2].replace('\n','')
            out1 = re.sub(timestr, date_updated, line)
            out2 = re.sub(commentstr, comments, out1)
            errfile_new.write(out2)
            replaced = True
        else:
            errfile_new.write(line)
    if replaced == False:
        out1 = process_name+'; '+date_updated+'; '+comments+'\n'
        errfile_new.write(out1)
        
    errfile_new.close()
    # Clean up
    if path.isfile(filepath_old) == True:
        remove(filepath_old)
    if path.isfile(filepath_new) == True:
        move(filepath_new, filepath_old)
