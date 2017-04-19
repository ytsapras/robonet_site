# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 16:56:05 2017

@author: rstreet
"""

from os import getcwd, path, remove, environ, makedirs, stat
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'..'))
import artemis_subscriber
import log_utilities
import glob
from datetime import datetime, timedelta
import survey_subscriber
import event_classes

def test_ogle_download():
    """Function to test that the download of data on events discovered from the
    OGLE server works as expected"""
    
    config = {'log_directory': '.',
              'log_root_name': 'test_ogle_download',
              'ogle_ftp_server': 'ftp.astrouw.edu.pl',
              'ogle_data_local_location': './surveys/OGLE',
              'ogle_time_stamp_file': 'last.changed',
              'ogle_lenses_file': 'lenses.par',
              'subscribe_ogle': 1,
              'version': 'test',
              'update_db': 0,
              'years': '2017',
            }
    if path.isdir(config['ogle_data_local_location']) == False:
        makedirs(config['ogle_data_local_location'])
        
    log = survey_subscriber.init_log(config)
    survey_subscriber.get_ogle_parameters(config, log)
    
    file_list = glob.glob(path.join(config['ogle_data_local_location'],'*'))
    
    f = path.join(config['ogle_data_local_location'],'last.changed')
    assert f in file_list
    
    mtime = datetime.fromtimestamp(path.getmtime(f))
    tlimit = datetime.utcnow() - timedelta(minutes=2.0)
    assert mtime > tlimit
    
    year = datetime.utcnow().year
    f = path.join(config['ogle_data_local_location'],'lenses.par.'+str(year))
    assert f in file_list
    
    mtime = datetime.fromtimestamp(path.getmtime(f))
    tlimit = datetime.utcnow() - timedelta(minutes=2.0)
    assert mtime > tlimit

def test_moa_download():
    """Function to test the harvesting of data from MOA.
    MOA's alert website appears to be offline, so this is currently 
    non-functional
    """
    
    config = {'log_directory': '.',
              'log_root_name': 'test_moa_download',
              'years': '2017',
              'version': 'test',
              'update_db': 0,
              'subscribe_moa': 1,
              'moa_server_root_url': 'http://www.massey.ac.nz/~iabond/moa/alert',
             }
    if int(config['subscribe_moa']) == 1:
        log = survey_subscriber.init_log(config)
        (events_index_data, alerts_page_data) = survey_subscriber.get_moa_parameters(config, log)
        assert len(events_index_data) > 0
        assert len(alerts_page_data) > 0
    else:
        events_index_data = []
        alerts_page_data = []
        assert len(events_index_data) == 0
        assert len(alerts_page_data) == 0

def parse_moa_data():
    """Function to test the parsing of the data harvested from the MOA website.
    """
    
    config = {'log_directory': '.',
              'log_root_name': 'test_moa_download',
              'years': '2017',
              'version': 'test',
              'update_db': 0,
              'subscribe_moa': 1,
              'moa_server_root_url': 'http://www.massey.ac.nz/~iabond/moa/alert',
              'moa_data_local_location': './surveys/MOA',
              'moa_time_stamp_file': 'last.changed',
              'moa_lenses_file': 'moa_lenses.par',
              'moa_updated_file': 'last.updated',
             }
    
    if path.isdir(config['moa_data_local_location']) == False:
        makedirs(config['moa_data_local_location'])

    events_index_data = [
        '2017-BLG-001 gb2-R-2-19629 268.434977871 -34.2212870236 2457782.047299 12.86 0.4000 14.49 25.7023916071 7518.94040867', 
        '2017-BLG-002 gb22-R-1-1852 278.458752339 -23.2755681594 2457699.204260 115.32 0.1765 18.66 27.6939729941 14125.0241051', 
        '2017-BLG-003 gb1-R-4-33756 266.543235238 -34.456722463 2457790.629467 24.96 0.1332 18.26 27.5295494495 18172.7134993', 
        '2017-BLG-004 gb10-R-2-69460 269.443227376 -27.1833850702 2457802.687856 86.66 0.9311 15.38 26.0642678012 5031.61172506', 
        '2017-BLG-005 gb10-R-3-28287 269.735461207 -27.6119669401 2457794.434049 46.22 0.3960 18.59 27.4085866458 0', 
        '2017-BLG-006 gb13-R-2-35653 271.394790055 -28.7593614078 2457799.861885 6.79 0.3465 15.69 26.018265486 4691.44030251', 
        '2017-BLG-007 gb14-R-5-63805 271.362554448 -28.260000663 2457794.398885 20.58 0.0958 18.35 27.8335772463 10651.9936414', 
        '2017-BLG-008 gb14-R-8-75621 271.887537868 -27.603476793 2457798.025811 44.38 0.1033 19.54 27.5796345574 15005.6158093'
                        ]
    
    alerts_page_data = [
        '', '    MOA Transient Alert Page', '    ', '    ', '    MOA Transient Alerts', '    Machine readable list of events', 
        '    MOA high magnification candidates', '    Cross referenced OGLE events:html/text file', '', '', '    ', '    ', 
        '    ID', '    RA (J2000.0)', '    Dec (J2000.0)', '    t0', '    tE(days)', '    Amax', '    Ibase', '    Assessment', 
        '2017-BLG-00117:53:44.39-34:13:16.632017-Jan-28.5512.862.6514.49microlensing', 
        '2017-BLG-00218:33:50.10-23:16:32.052016-Nov-6.70115.325.7318.66microlensing', 
        '2017-BLG-00317:46:10.38-34:27:24.202017-Feb-6.1324.967.5618.26microlensing', 
        '2017-BLG-00417:57:46.37-27:11:00.192017-Feb-18.1986.661.4015.38microlensing', 
        '2017-BLG-00517:58:56.51-27:36:43.082017-Feb-9.9346.222.6718.59microlensing', 
        '2017-BLG-00618:05:34.75-28:45:33.702017-Feb-15.366.793.0115.69microlensing', 
        '2017-BLG-00718:05:27.01-28:15:36.002017-Feb-9.9020.5810.4818.35microlensing', 
        '2017-BLG-00818:07:33.01-27:36:12.522017-Feb-13.5344.389.7219.54microlensing', 
        'This page last updated: 2017-04-19T16:26:11 UT'
                        ]
    mtime = datetime(2017, 4, 19, 16, 26, 11)
    
    if int(config['subscribe_moa']) == 1:
        log = survey_subscriber.init_log(config)
        moa_data = survey_subscriber.parse_moa_data(config,log,events_index_data, alerts_page_data)

        assert len(moa_data.lenses) == 8
        assert 'MOA-2017-BLG-0001' in moa_data.lenses.keys
        assert moa_data.last_updated == mtime

