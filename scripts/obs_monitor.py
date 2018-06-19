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
import math
import query_db

from bokeh.plotting import figure, show, output_file, gridplot,vplot
from bokeh.models import ColumnDataSource, HoverTool, LinearColorMapper, Legend,CheckboxGroup
from bokeh.models import FixedTicker,PrintfTickFormatter, ColumnDataSource, DatetimeTickFormatter
from bokeh.models import DEFAULT_DATETIME_FORMATS
from bokeh.models import BoxSelectTool
from bokeh.embed import components
from bokeh.resources import CDN

def analyze_requested_vs_observed(monitor_period_days=2.5,dbg=False):
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
    
    obs_list = fetch_obs_list(start_date, end_date)
    
    if len(obs_list) > 0:
    
        active_obs = fetch_subrequest_status(obs_list)
    
        (script, div) = plot_req_vs_obs(active_obs,dbg=dbg)
        
    else:
        
        script = ''
        div = '<br><h4>No observations in the DB within the period '+\
                start_date.strftime("%Y-%m-%d")+' to '+end_date.strftime("%Y-%m-%d")
                
    return script, div, start_date, end_date

def analyze_percentage_completed(start_date=None, end_date=None, dbg=False):
    """Function to analyze the number of subobsrequests which are completed
    as a percentage of the total submitted, broken down by date and instrument"""
    
    (start_date, end_date) = get_completion_date_period(start_date=start_date,
                                                        end_date=end_date)
    
    obs_list = fetch_obs_list(start_date, end_date, status='ALL')
    
    if len(obs_list) > 0:
    
        active_obs = fetch_subrequest_status(obs_list)

        (script, div) = plot_percent_complete(active_obs,dbg=dbg)
        
    else:
        
        script = ''
        div = '<br><h4>No observations in the DB within the period '+\
                start_date.strftime("%Y-%m-%d")+' to '+end_date.strftime("%Y-%m-%d")
                
    return script, div, start_date, end_date

def fetch_obs_list(start_date, end_date, status='AC'):
    """Function to query the DB for a list of observations within the dates
    given, and return it in the form of an observation list"""
    
    criteria = {'timestamp': start_date,
                'time_expire': end_date}
    
    if status != 'ALL':
        criteria['request_status'] = status
    
    obs_list = query_db.select_obs_by_date(criteria)

    return obs_list

def fetch_subrequest_status(obs_list):
    """Function to query the DB for the current status of all subrequests
    of the list of observations given"""
    
    active_obs = {}
    
    for obs in obs_list:
        
        qs = query_db.get_subrequests_for_obsrequest(obs.grp_id)
        
        active_obs[obs.grp_id] = { 'obsrequest': obs,
                                    'subrequests': qs }
    
    return active_obs

def calc_percent_complete(active_obs,camera,date_range):
    """Function to calculate the percentage completion, binned per day, 
    for a given instrument"""
    
    camera_subrequests = []
    sr_ids = []
    
    for grp_id, obs_dict in active_obs.items():
        
        if obs_dict['obsrequest'].which_inst == camera:
            
            for sr in obs_dict['subrequests']:
                
                if sr.sr_id not in sr_ids:
                    sr_ids.append(sr.sr_id)
                    camera_subrequests.append(sr)
    
    tstart = date_range[0]
    dt = timedelta(days=1.0)
    tend = tstart + dt
    
    xdata = []
    ydata = []
    
    while tend < date_range[1]:
        
        nreq = 0.0
        ncomp = 0.0
        
        for sr in camera_subrequests:
            
            if sr.window_start >= tstart and sr.window_end <= tend:
                
                nreq += 1.0
                
                if sr.status == 'COMPLETED':
                    
                    ncomp += 1.0
        
        xdata.append( (tstart + ((tend-tstart)/2)) )
        
        if ncomp > 0.0:
            ydata.append( (ncomp/nreq)*100.0 )
        else:
            ydata.append( 0.0 )
    
        tstart = tstart + dt
        tend = tstart + dt
    
    return xdata, ydata
    
