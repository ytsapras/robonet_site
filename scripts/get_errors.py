# Function to update the errors.txt file

from datetime import datetime
import re
import config_parser
from shutil import move
from os import remove, close, path
import socket

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
    filepath_new = path.join(config['log_directory'],'errors_new.txt')
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
    move(filepath_new, filepath_old)
