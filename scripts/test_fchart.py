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

exofop_publisher.get_finder_charts( config, events )