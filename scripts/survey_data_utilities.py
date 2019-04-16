# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 19:40:59 2016

@author: robouser
"""

from os import path
from sys import argv, exit
import utilities
from datetime import datetime, timedelta
import event_classes
import survey_classes
import pytz
import glob
import requests
from bs4 import BeautifulSoup as bs


def read_ogle_param_files( config ):
    """Function to read the listing of OGLE data"""
    
    ts_file_path = path.join( config['ogle_data_local_location'], \
                            config['ogle_time_stamp_file'] )
    par_file_path = path.join( config['ogle_data_local_location'], \
                            config['ogle_lenses_file']+'.*' )
    lens_file_list = glob.glob( par_file_path )
    updated_file_path = path.join( config['ogle_data_local_location'], \
                            config['ogle_updated_file'] )
    ogle_data = survey_classes.SurveyData()
                            
    # Parse the timestamp in the last.changed file. The timestamp is given in yyyymmdd.daydecimal format:
    ogle_data.last_changed = time_stamp_file( ts_file_path, "%Y%m%dTD" )
    ogle_data.last_changed = ogle_data.last_changed.replace(tzinfo=pytz.UTC)
    
    # Parse the lenses parameter file.
    # First 2 lines are header, so skipped:
    ogle_data.lenses = {}
    for par_file in lens_file_list:
        file_lines = open( par_file, 'r' ).readlines()
        for line in file_lines[2:]:
            (event_id, field, star, ra, dec, t0_hjd, t0_utc, tE, u0, A0, \
            dmag, fbl, I_bl, I0) = line.split()
            if 'OGLE' not in event_id: event_id = 'OGLE-'+event_id
            event = event_classes.Lens()
            event.set_par('name',event_id)
            event.set_par('survey_id',field)
            event.set_par('ra',ra)
            event.set_par('dec',dec)
            event.set_par('t0',t0_hjd)
            event.set_par('te',tE)
            event.set_par('u0',u0)
            event.set_par('a0',A0)
            event.set_par('i0',I0)
            event.origin = 'OGLE'
            ogle_data.lenses[event_id] = event
                
    ogle_data.last_updated = read_update_file( updated_file_path )
    
    return ogle_data

def read_moa_param_files( config ):
    """Function to read the listing of MOA events"""
    
    ts_file_path = path.join( config['moa_data_local_location'], \
                            config['moa_time_stamp_file'] )
    par_file_path = path.join( config['moa_data_local_location'], \
                            config['moa_lenses_file'] )
    updated_file_path = path.join( config['moa_data_local_location'], \
                            config['moa_updated_file'] )
    moa_data = survey_classes.SurveyData()
 
    # Parse the timestamp in the last.changed file:
    moa_data.last_changed = time_stamp_file( ts_file_path, "%Y-%m-%dT%H:%M:%S" )
    moa_data.last_changed = moa_data.last_changed.replace(tzinfo=pytz.UTC)
    
    # Parse the moa_lenses parameter file:
    file_lines = open( par_file_path, 'r' ).readlines()
    moa_data.lenses = {}
    for line in file_lines:
        if line.lstrip()[0:1] != '#': 
            (event_id, field, ra, dec, t0_hjd, tE, u0, A0, I0, c) = line.split()
            try:
                ra_deg = float(ra)
                dec_deg = float(dec)
                (ra_str, dec_str) = utilities.decdeg2sex(ra_deg,dec_deg)
            except ValueError:
                ra_str = ra
                dec_str = dec
            event = event_classes.Lens()
            event.set_par('name',event_id)
            event.set_par('survey_id',field)
            event.set_par('ra',ra_str)
            event.set_par('dec',dec_str)
            event.set_par('t0',t0_hjd)
            event.set_par('te',tE)
            event.set_par('u0',u0)
            event.set_par('a0',A0)
            event.set_par('i0',I0)
            event.set_par('classification',c)
            event.origin = 'MOA'
            moa_data.lenses[event_id] = event
    
    moa_data.last_updated = read_update_file( updated_file_path )
    
    return moa_data
    
def time_stamp_file( ts_file_path, format_string ):
    """Function to parse an ASCII file containig a single time stamp on line 1.
    format_string should indicate the expected structure of the timestamp in 
    the usual datetime notation, with the date and time separated by T.
    If the time is in decimal days, the format string should be ...TD
    Returns a datetime object
    """
    
    ts = None
    ( date_format, time_format ) = format_string.split('T')
    
    if path.isfile( ts_file_path ) == None:
        return ts
        
    t = open( ts_file_path, 'r' ).readline()
    t = t.replace('\n','').lstrip()
    
    if time_format == 'D':
        ts = datetime.strptime( t.split('.')[0], date_format )
        ts = ts.replace(tzinfo=pytz.UTC)
        dt = timedelta(days=float('0.'+t.split('.')[-1]))
        ts = ts + dt

    else:
        ts = datetime.strptime( t, format_string )
        ts = ts.replace(tzinfo=pytz.UTC)
    
    return ts

def write_update_file( file_path ):
    """Function to write a timestamp file containing the timestamp at which
    the data for a given survey was last downloaded"""
    
    fileobj = open( file_path, 'w' )
    ts = datetime.utcnow()
    ts = ts.replace(tzinfo=pytz.UTC)
    fileobj.write( ts.strftime("%Y-%m-%dT%H:%M:%S") + ' UTC\n' )
    fileobj.close()
    
    return ts
    
def read_update_file( file_path ):
    """Function to read the timestamp of when a survey's data was last
    downloaded"""
    
    if path.isfile( file_path ) == True:
        fileobj = open( file_path, 'r' )
        line = fileobj.readline()
        fileobj.close()
        ts = datetime.strptime( line.split()[0], "%Y-%m-%dT%H:%M:%S" )
        ts = ts.replace(tzinfo=pytz.UTC)
    else:
        ts = None
        
    return ts

def scrape_rtmodel(year, event):
    """Function to scape data on a specific event from RTmodel, if any is available.
    
    Original code by Y. Tsapras
    """
    
    root_url = 'http://www.fisica.unisa.it/GravitationAstrophysics/RTModel/'
    
    event = str(event)
    rtmodel_html = path.join(root_url,str(year),event+'.htm')
    page = requests.get(rtmodel_html)
    if page.status_code == 200:
        soup = bs(page.content,'html.parser')
        # Extract the bits with the event name and classification
        try:
            text1 = soup.find_all('div')[1].get_text().replace('\r\n\t\t','')
            text2 = soup.find_all('div')[2].get_text().replace('\r\n\t\t','')
            # Extract the best model image link
            text3 = path.join(root_url,str(year),soup.find_all('div')[4].find_all('a')[1]['href'])
        except IndexError:
            text1 = ''
            text2 = ''
            text3 = ''
            
        # Check that the event name matches
        if event in text1:
            rtmodel = True
            classif = text2
            image_link = text3
            page_response = True
        else:
            rtmodel = False
            classif = 'N/A'
            image_link = 'N/A'
            page_response = True
    else:
        rtmodel = False
        classif = 'N/A'
        image_link = 'N/A'
        page_response = False
    return (rtmodel_html, classif, image_link, page_response, rtmodel)

# Look if there is a MiSMap model for these events
def scrape_mismap(year, event):
    """Function to scape data on a specific event from MiSMAP, if any is available.
    
    Original code by Y. Tsapras
    """
    
    root_url = 'http://www.iap.fr/miiriads/MiSMap/Events/'
    
    event = str(event)
    mismap_html = path.join(root_url, event+'.html')
    page = requests.get(mismap_html)
    if page.status_code == 200:
        soup = bs(page.content,'html.parser')
        # Extract the bits with the event name
        try:
            text1 = soup.find_all('div')[5].find_all('option')[1]['value'].split('/')[-1].split('_')[0]
        except IndexError:
            text1 = ''
        # Extract the search map image link
        text2 = path.join(root_url, event+'.png')
        # Check that the event name matches
        if event in text1:
            mismap = True
            image_link = text2
            page_response = True
        else:
            mismap = False
            image_link = 'N/A'
            page_response = True
    else:
        mismap = False
        image_link = 'N/A'
        page_response = False
    return (mismap_html, image_link, page_response, mismap)
    
# Look if there is a MOA model for these events
def scrape_moa(year, event):
    """Function to scape data on a specific event from MOA, if any is available.
    
    Original code by Y. Tsapras
    """
    
    root_url = 'http://iral2.ess.sci.osaka-u.ac.jp/~moa/anomaly/'
    
    event = str(event)
    moa_html = 'N/A'
    moa = False
    image_link = 'N/A'
    page_response = False
    # Reformat name
    event_reformatted = 'OGLE-'+str(year)+'-BLG-'+event[4:]  
    page_html = path.join(root_url,str(year),'index.html')
    try:
        page = requests.get(page_html)
        lines = page.content.splitlines()[19:-5]
        # Find if the event is in the list
        for oneline in lines:
            if event_reformatted in str(oneline):
                event_moa = str(oneline).split('<td>')[-1].split('="')[1].split('.html')[0]
                moa = True
                moa_html = path.join(root_url,str(year),event_moa+'.html')
                image_link = path.join(root_url,str(year),event_moa+'.jpg')
                page_response = True
                break
    except IOError:
        moa = False
        moa_html = 'N/A'
        image_link = 'N/A'
        page_response = False

    return (moa_html, image_link, page_response, moa)

# Look if there are KMTNet data for these events
def scrape_kmt(year, event):
    """Function to scape data on a specific event from KMTNet, if any is available.
    
    Original code by Y. Tsapras
    """
    
    root_url = 'http://kmtnet.kasi.re.kr/ulens/event/'
    
    event = str(event)
    kmt_html = path.join(root_url,str(year))
    
    page = requests.get(kmt_html)
    if page.status_code == 200:
        soup = bs(page.content,'html.parser')
        # Extract the table rows
        rows = soup.find_all('tr')
        # Look for the event
        for row in rows:
            text1 = row.find_all('td')[-1].get_text().strip()
            kmtname = row.find_all('td')[0].get_text().strip()
            # Check that the event name matches
            if event in text1:
                kmtnet = True
                kmt_link = path.join(root_url,str(year),'view.php?event='+kmtname)
                page_response = True
                break
            else:
                kmtnet = False
                kmt_link = 'N/A'
                page_response = True
    else:
        kmtnet = False
        kmt_link = 'N/A'
        page_response = False
    return (kmt_html, kmt_link, page_response, kmtnet)

# Get OGLE finder chart
def fetch_ogle_fchart(year, event):
    """Function to fetch the finder chart from the OGLE website, if any
    
    Original code by Y. Tsapras
    """
    
    root_url = 'http://ogle.astrouw.edu.pl/ogle4/ews/'
    
    ogle_id = event.replace(event[0:4],'blg-')
    finder_url = path.join(root_url,'data',str(year),ogle_id,'fchart.jpg')
    page = requests.get(finder_url)
    if page.status_code == 200:
        ogle_finder = True
    else:
        ogle_finder = False
    return (finder_url, ogle_finder)
