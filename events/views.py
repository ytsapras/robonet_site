from django.shortcuts import render
from .models import Operator, Telescope, Instrument, Filter, Event, EventName, SingleModel, BinaryModel, RobonetReduction, RobonetRequest, RobonetStatus, DataFile, Tap, Image
from itertools import chain
from django.http import HttpResponse, Http404
from astropy.time import Time

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

##############################################################################################################
def list_all(request):
   """
   Will list all events in database. 
   """
   event_names = Event.objects.filter(ev_name_ogle__contains="OGLE") | Event.objects.filter(ev_name_moa__contains="MOA") |  Event.objects.filter(ev_name_kmt__contains="KMT")    
   ordered_ogle = Event.objects.filter(ev_name_ogle__contains="OGLE").order_by('ev_name_ogle')
   ordered_moa = Event.objects.filter(ev_name_moa__contains="MOA", ev_name_ogle__contains="...", ev_name_kmt__contains="...").order_by('ev_name_moa')
   ordered_kmt = Event.objects.filter(ev_name_kmt__contains="KMT", ev_name_ogle__contains="...", ev_name_moa__contains="...").order_by('ev_name_kmt')
   ordered_all = list(chain(ordered_ogle, ordered_moa, ordered_kmt))
   context = {'event_names': ordered_all}
   return render(request, 'events/list_events.html', context)

##############################################################################################################
def show_event(request, event_id):
   """
   Will set up a single event page.
   """
   possible_status = { 
      'CH':'check',
      'AC':'active',
      'AN':'anomaly',
      'RE':'rejected',
      'EX':'expired'}
   try:
      event_name =  Event.objects.get(pk=event_id)
      ev_ra = event_name.ev_ra
      ev_dec = event_name.ev_dec
      ev_ogle = event_name.ev_name_ogle
      ev_moa = event_name.ev_name_moa
      ev_kmt = event_name.ev_name_kmt
      # Get the names for this event ID from all surveys
      # Keep just one so that we can generate the url link to /microlensing.zah.uni-heidelberg.de
      if ev_ogle != "...":
         ev_name = event_name.ev_name_ogle
         survey_name = "OGLE"
         event_number = ev_name.split('-')[-1]
      elif ev_moa != "...":
	 ev_name = "MOA"
	 event_number = ev_name.split('-')[-1]
      elif ev_kmt != "...":
	 ev_name = "KMT"
	 event_number = ev_name.split('-')[-1]
      discussion =  "https://microlensing.zah.uni-heidelberg.de/index.php#filter=1&%s&all&%s" % (survey_name, event_number)
      # Get list of all observations and select the one with the most recent time.
      try:
         single_recent = Single_Model.objects.select_related().filter(event=event_name).values().latest('last_updated')
	 obs_recent = Data_File.objects.select_related().filter(event=event_name).values().latest('last_updated')
	 status_recent = Robonet_Status.objects.select_related().filter(event=event_name).values().latest('timestamp')
         last_obs = obs_recent['last_updated']
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
	 ogle_url, moa_url, kmt_url = '','',''
	 if "OGLE" in ev_name:
	    ogle_url = Ogle_Detail.objects.filter(event=event_name).values('url_link').latest('last_updated')['url_link']
	 if "MOA" in ev_name:
 	    moa_url = Moa_Detail.objects.filter(event=event_name).values('url_link').latest('last_updated')['url_link']
	 if "KMT" in ev_name:
	    kmt_url = Kmt_Detail.objects.filter(event=event_name).values('url_link').latest('last_updated')['url_link']
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
	 moa_url = ''
	 kmt_url = ''
      context = {'event_name': event_name, 'ev_ogle':ev_ogle, 'ev_moa':ev_moa, 'ev_kmt':ev_kmt, 
                 'ev_ra': ev_ra, 'ev_dec':ev_dec, 'discussion':discussion, 'last_obs':last_obs, 
		 'Tmax':Tmax, 'e_Tmax':e_Tmax, 'tau':tau, 'e_tau':e_tau, 'umin':umin, 
		 'e_umin':e_umin, 'last_updated':last_updated, 'last_updated_hjd':last_updated_hjd,
		 'last_obs':last_obs, 'last_obs_hjd':last_obs_hjd, 'status':possible_status[status],
		 'last_obs_tel':last_obs_tel, 'ogle_url':ogle_url, 'moa_url':ogle_url, 'kmt_url':kmt_url}
   except Event.DoesNotExist:
      raise Http404("Event does not exist")
   return render(request, 'events/show_event.html', context)
