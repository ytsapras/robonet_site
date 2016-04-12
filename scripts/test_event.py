# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 19:47:05 2016

@author: robouser
"""

import event_classes
import utilities

event = event_classes.K2C9Event()
event.ogle_name = 'OGLE-2016-BLG-0001'
event.ogle_alert = '2016-05-02T12:00:51'
(ra,dec) = utilities.sex2decdeg('17:23:24.5','-27:12:23.4')
event.ogle_ra = ra
event.ogle_dec = dec
position = ( event.ogle_ra, event.ogle_dec )
event.ogle_alert_hjd = utilities.ts_to_hjd( event.ogle_alert, position )
event.moa_name = 'MOA-2015-BLG-200'
event.moa_alert = '2016-05-01T16:50:51'
event.moa_ra = ra
event.moa_dec = dec
position = ( event.moa_ra, event.moa_dec )
event.moa_alert_hjd = utilities.ts_to_hjd( event.moa_alert, position )

event.set_official_name()
print event.official_name
