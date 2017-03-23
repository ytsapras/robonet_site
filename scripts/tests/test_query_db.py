# -*- coding: utf-8 -*-
"""
Created on Sun Mar 19 12:23:44 2017

@author: rstreet
"""


from os import getcwd, path, remove
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'..'))
import query_db


def test_get_active_obs():
    
    qs = query_db.get_active_obs()
    
    assert len(qs) > 0
    if len(qs) > 0:
        assert hasattr(qs[0],'field') and hasattr(qs[0],'request_type')

def test_get_rea_targets():
    
    qs = query_db.get_rea_targets()
    
    assert len(qs) > 0
    if len(qs) > 0:
        assert hasattr(qs[0],'field') and hasattr(qs[0],'request_type')