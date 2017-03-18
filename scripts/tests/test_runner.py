# -*- coding: utf-8 -*-
"""
Created on Sat Mar 18 16:03:04 2017

@author: rstreet
"""

import unittest

def run_all_tests():
    """Function to run all unittests"""

    loader = unittest.TestLoader()
    start_dir = '.'
    suite = loader.discover(start_dir, 'test_*.py')
    
    runner = unittest.TextTestRunner()
    runner.run(suite)
    
if __name__ == '__main__':
    run_all_tests()