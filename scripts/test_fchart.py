# -*- coding: utf-8 -*-
"""
Created on Wed Feb 24 01:11:39 2016

@author: robouser
"""

import exofop_publisher
import event_classes
import config_parser

config = config_parser.read_config( '../configs/exofop_publish.xml' )

events = {'master_index': { } }

e = event_classes.K2C9Event()
e.ogle_name = 'OGLE-2015-BLG-2093'
e.in_footprint = True
e.during_campaign = True

events['master_index'][1] = e

e2 = event_classes.K2C9Event()
e2.moa_name = 'MOA-2016-BLG-006'
e2.survey_id = 'gb10-R-6-38787'
e2.in_footprint = True
e2.during_campaign = True

events['master_index'][2] = e2

exofop_publisher.get_finder_charts( config, events )
