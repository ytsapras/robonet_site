from django.shortcuts import render
from .models import Operator, Telescope, Instrument, Filter, Event, EventName, SingleModel, BinaryModel, RobonetReduction, RobonetRequest, RobonetStatus, DataFile, Tap, Image
from itertools import chain
from django.http import HttpResponse, Http404
from astropy.time import Time
from datetime import datetime
from django.shortcuts import render
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import components
import sys
sys.path.append('/home/Tux/ytsapras/robonet_site/scripts/')
from plotter import *

# Path to ARTEMiS files
artemis = "/work/Tux8/ytsapras/Data/RoboNet/ARTEMiS/"
# Color & site definitions for plotting
colors = artemis+"colours.sig.cfg"
colordef = artemis+"colourdef.sig.cfg"
# Set up and populate dictionaries
col_dict = {}
site_dict = {}
with open(colors) as f:
    for line in f:
       elem = line.split()
       key = elem[0]
       tel_id = " ".join([e.replace('"','') for e in elem[3:]])
       vals = [elem[1], elem[2], tel_id]
       site_dict[key] = vals

with open(colordef) as f:
    for line in f:
       elem = line.split()
       key = elem[0]
       val = elem[1]
       col_dict[key] = val

def test(request):
   plot = figure(title='plot')
   plot.circle([1,2], [3,4])
   script, div = components(plot, CDN)
   context = {'the_script': script, 'the_div': div, 'lala': 'blah'}
   return render(request, 'events/test.html', context)
   
##############################################################################################################
def list_all(request):
   """
   Will list all events in database. 
   """
   events = Event.objects.all()
   ev_id = [k.pk for k in events]
   ra = [k.ev_ra for k in events]
   dec = [k.ev_dec for k in events]
   bright_neighbour = [k.bright_neighbour for k in events]
   names_list = []
   for i in range(len(events)):
      evnm = EventName.objects.filter(event=events[i])
      names = [k.name for k in evnm]
      names_list.append(names)
   rows = zip(ev_id, names_list, ra, dec, bright_neighbour)
   rows = sorted(rows, key=lambda row: row[1])
   #context = {'evid': ev_id, 'event_names': names_list, 'ra': ra, 'dec': dec, 'bn': bright_neighbour}
   context = {'rows': rows}
   return render(request, 'events/list_events.html', context)

##############################################################################################################
def show_event(request, event_id):
   """
   Will set up a single event page.
   """
   time_now = datetime.now()
   time_now_jd = Time(time_now).jd
   possible_status = { 
      'CH':'check',
      'AC':'active',
      'AN':'anomaly',
      'RE':'rejected',
      'EX':'expired'}
   try:
      ev_ra = Event.objects.get(pk=event_id).ev_ra
      ev_dec = Event.objects.get(pk=event_id).ev_dec
      ev_names = EventName.objects.filter(event_id=event_id)
      for name in ev_names:
         if 'OGLE' in name.name:
            ev_ogle = name.name
	 if 'MOA' in name.name:
	    ev_moa = name.name
	 if 'KMT' in name.name:
	    ev_kmt = name.name
      # Get the names for this event ID from all surveys
      # Keep just one so that we can generate the url link to /microlensing.zah.uni-heidelberg.de
      if 'ev_ogle' in locals():
         ev_name = ev_ogle
         survey_name = "OGLE"
         event_number = ev_name.split('-')[-1]
      elif 'ev_moa' in locals():
	 ev_name = ev_moa
	 survey_name = "MOA"
	 event_number = ev_name.split('-')[-1]
      elif 'ev_kmt' in locals():
	 ev_name = ev_kmt
	 survey_name = "KMT"
	 event_number = ev_name.split('-')[-1]
      #discussion =  "https://microlensing.zah.uni-heidelberg.de/index.php#filter=1&%s&all&%s" % (survey_name, event_number)
      discussion =  "https://microlensing.zah.uni-heidelberg.de/index.php?page=1&filterSurvey=%s&filterStatus=all&minMag=all&searchById=%s" % (survey_name, event_number)
      # Get list of all observations and select the one with the most recent time.
      try:
         event = Event.objects.get(id=event_id)
         single_recent = SingleModel.objects.select_related().filter(event=event).values().latest('last_updated')
	 obs_recent = DataFile.objects.select_related().filter(event=event).values().latest('last_obs')
	 status_recent = RobonetStatus.objects.select_related().filter(event=event).values().latest('timestamp')
         last_obs = obs_recent['last_obs']
	 last_obs_hjd = Time(last_obs).jd
         Tmax = single_recent['Tmax']
         e_Tmax = single_recent['e_Tmax']
         tau = single_recent['tau']
         e_tau = single_recent['e_tau']
         umin = single_recent['umin']
         e_umin = single_recent['e_umin']
         last_updated = single_recent['last_updated']
         last_updated_hjd =  Time(last_updated).jd
	 last_obs_tel = site_dict['z'][-1]
	 status = status_recent['status']
	 ogle_url = ''
	 if "OGLE" in ev_name:
	    ogle_url = 'http://ogle.astrouw.edu.pl/ogle4/ews/%s/%s.html' % (ev_name.split('-')[1], 'blg-'+ev_name.split('-')[-1])
      except:
         last_obs = "N/A"
	 last_obs_hjd = "N/A"
	 Tmax = "N/A"
	 e_Tmax = "N/A"
	 tau = "N/A"
	 e_tau = "N/A"
	 umin = "N/A"
	 e_umin = "N/A"
	 last_updated = "N/A"
 	 last_updated_hjd = "N/A"
 	 last_obs_tel = "N/A"
 	 status = 'EX'
	 ogle_url = ''
      # Convert the name to ARTEMiS format for bokeh plotting
      if 'OGLE' in ev_name:
         artemis_name = 'OB'+ev_name.split('-')[1][2:]+ev_name.split('-')[-1]
      elif 'MOA' in ev_name:
         artemis_name = 'KB'+ev_name.split('-')[1][2:]+ev_name.split('-')[-1]
      elif 'KMT' in ev_name:
         artemis_name = 'KM'+ev_name.split('-')[1][2:]+ev_name.split('-')[-1]
      else:
         artemis_name = 'UNKNOWN EVENT'
      try:
         script, div = plot_it(artemis_name)
      except:
         script, div = '', 'Detected empty or corrupt datafile in list of lightcurve files.<br>Plotting disabled.'
      context = {'event_id': event_id, 'event_name': ev_names, 
                 'ev_ra': ev_ra, 'ev_dec':ev_dec, 'discussion':discussion, 'last_obs':last_obs, 
		 'Tmax':Tmax, 'e_Tmax':e_Tmax, 'tau':tau, 'e_tau':e_tau, 'umin':umin, 
		 'e_umin':e_umin, 'last_updated':last_updated, 'last_updated_hjd':last_updated_hjd,
		 'last_obs':last_obs, 'last_obs_hjd':last_obs_hjd, 'status':possible_status[status],
		 'last_obs_tel':last_obs_tel, 'ogle_url':ogle_url, 'time_now': time_now, 
		 'time_now_jd': time_now_jd, 'the_script': script, 'the_div': div}
   except Event.DoesNotExist:
      raise Http404("Event does not exist.")
   return render(request, 'events/show_event.html', context)
