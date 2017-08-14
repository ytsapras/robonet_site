# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 17:41:27 2017

@author: rstreet
"""

from os import getcwd, path, remove, environ
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'..'))
import event_classes
import artemis_subscriber
import log_utilities
from datetime import datetime
import api_tools
import pytz

e = event_classes.Lens()
e.name = 'OGLE-2017-BLG-1516'
e.survey_id = 'field 1'
e.ra = '17:26:49.06'
e.dec = '-29:33:60.0'
e.t0 = 2457000.0
e.te = 30.0
e.u0 = 0.1
e.a0 = 10.0
e.i0 = 20.0
e.origin = 'OGLE'
e.modeler = 'ARTEMiS'
e.last_updated = datetime.utcnow()
e.last_updated = e.last_updated.replace(tzinfo=pytz.UTC)

event_pk = 2016
field_id = 'Outside ROMEREA footprint'
operator_id = 'OGLE'
eventname_pk = 2289

config = {'db_user_id': 'rstreet', 'db_pswd': 'skynet1186'}
client = api_tools.connect_to_db(config,testing=True,verbose=True)

def test_check_event_in_DB():
    
    config = artemis_subscriber.read_config()

    log = log_utilities.start_day_log( config, 'test_artemis_subscriber' )
    
    debug = True
    testing = True

    e.check_event_in_DB(client,config,log=log,debug=debug,testing=testing)
    
    assert e.event_pk == event_pk
    
    log_utilities.end_day_log( log )

def test_get_field():
    
    config = artemis_subscriber.read_config()

    log = log_utilities.start_day_log( config, 'test_artemis_subscriber' )
    
    debug = True
    testing = True

    e.get_field(client,config,log=log,debug=debug,testing=testing)
    
    assert e.field_id == field_id
    
    log_utilities.end_day_log( log )

def test_get_operator():
    
    config = artemis_subscriber.read_config()

    log = log_utilities.start_day_log( config, 'test_artemis_subscriber' )
    
    debug = True
    testing = True

    e.get_operator(client,config,log=log,debug=debug,testing=testing)
    
    assert e.operator_id == operator_id
    
    log_utilities.end_day_log( log )

def test_add_event_to_DB():
    """Function to test the addition of a new event to the DB. """
    
    config = artemis_subscriber.read_config()

    log = log_utilities.start_day_log( config, 'test_artemis_subscriber' )
    
    debug = True
    testing = True
    
    e.add_event_to_DB(client,config,log=log,debug=debug,testing=testing)

    assert e.event_pk == event_pk
    
    log_utilities.end_day_log( log )

def test_check_event_name_in_DB():
    
    config = artemis_subscriber.read_config()

    log = log_utilities.start_day_log( config, 'test_artemis_subscriber' )
    
    debug = True
    testing = True

    e.check_event_name_in_DB(client,config,log=log,debug=debug,testing=testing)
    
    assert e.eventname_pk == eventname_pk
    
    log_utilities.end_day_log( log )

def test_check_event_name_assoc_event():
    
    config = artemis_subscriber.read_config()

    log = log_utilities.start_day_log( config, 'test_artemis_subscriber' )
    
    debug = True
    testing = True

    e.check_event_name_assoc_event(client,config,log=log,debug=debug,testing=testing)
    
    assert e.got_eventname == True
    
    log_utilities.end_day_log( log )

def test_check_last_singlemodel():
    
    config = artemis_subscriber.read_config()

    log = log_utilities.start_day_log( config, 'test_artemis_subscriber' )
    
    debug = True
    testing = True

    e.check_last_singlemodel(client,config,log=log,debug=debug,testing=testing)
    
    assert e.singlemodel_pk != -1
    
    log_utilities.end_day_log( log )

def test_add_singlemodel_to_DB():
    
    config = artemis_subscriber.read_config()

    log = log_utilities.start_day_log( config, 'test_artemis_subscriber' )
    
    debug = True
    testing = True

    e.add_singlemodel_to_DB(client,config,log=log,debug=debug,testing=testing)
    
    assert e.singlemodel_pk != -1
    
    log_utilities.end_day_log( log )

def test_sync_event_with_DB():
    
    config = artemis_subscriber.read_config()

    log = log_utilities.start_day_log( config, 'test_artemis_subscriber' )
    
    debug = True
    testing = True

    e.sync_event_with_DB(client,config,log=log,debug=debug,testing=testing)
    
    assert e.event_pk == event_pk
    assert e.field_id == field_id
    assert e.operator_id == operator_id
    assert e.eventname_pk == eventname_pk
    assert e.got_eventname == True
    assert e.singlemodel_pk != -1
    
    log_utilities.end_day_log( log )

if __name__ == '__main__':
    test_check_event_in_DB()
    test_get_field()
    test_get_operator()
    test_add_event_to_DB()
    test_check_event_name_in_DB()
    test_check_event_name_assoc_event()
    test_check_last_singlemodel()
    test_add_singlemodel_to_DB()
    test_sync_event_with_DB()
    