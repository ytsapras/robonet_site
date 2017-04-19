# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 12:04:44 2017

@author: rstreet
"""

from os import getcwd, path, remove, environ
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'..'))
import artemis_subscriber
import log_utilities
import glob
from datetime import datetime
import survey_data_utilities
import event_classes

def test_read_ogle_param_files():
    """Function to test whether the OGLE parameter files can be parsed
    properly
    """
    
    # Note that OGLE lenses.par files are searched for using a glob call
    # which resolves the year suffices so that need not be given here
    config = {
            'ogle_data_local_location': '../../data/',
            'ogle_time_stamp_file': 'ogle.last.changed',
            'ogle_lenses_file': 'lenses.par',
            'ogle_updated_file': 'ogle.last.updated',
            }
    ogle_data = survey_data_utilities.read_ogle_param_files(config)
    
    last_changed = datetime(2016, 11, 2, 1, 4, 39, 360000)
    assert ogle_data.last_changed == last_changed
    
    last_updated = datetime(2017, 1, 23, 22, 30, 16)
    assert ogle_data.last_updated == last_updated
    
    assert len(ogle_data.lenses) == 1927

    lens = event_classes.Lens()
    assert type(ogle_data.lenses['OGLE-2016-BLG-0110']) == type(lens)

def test_read_moa_param_files():
    """Function to test whether the MOA parameter files can be parsed
    properly
    """
    
    config = {
            'moa_data_local_location': '../../data/',
            'moa_time_stamp_file': 'moa.last.changed',
            'moa_lenses_file': 'moa_lenses.par',
            'moa_updated_file': 'moa.last.updated',
            }
    
    moa_data = survey_data_utilities.read_moa_param_files(config)

    last_changed = datetime(2016, 11, 4, 4, 0, 35)
    assert moa_data.last_changed == last_changed
    
    last_updated = datetime(2017, 1, 23, 22, 30, 19)
    assert moa_data.last_updated == last_updated
    
    assert len(moa_data.lenses) == 618

    lens = event_classes.Lens()
