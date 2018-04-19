# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 15:30:36 2018

@author: rstreet
"""

import os
import sys
cwd = os.getcwd()
sys.path.append(os.path.join(cwd,'..'))
from local_conf import get_conf
robonet_site = get_conf('robonet_site')
sys.path.append(robonet_site)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'robonet_site.settings')
from django.core import management
from django.conf import settings
from django.utils import timezone
from django import setup
from datetime import datetime, timedelta
setup()

from events.models import ObsRequest

import lco_api_tools
import config_parser
import pytz

from bokeh.plotting import figure, show, output_file, gridplot,vplot
from bokeh.models import ColumnDataSource, HoverTool, LinearColorMapper, Legend,CheckboxGroup
from bokeh.models import FixedTicker,PrintfTickFormatter
from bokeh.embed import components
from bokeh.resources import CDN

def analyze_requested_vs_observed(monitor_period_days=5.0):
    """Function to analyze the observations requested within a given period, 
    checked whether or not observations were actually obtained, 
    and generating diagnostic plots.
    
    Inputs:
        :param float monitor_period_days: Window used to search for 
                                          current observations.
                                          Window = now - monitor_period_days:
                                                  now + monitor_period_days
    """
    
    config = config_parser.read_config_for_code('setup')
    
    (start_date, end_date) = get_monitor_period(monitor_period_days)
    
    active_obs = get_status_active_obs_subrequests(config['token'],
                                                   start_date,end_date,
                                                   )
    
    plot_req_vs_obs(active_obs)
    
def plot_req_vs_obs(active_obs):
    """Function to generate a graphical representation of the currently-active
    ObsRequests and their subrequests, and indicate which ones have been 
    observed."""
    
    output_file("test_plot.html")
    
    fig = figure(plot_width=800, plot_height=300, 
                 title="Requested vs Observed",
                 x_axis_label='Time',
                 x_axis_type="datetime")

    instruments = get_instrument_list(active_obs)
    
    colours = [ 'navy', 'magenta', 'pink', 'yellow', 'orange', 'green']
    yoff = 1.0
    
    for c,camera in enumerate(instruments):
        
        xdata = []
        ydata = []
        alphas = []
        
        for grp_id,entry in active_obs.items():
            
            if entry['obsrequest'].which_inst == camera:
                
                for i in range(0,len(entry['sr_windows']),1):
                    
                    xdata.append(entry['sr_windows'][i][0])
                    ydata.append(yoff)
                    
                    if entry['sr_states'][i] == 'COMPLETED':
                        alphas.append(1.0)
                    else:
                        alphas.append(0.2)
        
        yoff += 1.0
        
        fig.circle(xdata, ydata, size=10, color=colours[c], 
                   alpha=alphas, legend=camera)
    
    show(fig)

def get_instrument_list(active_obs):
    """Function to extract a list of instruments used from a list of 
    active observations"""
    
    instruments = []
    
    for grp_id,entry in active_obs.items():
        
        if entry['obsrequest'].which_inst not in instruments:
            
            instruments.append(entry['obsrequest'].which_inst)
    
    return instruments

def get_monitor_period(monitor_period_days):
    """Function to return the start and end datetimes for the current
    period for observation monitoring"""
    
    monitor_period_secs = monitor_period_days*24.0*60.0*60.0
    
    start_date = datetime.now() - timedelta(seconds=monitor_period_secs)
    start_date = start_date.replace(tzinfo=pytz.UTC)

    end_date = datetime.now() + timedelta(seconds=monitor_period_secs)
    end_date = end_date.replace(tzinfo=pytz.UTC)
    
    return start_date, end_date

def get_status_active_obs_subrequests(token,start_date,end_date,dbg=False):
    """Function to determine the status of all observation requests within
    a specified time period. 
    
    Inputs:
        :param datetime start_date: Start of observing period
        :param datetime end_date: End of observing period
    Outputs:
        :param dict active_obs: Dictionary of matching observations of format:
            { obs.grp_id : {'obsrequest': ObsRequest object, 
                            'subrequest_states': states of ObsRequest cadence subrequests,
                            'completed_ts': timestamps of subrequest completion, or None}
    """
    
    print('Querying LCO for observation status...')
    
    qs = ObsRequest.objects.all().exclude(request_status = 'CN').\
            filter(timestamp__lte=end_date).filter(time_expire__gt=start_date)
    
    active_obs = {}
    
    for obs in qs:
        
        if dbg:
            print(obs.grp_id+' '+obs.track_id+' '+\
                obs.timestamp.strftime("%Y-%m-%dT%H:%M:%S")+' - '+\
                obs.time_expire.strftime("%Y-%m-%dT%H:%M:%S"))
                
        (states, completed_ts, windows) = lco_api_tools.get_subrequests_status(token,obs.track_id)
        
        if dbg:
            for i in range(0,len(states),1):
                try:
                    print '-> '+states[i], completed_ts[i].strftime("%Y-%m-%dT%H:%M:%S")
                except AttributeError:
                    print '-> '+states[i], repr(completed_ts[i])
        
        active_obs[obs.grp_id] = {'obsrequest': obs, 
                                  'sr_states': states,
                                  'sr_completed_ts': completed_ts,
                                  'sr_windows': windows}
    return active_obs
    
if __name__ == '__main__':
    
    analyze_requested_vs_observed(monitor_period_days=1.0)
    