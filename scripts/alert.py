# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 14:05:34 2017

@author: rstreet
"""

from commands import getstatusoutput
from os import path

def send_alert(message,subject,eaddress_list):
    '''Function to send an email alert'''
    
    for eaddress in eaddress_list:
        alert = 'echo "'+message+'" | mail  -s "'+subject+'" '+eaddress
        (iexec,coutput) = getstatusoutput(alert)
    
    return iexec

if __name__ == '__main__':

    message = 'ROME/REA Alert System\n\nTest message'
    subject = 'ROME/REA Alert System Test'
    eaddress_list = [ 'rstreet@lco.global' ]

    iexec = send_alert(message,subject,eaddress_list)