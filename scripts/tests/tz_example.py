# -*- coding: utf-8 -*-
"""
Created on Sat Apr  1 15:02:01 2017

@author: rstreet
"""

from datetime import datetime
import pytz
d = datetime(2017,4,1,12,00,tzinfo=pytz.UTC)
d2 = datetime.utcnow()
d2 = d2.replace(tzinfo=pytz.UTC)