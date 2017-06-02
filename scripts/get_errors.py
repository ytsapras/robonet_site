# Function to update the errors.txt file

from datetime import datetime
import re
import config_parser
from shutil import move
from os import remove, close
import socket

# Get hostname and set paths
host_name = socket.gethostname()
if 'cursa' in host_name:
    log_path = '/work/Tux8/ytsapras/Data/RoboNet/Logs/2017'
else:
    config = config_parser.read_config("/var/www/robonetsite/configs/obscontrol_config.xml")
    log_path = config['log_directory']

# process_name can be one of the following:
# 'artemis_subscriber', 'obs_control_rome', 'obs_control_rea', 'run_rea_tap', 'reception'

# comments is just a string

# date_updated is in the format 2017-05-31T14:10:19

def update_err(process_name, comments, date_updated=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")):
    filepath_new = log_path+"/errors_new.txt"
    filepath_old = log_path+"/errors.txt"
    errfile_new = open(filepath_new,"a")
    errfile_old = open(filepath_old).readlines()
    for line in errfile_old:
        if (process_name in line):
	    timestr = line.split('; ')[1]
	    commentstr = line.split('; ')[2].replace('\n','')
            out1 = re.sub(timestr, date_updated, line)
	    out2 = re.sub(commentstr, comments, out1)
	    errfile_new.write(out2)
	else:
	    errfile_new.write(line)
    
    errfile_new.close()
    # Clean up
    remove(filepath_old)
    move(filepath_new, filepath_old)