def plot_percent_complete(active_obs, dbg=False):
    """Function to generate a graph showing the percentage of subobsrequest
    completed as a function of time for the different cameras used for 
    observations."""
    
    instruments = get_instrument_list(active_obs)
    
    date_range = get_date_range(active_obs)    
    deltax = date_range[1] - date_range[0]

    camera_colors = {'fl12': ['#12c0ce', '#98cace'], # Turquoise
                     'fl06': ['#134dd6', '#a5b0cc'], # Blue
                     'fl15': ['#7119c4', '#b09bc4'], # Magenta
                     'fl03': ['#cc8616', '#cec0a9'], # Orange
                     'fl16': ['#4c722a', '#667559'], # Army green
                     'fl11': ['#137c6d', '#54706c'], # Teal
                     'fl14': ['#d8d511', '#e2e2a7']} # Yellow
        
    if dbg:
        output_file("test_plot.html")
    
    title = 'Subrequests available between '+date_range[0].strftime("%Y-%m-%dT%H:%M:%S")+' to '+\
                                        date_range[1].strftime("%Y-%m-%dT%H:%M:%S")
                                        
    fig = figure(plot_width=600, plot_height=400, 
                 title=title,
                 x_axis_label='Time [UTC]',
                 x_axis_type="datetime",
                 y_axis_label='Percentage completed')
    
    for camera in instruments:
        
        (xdata, ydata) = calc_percent_complete(active_obs,camera,date_range)

        fig.scatter(xdata, ydata, color=camera_colors[camera][0])
        fig.line(xdata, ydata, color=camera_colors[camera][0], line_width=2, 
                 legend=camera)

    fig.xaxis.formatter = DatetimeTickFormatter(days=["%Y-%m-%d %H:%M"])
    
    fig.xaxis.major_label_orientation = math.pi/4
    
    if dbg:
        show(fig)
        return None, None
        
    else:
        (script, div) = components(fig)
        
        return script, div
        
def plot_req_vs_obs(active_obs, dbg=False):
    """Function to generate a graphical representation of the currently-active
    ObsRequests and their subrequests, and indicate which ones have been 
    observed."""

    fields = get_fields_list(active_obs)
    
    fields_sorted = fields.keys()
    fields_sorted.sort(reverse=True)
    
    date_range = get_date_range(active_obs)
    deltax = date_range[1] - date_range[0]
    
    camera_colors = {'fl12': ['#12c0ce', '#98cace'], # Turquoise
                     'fl06': ['#134dd6', '#a5b0cc'], # Blue
                     'fl15': ['#7119c4', '#b09bc4'], # Magenta
                     'fl03': ['#cc8616', '#cec0a9'], # Orange
                     'fl16': ['#4c722a', '#667559'], # Army green
                     'fl11': ['#137c6d', '#54706c'], # Teal
                     'fl14': ['#d8d511', '#e2e2a7']} # Yellow
    
    if dbg:
        output_file("test_plot.html")
    
    title = 'Subrequests available between '+date_range[0].strftime("%Y-%m-%dT%H:%M:%S")+' to '+\
                                        date_range[1].strftime("%Y-%m-%dT%H:%M:%S")
                                        
    fig = figure(plot_width=600, plot_height=400, 
                 title=title,
                 x_axis_label='Time [UTC]',
                 x_axis_type="datetime",
                 y_range=fields_sorted)
                     
    for f,field_id in enumerate(fields_sorted):
        
        xdata = []
        ydata = []
        widths = []
        alphas = []
        colours = []
        line_colours = []
        
        obs_list = fields[field_id]
        
        for entry in obs_list:
            
            camera = entry['obsrequest'].which_inst

            for sr in entry['subrequests']:
                                
                mid_time = sr.window_start + (sr.window_end-sr.window_start)/2
                sr_length = sr.window_end - sr.window_start
                
                xdata.append(mid_time)
                widths.append(sr_length)
                ydata.append(field_id)
                
                if sr.status == 'COMPLETED':
                    alphas.append(1.0)
                    colours.append(camera_colors[camera][0])
                    line_colours.append(camera_colors[camera][0])
                else:
                    alphas.append(0.6)
                    colours.append(camera_colors[camera][1])
                    line_colours.append('black')
        
        source = ColumnDataSource(data={
                                'xdata':xdata,
                                'ydata':ydata,
                                'fill_colours':colours,
                                'line_colours':line_colours,
                                'alphas':alphas,
                                'widths':widths,
                                'heights':[0.6]*len(xdata)})
                
        fig.rect('xdata', 'ydata', width='widths', height='heights', source=source, 
                    fill_color='fill_colours', line_color='line_colours',
                     alpha='alphas')

    fig.xaxis.formatter = DatetimeTickFormatter(days=["%Y-%m-%d %H:%M"])
    
    fig.xaxis.major_label_orientation = math.pi/4
    
    if dbg:
        show(fig)
        return None, None
        
    else:
        (script, div) = components(fig)
        
        return script, div
    
