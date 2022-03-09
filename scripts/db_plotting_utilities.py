# -*- coding: utf-8 -*-
"""
Created on Thu Sep  7 12:17:08 2017

@author: rstreet
"""

import os
import sys
from . import local_conf
robonet_site = local_conf.get_conf('robonet_site')
sys.path.append(robonet_site)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'robonet_site.settings')
from django.core import management
from django.conf import settings
from django.utils import timezone
from django import setup
from datetime import datetime, timedelta
setup()

from . import query_db
import matplotlib.pyplot as plt
from . import config_parser
import socket

def read_config():
    """Function to read the configuration for the plotting functions"""

    host_name = socket.gethostname()
    if 'rachel' in str(host_name).lower():
        config_file_path = os.path.join('/Users/rstreet/.robonet_site/media_config.xml')
    else:
        config_file_path = '/var/www/robonetsite/configs/media_config.xml'
    if os.path.isfile(config_file_path) == False:
        raise IOError('Cannot find configuration file, looking for:'+config_file_path)
    config = config_parser.read_config(config_file_path)

    return config

def plot_image_rejection_statistics():
    """Function to plot a piechart of the reasons why images have been
    rejected"""

    config = read_config()
    plot_path = os.path.join(config['media_directory'],'image_rejection_stats.png')

    image_stats = query_db.get_image_rejection_statistics()

    keys = image_stats.keys()
    keys.sort()
    image_totals = []
    legend_text = []
    for k in keys:
        if 'total' not in str(k).lower():
            image_totals.append(image_stats[k])
            legend_text.append(k+' '+str(image_stats[k]))

    fig = plt.figure(1, figsize=(7.0,7.0))
    plt.pie(image_totals, radius=1.0,autopct='%1.f%%', shadow=False)
    plt.title('Percentages of images accepted vs. rejected\nTotal number of images: '+\
            str(image_stats['Total number of images']))
    plt.legend(tuple(legend_text), bbox_to_anchor=(1,0.5), loc=(0,-0.05))
    plt.savefig(plot_path, bbox_inches="tight")
    plt.close(1)

    return os.path.basename(plot_path)

if __name__ == '__main__':
    plot_image_rejection_statistics()
