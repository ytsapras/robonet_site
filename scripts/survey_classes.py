# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 14:40:47 2016

@author: rstreet
"""

##################################################
# CLASS DEFINITIONS
class SurveyData:
    """Class describing a data downloaded from a survey"""

    def __init__(self):
        self.survey = None
        self.last_changed = None
        self.last_updated = None
        self.lenses = {}
    
    def update_lenses_db(self,log=None):
        for lname,lens in self.lenses.items():
            lens.sync_event_with_DB(self.last_changed,log=log)
            