def get_fields_list(active_obs):
    """Function to extract a list of the fields from a list of 
    active observations"""
    
    fields = {}
    
    for grp_id,entry in active_obs.items():
                
        if entry['obsrequest'].field not in fields.keys():
            
            fields[str(entry['obsrequest'].field)] = [ entry ]
        
        else:
            
            fields[str(entry['obsrequest'].field)].append( entry )
            
    return fields

def get_instrument_list(active_obs):
    """Function to extract a list of instruments used from a list of 
    active observations"""
    
    instruments = []
    
    for grp_id,entry in active_obs.items():
        
        if entry['obsrequest'].which_inst not in instruments:
            
            instruments.append(entry['obsrequest'].which_inst)
    
    return instruments

def get_date_range(active_obs):
    """Function to calculate the range of dates spanned by a set of 
    active observations"""
    
    start_date = datetime.now() + timedelta(days=365.0)
    start_date = start_date.replace(tzinfo=pytz.UTC)
    end_date = datetime.now() - timedelta(days=365.0)
    end_date = end_date.replace(tzinfo=pytz.UTC)
    
    for grp_id, obs_dict in active_obs.items():
        
        for sr in obs_dict['subrequests']:
            
            if sr.window_start < start_date:
                
                start_date = sr.window_start
                
            if sr.window_end > end_date:
                
                end_date = sr.window_end
    
    start_date = start_date - timedelta(days=1.0)
    end_date = end_date + timedelta(days=1.0)
    
    return (start_date, end_date)
    
def get_monitor_period(monitor_period_days):
    """Function to return the start and end datetimes for the current
    period for observation monitoring"""
    
    monitor_period_secs = monitor_period_days*24.0*60.0*60.0
    
    start_date = datetime.now() - timedelta(seconds=monitor_period_secs)
    start_date = start_date.replace(tzinfo=pytz.UTC)

    end_date = datetime.now() + timedelta(seconds=monitor_period_secs)
    end_date = end_date.replace(tzinfo=pytz.UTC)
    
    return start_date, end_date

def get_completion_date_period(start_date=None,end_date=None):
    """Function to return an appropriate range of dates for which to calculate
    the percentage completion of observation requests."""
    
    
    year = datetime.utcnow().strftime("%Y")
    if start_date == None:
                
        start_date = datetime.strptime(year+'-01-01T00:00:00',"%Y-%m-%dT%H:%M:%S")
    
    if end_date == None:
        
        end_date = datetime.utcnow()
    
    start_date = start_date.replace(tzinfo=pytz.UTC)
    end_date = end_date.replace(tzinfo=pytz.UTC)
    
    return start_date, end_date
    
if __name__ == '__main__':
    
    (script, div, start_date, end_date) = analyze_requested_vs_observed(monitor_period_days=5.0,dbg=True)
    