# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 22:32:15 2016

@author: robouser
"""

##############################################################################
#                   EMAIL HARVESTER
##############################################################################

from os import path
from sys import exit, argv
import imaplib
from email import parser
from datetime import datetime

def harvest_events_from_email(data_dir,fetch_ogle=True,fetch_moa=True,dbg=False):

    # Read back the log of known events, for speed:
    log_file = path.join(data_dir,'event_email_alerts.log')
    event_alerts = read_alert_log(log_file)
    
    # Fetch the authentication for the user's Gmail account
    auth = fetch_auth()

    # Log into the Gmail IMAP server:
    connect = imaplib.IMAP4_SSL('imap.gmail.com')
    connect.login( auth[0], auth[1] )
    connect.select('INBOX')
    
    # Fetch and parse OGLE event data:
    if fetch_ogle == True:
        iyear = 173000
        msg_index = get_msg_index(connect,'(FROM "OGLE EWS")')
        if dbg==True: print len(msg_index),' messages from OGLE'
        for i in msg_index:
            if int(i) > iyear:
                date = get_msg_date(connect,i)
                event_list = parse_ogle_msg_body(connect,i,['OGLE-','-BLG-'])
                for event in event_list:
                    event_alerts[event] = date
                    if dbg==True: print 'Message ',i,' ',date, ' ', event
        
    # Fetch and parse MOA event data:
    if fetch_moa == True:
        iyear = 172000
        msg_index = get_msg_index(connect,'(FROM "MOA transient alert")')
        if dbg==True: print len(msg_index),' messages from MOA'
        for i in msg_index:
            if int(i) > iyear:
                date = get_msg_date(connect,i)
                event_list = parse_moa_msg_body(connect,i)
                for event in event_list:
                    event_alerts[event] = date
                    if dbg==True: print 'Message ',i,' ',date, ' ', event
                    
    # Output the updated event_alerts log:
    event_log = open(log_file,'w')
    event_log.write('# Log of event alerts received\n')
    event_log.write('# Last updated: ' + \
        datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')+'\n')
    event_log.write('# Event name    Alert received [UTC]\n')
    sort_keys = event_alerts.keys()
    sort_keys.sort()
    for event in sort_keys:
        date = event_alerts[event]
        event_log.write(event + '  ' + date.strftime('%Y-%m-%dT%H:%M:%S')+'\n')
    event_log.close()
    
    # Close the connection and finish:
    connect.close()
    connect.logout()
    
    event_log.close()
    
    return event_alerts    
    
def get_msg_date(connect,imsg):
    (typ,msg_hdr) = connect.fetch(imsg,'(BODY.PEEK[HEADER])')
    date = parse_msg_hdr(msg_hdr)
    return date
    
def get_msg_index(connect,search_string):
    (typ,msg_index) = connect.search(None,search_string)
    msg_index = msg_index[0].split()
    return msg_index

def parse_msg_hdr(hdr):
    date = None
    meta_data = hdr[0][1].split('\n')
    for item in meta_data:
        if 'Date:' in item:
            date = item.replace('\r','').replace('Date: ','')
            date = convert_to_datetime(date)
    return date

def convert_to_datetime(date_string):
    
    dlist = date_string.replace(',',' ').split()
    day_name = dlist[0]
    day = dlist[1]
    month = dlist[2]
    year = dlist[3]
    time = dlist[4]
    date = ' '.join(dlist[1:4])
    
    d = datetime.strptime( date+'T'+time, "%d %b %YT%H:%M:%S" )
    
    return d

def parse_ogle_msg_body(connect,imsg,search_list):
    (typ,body) = connect.fetch(imsg,'(BODY.PEEK[TEXT])')
    event_list = []
    for line in body[0][1].split('\n'):
        got_items = True
        for item in search_list:
            if item not in line: got_items = False
        if got_items == True:
            if len(line.replace('\r','').split(' ')) == 1:
                event_list.append(line.replace('\r',''))
    return event_list

def parse_moa_msg_body(connect,imsg):
    (typ,body) = connect.fetch(imsg,'(BODY.PEEK[TEXT])')
    event_list = []
    for line in body[0][1].split('\n'):
        if 'MOA_ID:' in line: 
            event_name = 'MOA-' + line.replace('\r','').replace('MOA_ID: ','')
            event_list.append(event_name)
    return event_list

def fetch_auth():
    auth_file = path.join(path.expanduser('~'),'.robonet_site','exofop.auth')
    line = open(auth_file,'r').readline()
    (userid,password) = line.replace('\n','').split()
    return userid, password

def read_alert_log(log_file):
    event_alerts = {}
    if path.isfile(log_file) == False:
        return event_alerts
        
    event_log = open(log_file,'r')
    line_list = event_log.readlines()
    event_log.close()
    for line in line_list:
        if line[0:1] != '#':
            try:
                (event_name,datestr) = line.replace('\n','').split()
            except ValueError:
                pass
            date = datetime.strptime(datestr,"%Y-%m-%dT%H:%M:%S")
            event_alerts[event_name] = date
    return event_alerts
    
if __name__ == '__main__':
    if len(argv) == 1:
        data_dir = raw_input('Please enter output directory: ')
    else:
        data_dir = argv[1]
    event_alerts = harvest_events_from_email(data_dir,dbg=False)