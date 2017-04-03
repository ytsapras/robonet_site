# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 10:11:29 2017

@author: rstreet
"""

from os import getcwd, environ, path
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'../'))

from local_conf import get_conf

if __name__ == '__main__':
    robonet_site = get_conf('robonet_site')
    print robonet_site
    