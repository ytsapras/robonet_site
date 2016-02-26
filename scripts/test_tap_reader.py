# -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 22:13:46 2016

@author: robouser
"""

import exofop_publisher
import config_parser

def test_tap_reader():
    
    config = config_parser.read_config( '../configs/exofop_publish.xml' )

    tap_data = exofop_publisher.load_tap_output( config )
    
    for event_name, entry in tap_data.items():
        if event_name == 'OGLE-2016-BLG-0036':
            print ':',event_name,':', entry

if __name__ == '__main__':
    test_tap_reader()