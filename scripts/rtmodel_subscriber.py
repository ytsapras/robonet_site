# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 19:28:11 2016

@author: rstreet
"""

import config_parser
from os import path
from sys import exit
import log_utilities
import utilities
import event_classes

def rtmodel_subscriber():
    """Function to download the parameters of events modeled by RTModel"""
    
    # Read configuration:
    config_file_path = path.join(path.expanduser('~'),
                                 '.robonet_site', 'rtmodel_sync.xml')
    config = config_parser.read_config(config_file_path)
    
    log = log_utilities.start_day_log( config, __name__ )
    log.info('Started sync with RTmodel server')
    
    # Scrape the list of events which have been modeled from the 
    # top level site:
    events_list = get_events_list( config, log )
    
    # Loop over all events, harvest the parameters of the best fit
    # for each one:
    for event_id in events_list:
        get_event_params( config, event_id, log )
        exit()
        
    # Tidy up and finish:
    log_utilities.end_day_log( log )
    
def get_events_list( config, log ):
    """Function to scrape the list of events which have been modeled by
    the RTmodel system"""
    
    url = path.join( str(config['root_url']), str(config['year']), 'RTModel.htm' )
    events_list = []
    
    (events_index_data,msg) = utilities.get_http_page(url)
    log.info('Loaded RTmodel URL with status: ' + msg)
    
    for line in events_index_data.split('\n'):
        if 'OB' in line or 'KB' in line:
            entry = line.replace('\n','').split()[0]
            events_list.append( entry ) 
    log.info('Models available for ' + str(len(events_list)) + ' events')
    
    return events_list

def get_event_params( config, event_id, log ):
    """Function to retrieve the parameters of RTmodel's current best-fitting
    model for a given event"""
    
    url = path.join( str(config['root_url']), str(config['year']), \
                        event_id + '.htm' )
    (page_data,msg) = utilities.get_http_page(url,parse=False)
    
    model = event_classes.RTModel()
    page_lines = page_data.split('\n')
    i = 0
    while i < (len(page_lines)):
        entries = page_lines[i].split()
        if len(entries) > 0 and '>Model ' in page_lines[i] and \
                '&chi;<sup>2</sup>' in page_lines[i]:
            idx = i
            i = len(page_lines)
        i = i + 1
    
    line = page_lines[idx]
    entry = line.split('&chi;<sup>2</sup>')[1].replace('=','')
    entry = entry.split('</b>')[0]
    model.chisq = float(entry)
    
    print 'Model chisq = ',model.chisq
    
    params = {'s':'s', \
                'q':'q', \
                'u0': 'u<sub>0</sub>', \
                'theta': '&theta;', \
                'rho': '&rho;<sub>*</sub>', \
                'tE': 't<sub>E</sub>', \
                't0': 't<sub>0</sub>'
                }
    
    for key, search_term in params.items():
        try:
            i = line.index(search_term)
            istart = i + line[i:].index('=') + 1
            iend = i + line[i:].index('&plusmn;')
            par = line[i:i+len(search_term)]
            value = float(line[istart:iend])
            
            istart = iend + len('&plusmn;')
            iend = istart + line[istart:].index('&nbsp;')
            sigma = float(line[istart:iend])
            
            setattr(model,key, value)
            setattr(model,'sig_'+key, sigma)
            print 'Model set: ',key,getattr(model,key), getattr(model,'sig_'+key)
            
        except ValueError:
            pass
        
    
if __name__ == '__main__':
    rtmodel_subscriber()
    