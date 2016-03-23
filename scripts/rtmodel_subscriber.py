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

def rtmodel_subscriber(log=None, renamed=None):
    """Function to download the parameters of events modeled by RTModel"""
    
    # Read configuration:
    config_file_path = path.join(path.expanduser('~'),
                                 '.robonet_site', 'rtmodel_sync.xml')
    config = config_parser.read_config(config_file_path)
    
    if log == None:
        use_given_log = True
        log = log_utilities.start_day_log( config, __name__ )
        log.info('Started sync with RTmodel server')
    else:
        use_given_log = False
        
    # Scrape the list of events which have been modeled from the 
    # top level site:
    events_list = get_events_list( config, log )
    
    # Loop over all events, harvest the parameters of the best fit
    # for each one:
    rtmodels = {}
    for event_id in events_list:
        model = get_event_params( config, event_id, log )
        if renamed != None and model.event_name in renamed.keys():
            model.event_name = renamed[model.event_name]
            log.info('-> Switched name of event renamed by ARTEMiS to '+\
                             model.event_name)
        rtmodels[model.event_name] = model
        log.info( model.summary() )
        
    # Tidy up and finish:
    if use_given_log == False:
        log_utilities.end_day_log( log )
    
    return rtmodels    
    
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
    model for a given event. 
    The summary page for each event may list one or more models, of which
    we assume the top model has the lowest chisq, i.e. the current best fit, 
    and scrape the relevant parameters, which may include a subset of the
    full parameter set
    """
    
    url = path.join( str(config['root_url']), str(config['year']), \
                        event_id + '.htm' )
    (page_data,msg) = utilities.get_http_page(url,parse=False)
    
    model = event_classes.RTModel()
    model.event_name = utilities.short_to_long_name(event_id)
    model.url = url
    
    # Identify the top model, and extract the first line which contains the
    # parameters.  Separate them from the HTML and set the model parameters.
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
    
    params = {'s':'<br>s=', \
                'q':'q', \
                'u0': 'u<sub>0</sub>', \
                'theta': '&theta;', \
                'rho': '&rho;<sub>*</sub>', \
                'tE': 't<sub>E</sub>', \
                't0': 't<sub>0</sub>',\
                'pi_perp': '&pi;<sub>&perp;</sub>',\
                'pi_para': '&pi;<sub>||</sub>'
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
            
            if key == 't0':
                value = 2450000.0 + value
            
            setattr(model,key, value)
            setattr(model,'sig_'+key, sigma)
            
        except ValueError:
            pass
      
    return model
    
if __name__ == '__main__':
    rtmodels = rtmodel_subscriber()
    
    for event_id, model in rtmodels.items():
        print model.summary()
        