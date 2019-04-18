# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 09:26:11 2019

@author: rstreet
"""
import subprocess
from datetime import datetime

def check_for_running_code(code_name):
    """Function to check whether software is currently running"""
    
    processes = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE).communicate()[0]
    
    time_running = None
    
    for line in processes.split('\n'):
        
        if code_name in line:
            try:
                time_running = datetime.strptime(line.split()[9],"%H:%M")
            except ValueError:
                time_running = datetime.strptime(line.split()[9],"%H:%M.%f")
    
    return time_running

def check_for_multiple_instances(code_name):
    """Function to check to see if multiple instances of the same code are 
    running"""
    
    processes = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE).communicate()[0]
    
    instances = []
    
    for line in processes.split('\n'):
        
        if code_name in line:
            
            instances.append(line)
    
    if len(instances) > 1:
        return True
    else:
        return False
        