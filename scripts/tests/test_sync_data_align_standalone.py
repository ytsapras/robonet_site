# -*- coding: utf-8 -*-
"""
Created on Fri Aug 11 17:54:04 2017

@author: rstreet
"""
from os import getcwd, path, remove, environ
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'..'))
import artemis_subscriber
import log_utilities
import api_tools

def test_sync_data_align_files_with_db():
    """Test function for the sync of the contents of the align files 
    with the DB"""
    
    config = artemis_subscriber.read_config()
    
    log = log_utilities.start_day_log( config, 'test_artemis_subscriber' )

    client = api_tools.connect_to_db(config,testing=config['testing'],
                                             verbose=config['verbose'])
    
    #align_file = '../../data/OB170570.align'
    #data_file = '../../data/OOB170570I.dat'
    
    #sync_data_align_files_with_db(client,config,data_file,align_file,log)
    
    log_utilities.end_day_log( log )

def sync_data_align_files_with_db(client,config,data_file,align_file,log):
    """Function to ensure the DB record of the latest data is up to date"""
    log.info('GOT HERE')
    short_name = path.basename(data_file).split('.')[0][1:-1]
    filt = path.basename(data_file).split('.')[0][-1:]
    origin = path.basename(data_file).split('.')[0][0:1]
    tel = look_up_origin(origin)
    ndata = mapcount_file_lines(data_file)
    if ndata > 0:
        try:
            (first, last) = read_first_and_last(data_file)
            last_mag = round(float(last.split()[0]),2)
            last_hjd = float(last.split()[2])
            if last_hjd < 2450000.0:
                last_hjd = last_hjd + 2450000.0
        except IndexError:
            last_mag = 0.0
            last_hjd = 0.0
    else:
        last_mag = 0.0
        last_hjd = 0.0
    last_upd = datetime.fromtimestamp(path.getmtime(data_file))
    last_upd = last_upd.replace(tzinfo=pytz.UTC)
    align_pars = read_artemis_align_params(align_file,filt)
    log.info(repr(align_pars))
    params = {'name': utilities.short_to_long_name(short_name)}
    
    event_pk = int(api_tools.contact_db(client,config,params,
                                            'query_eventname',
                                            testing=config['testing']))
    log.info('event_pk = '+str(event_pk))

if __name__ == '__main__':
    test_sync_data_align_files_with_db()
    