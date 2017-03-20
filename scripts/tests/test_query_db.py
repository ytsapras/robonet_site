# -*- coding: utf-8 -*-
"""
Created on Sun Mar 19 12:23:44 2017

@author: rstreet
"""


import unittest
from os import getcwd, path, remove
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'..'))
import query_db


class TestQueryDB(unittest.TestCase):
    """Tests of the database query functions"""

    def test_get_active_obs(self):
        print 'Got here'
    
if __name__ == '__main__':
    unittest.main()