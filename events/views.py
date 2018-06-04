from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Max
from django.utils import timezone
from django.http import HttpResponse, Http404, HttpResponseRedirect
from .forms import QueryObsRequestForm, RecordObsRequestForm, OperatorForm, TelescopeForm, EventForm, EventNameForm, SingleModelForm
from .forms import BinaryModelForm, EventReductionForm, DataFileForm, TapForm, ImageForm, RecordDataFileForm, TapLimaForm
from .forms import RecordSubObsRequestForm, QueryObsRequestDateForm
from .forms import TapStatusForm, EventAnomalyStatusForm, EventNameForm
from events.models import Field, Operator, Telescope, Instrument, Filter, Event, EventName, SingleModel, BinaryModel
from events.models import EventReduction, ObsRequest, EventStatus, DataFile, Tap, Image
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view,authentication_classes,permission_classes
from itertools import chain
from astropy.time import Time
from datetime import datetime, timedelta
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import components
import sys, os
from scripts.plotter import *
from scripts.local_conf import get_conf
from scripts.blgvis_ephem import *
from scripts.utilities import short_to_long_name
from scripts import config_parser
from scripts.get_errors import *
from scripts import update_db_2
from scripts import query_db
from scripts import db_plotting_utilities
from scripts import obs_monitor
import requests
import pytz

# Path to ARTEMiS files
artemis_col = get_conf('artemis_cols')
robonet_site = get_conf('robonet_site')
sys.path.append(robonet_site)

# Color & site definitions for plotting
colors = artemis_col+"colours.sig.cfg"
colordef = artemis_col+"colourdef.sig.cfg"

# Path to save offline plotly plots
#plotly_path = "/home/Tux/ytsapras/robonet_site/events/static/events/"

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
@login_required(login_url='/db/login/')
def change_password(request):
   """
   Will allow a user to change their password.
   """
   if request.user.is_authenticated():
      try:
         if request.method == 'POST':
 	    form = PasswordChangeForm(request.user, request.POST)
 	    if form.is_valid():
 	       user = form.save()
 	       update_session_auth_hash(request, user)  # Important!
 	       messages.success(request, 'Your password was successfully updated!')
 	       return HttpResponseRedirect('/db')
 	    else:
 	       messages.error(request, 'Please correct the error below.')
 	 else:
 	    form = PasswordChangeForm(request.user)
 	 return render(request, 'events/change_password.html', {'form': form})
      except:
         raise Http404("Encountered a problem while rendering page.")  
   else:
      return HttpResponseRedirect('login')

##############################################################################################################
@login_required(login_url='/db/login/')
def test(request):
   ########### ONLY FOR TESTING ################
   plot = figure(title='plot')
   plot.circle([1,2], [3,4])
   script, div = components(plot, CDN)
   context = {'the_script': script, 'the_div': div, 'lala': 'blah'}
   return render(request, 'events/test.html', context)

##############################################################################################################
@login_required(login_url='/db/login/')
def simple(request):
   ########### ONLY FOR TESTING ################
   tels = [u'LCOGT CTIO 1m A', u'LCOGT CTIO 1m B', u'LCOGT CTIO 1m C', u'LCOGT SAAO 1m A', 
           u'LCOGT SAAO 1m B', u'LCOGT SAAO 1m C', u'LCOGT SSO 1m B']
   cols =['#38FFB8', '#33285D', '#C04B31', '#DE96BC', '#C340AE', '#BD6D6F', '#151BE8']
   num_obs = [21, 13, 15, 13, 16, 3, 0]
   ndata = 30
   event_id = 33
   from pylab import figure, rcParams, title, legend, savefig, close, axes, pie, get_current_fig_manager
   from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
   import os
   fig = figure(figsize=[10, 10])
   ax = fig.add_subplot(111)  
   rcParams['axes.titlesize'] = 10.0
   rcParams['xtick.labelsize'] = 14.0
   rcParams['legend.fontsize'] = 22.0
   rcParams['font.size'] = 22.0
   colors=cols
   fracs=num_obs
   patches = ax.pie(fracs, colors=cols, labels=tels, labeldistance=0.95, explode=None, autopct='%1.f%%', shadow=False)
   for pie_wedge in patches[0]:
      pie_wedge.set_edgecolor('white')
   
   title = "Observations: "+str(ndata)
   legend([k[0]+': '+str(k[1]) for k in zip(tels, num_obs)],loc=(-.12,-.12), framealpha=0.4)
   # Store image in a string buffer
   #buffer_1 = StringIO.StringIO()
   #canvas = get_current_fig_manager().canvas
   #canvas.draw()
   #pilImage = Image.fromstring("RGB", canvas.get_width_height(), canvas.tostring_rgb())
   #pilImage.save(buffer_1, "PNG")
   canvas = FigureCanvas(fig)
   response = HttpResponse(content_type='image/png')
   canvas.print_png(response)
   #response = HttpResponse(buffer_1.getvalue(), content_type="image/png")
   return response

##############################################################################################################
def dashboard(request):
    """
    Will display the database front view (dashboard).
    """
    if request.user.is_authenticated():
        try:
            config2 = config_parser.read_config_for_code('setup')
            api_token = config2['token']
            # Retrieve time usage information
            response = requests.get(
                'https://observe.lco.global/api/proposals/?id=KEY2017AB-004',
                headers={'Authorization': 'Token {}'.format(api_token)}
                )
            # Make sure this api call was successful
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as exc:
                print('Request failed: {}'.format(response.content))
                raise exc
            # Report the time allocation only for the 1m network
            proposals_dict = response.json()  # api returns a json dictionary containing proposal information
            for alloc in proposals_dict['results'][0]['timeallocation_set']:
                if ( (alloc['telescope_class'] == u'1m0') and (alloc['semester'] == '2018A') ):
                        time_available = alloc['std_allocation']
                        time_used = alloc['std_time_used']
                        ipp_time_available = alloc['ipp_time_available']
                        ipp_limit = alloc['ipp_limit']
        except:
            raise Http404("Encountered a problem while trying to access the LCO observe api. Please contact the site administrator.")
        errors = read_err()
        try:
            # Get telescope status information
            response3 = requests.get(
                'https://observe.lco.global/api/telescope_states/',
                headers={'Authorization': 'Token {}'.format(api_token)}
                )
            # Make sure this api call was successful
            try:
                response3.raise_for_status()
            except requests.exceptions.HTTPError as exc:
                print('Request failed: {}'.format(response3.content))
                raise exc
            telstate_dict = response3.json()
            try:
                coj_doma = telstate_dict['coj.doma.1m0a'][0]['event_type']
            except:
                coj_doma = 'Unknown'
            try:
                coj_domb = telstate_dict['coj.domb.1m0a'][0]['event_type']
            except:
                coj_domb = 'Unknown'
            try:
                cpt_doma = telstate_dict['cpt.doma.1m0a'][0]['event_type']
            except:
                cpt_doma = 'Unknown'
            try:
                cpt_domb = telstate_dict['cpt.domb.1m0a'][0]['event_type']
            except:
                cpt_domb = 'Unknown'
            try:
                cpt_domc = telstate_dict['cpt.domc.1m0a'][0]['event_type']
            except:
                cpt_domc = 'Unknown'
            try:
                lsc_doma = telstate_dict['lsc.doma.1m0a'][0]['event_type']
            except:
                lsc_doma = 'Unknown'
            try:
                lsc_domb = telstate_dict['lsc.domb.1m0a'][0]['event_type']
            except:
                lsc_domb = 'Unknown'
            try:
                lsc_domc = telstate_dict['lsc.domc.1m0a'][0]['event_type']
            except:
                lsc_domc = 'Unknown'
        except:
            raise Http404("Encountered a problem while trying to access the LCO observe api to read the telescope states. Please contact the site administrator.")
        # Get current time (UTC now)
        status_time = datetime.now()
        date_today = str(status_time.year)+str(status_time.month).zfill(2)+str(status_time.day).zfill(2)
        status_time_jd = Time(status_time).jd
        context = {'status_time':status_time, 'status_time_jd':status_time_jd, 
                   'date_today':date_today, 'errors': errors,
		   'coj_doma':coj_doma, 'coj_domb':coj_domb,
		   'cpt_doma':cpt_doma, 'cpt_domb':cpt_domb, 'cpt_domc':cpt_domc,
		   'lsc_doma':lsc_doma, 'lsc_domb':lsc_domb, 'lsc_domc':lsc_domc,
		   'time_used':str.format('{0:.1f}', time_used),'time_available':str.format('{0:.1f}', time_available),
		   'ipp_limit':str.format('{0:.1f}', ipp_limit),'ipp_time_available':str.format('{0:.1f}', ipp_time_available)
                    }
        return render(request, 'events/dashboard.html', context)
    else:
        return HttpResponseRedirect('login')
      
##############################################################################################################
@login_required(login_url='/db/login/')
def download_lc_by_id(request, event_id):
   """
   Will serve a tar file of the ARTEMiS lightcurves for this event for download.
   """
   def tar_lc(lightcurves):
      import tarfile
      import os
      filename = settings.MEDIA_ROOT+str(event_id)+".tgz"
      if (os.path.exists(filename) ):
         os.remove(filename)
      # Serve lightcurves at tgz
      tar = tarfile.open(filename,"w:gz")
      for lc in lightcurves:
         # Ignore directory paths when tarring the files
         tar.addfile(tarfile.TarInfo(lc.split('/')[-1]), file(lc))
      tar.close()
      return filename

   if request.user.is_authenticated():
      event = Event.objects.get(id=event_id)
      lightcurves = []
      lightcurves_dictionary = DataFile.objects.select_related().filter(event=event).values('datafile')
      for i in lightcurves_dictionary:
         lightcurves.append(i['datafile'])
      try:
         filename = tar_lc(lightcurves)
      except:
         raise Http404("Encountered a problem while generating the tar file.") 
      try:
         download = open(filename,'rb')
      except:
         raise Http404("Encountered a problem while reading the tar file.") 
      try:
         response = HttpResponse(download.read(),content_type='application/x-tar')
         response['Content-Disposition'] = 'attachment; filename="%s"' % filename.split('/')[-1]
      except:
         raise Http404("Encountered a problem while generating the HttpResponse.")  
      return response
   else:
      return HttpResponseRedirect('login')
      
##############################################################################################################
@login_required(login_url='/db/login/')
def download_lc(request, event_name):
   """
   Will serve a tar file of the ARTEMiS lightcurves for this event for download.
   """
   if request.user.is_authenticated():
      # Convert shorthand format to long format to make compatible with the DB
      event_name = short_to_long_name(event_name)
      # Get the ID for this event
      event_id = EventName.objects.get(name=event_name).event_id
      def tar_lc(lightcurves):
         import tarfile
         import os
         filename = settings.MEDIA_ROOT+str(event_name)+".tgz"
         if (os.path.exists(filename) ):
            os.remove(filename)
         # Serve lightcurves at tgz
         tar = tarfile.open(filename,"w:gz")
         for lc in lightcurves:
            # Ignore directory paths when tarring the files
            tar.addfile(tarfile.TarInfo(lc.split('/')[-1]), file(lc))
         tar.close()
         return filename
      event = Event.objects.get(id=event_id)
      lightcurves = []
      lightcurves_dictionary = DataFile.objects.select_related().filter(event=event).values('datafile')
      for i in lightcurves_dictionary:
         lightcurves.append(i['datafile'])
      try:
         filename = tar_lc(lightcurves)
      except:
         raise Http404("Encountered a problem while generating the tar file.") 
      try:
         download = open(filename,'rb')
      except:
         raise Http404("Encountered a problem while reading the tar file.") 
      try:
         response = HttpResponse(download.read(),content_type='application/x-tar')
         response['Content-Disposition'] = 'attachment; filename="%s"' % filename.split('/')[-1]
      except:
         raise Http404("Encountered a problem while generating the HttpResponse.")  
      return response
   else:
      return HttpResponseRedirect('login')

##############################################################################################################
@login_required(login_url='/db/login/')
def obs_log(request, date):
   from django.utils import timezone
   """
   Will display the observation log for the given date.
   Date must be provided in the format: YYYYMMDD
   """
   if request.user.is_authenticated():
      try:
         date_min = datetime(int(date[0:4]), int(date[4:6]), int(date[6:8]))
	 date_min = timezone.make_aware(date_min, timezone.get_current_timezone())
         date_max = date_min + timedelta(hours=24)
      except:
         raise Http404("Encountered an error: Date must be provided in the format: YYYYMMDD")
      try:
         images = Image.objects.filter(date_obs__range=(date_min, date_max))
         filenames = [k.image_name for k in images]
         times = [k.date_obs for k in images]
         fields = [k.field_id for k in images]
         ras = [k.field.field_ra for k in images]
         decs = [k.field.field_dec for k in images]
         filts = [k.filt for k in images]
         tels = [k.tel for k in images]
         insts = [k.inst for k in images]
         grp_ids = [k.grp_id for k in images]
         track_ids = [k.track_id for k in images]
         req_ids = [k.req_id for k in images]
         airmasses = [k.airmass for k in images]
         avg_fwhms = [k.avg_fwhm for k in images]
         avg_skys = [k.avg_sky for k in images]
         avg_sigskys = [k.avg_sigsky for k in images]
         moon_seps = [k.moon_sep for k in images]
         elongations = [k.elongation for k in images]
         nstars = [k.nstars for k in images]
         qualitys = [k.quality for k in images]
         rows = zip(filenames, times, fields, ras, decs, filts, tels, insts, grp_ids, track_ids,
        	    req_ids, airmasses, avg_fwhms, avg_skys, avg_sigskys, moon_seps, elongations,
        	    nstars, qualitys)
         rows = sorted(rows, key=lambda row: row[1])
      except:
         raise Http404("Encountered a problem while loading. Please contact the site administrator.")
      context = {'rows': rows, 'date': date[0:4]+'-'+date[4:6]+'-'+date[6:8]}
      return render(request, 'events/obs_log.html', context)
   else:
      return HttpResponseRedirect('login')

##############################################################################################################
@login_required(login_url='/db/login/')
def obs_requests24(request):
   from django.utils import timezone
   """
   Will display the observation requests for the last 24 hours.
   """
   if request.user.is_authenticated():
      try:
         date_max = datetime.now()
	 date_max = timezone.make_aware(date_max, timezone.get_current_timezone())
         date_min = date_max + timedelta(hours=-24)
      except:
         raise Http404("Encountered an error: Date must be provided in the format: YYYYMMDD")
      try:
         obs_requests = ObsRequest.objects.filter(timestamp__range=(date_min, date_max))
	 field = [k.field.name for k in obs_requests]       
	 t_sample = [k.t_sample for k in obs_requests] 
	 exptime = [k.exptime for k in obs_requests]   
	 timestamp = [k.timestamp.strftime("%Y-%m-%dT%H:%M:%S") for k in obs_requests]  
	 time_expire = [k.time_expire.strftime("%Y-%m-%dT%H:%M:%S") for k in obs_requests] 
	 request_status = [k.request_status for k in obs_requests]   
	 request_type = [k.request_type for k in obs_requests]
	 which_site = [k.which_site for k in obs_requests]
	 which_inst = [k.which_inst for k in obs_requests]
	 which_filter = [k.which_filter for k in obs_requests]
	 grp_id = [k.grp_id for k in obs_requests]
	 track_id = [k.track_id for k in obs_requests]
	 req_id = [k.req_id for k in obs_requests] 
	 n_exp  = [k.n_exp for k in obs_requests]    
         rows = zip(field,t_sample,exptime,timestamp,time_expire,request_status,
	            request_type,which_site,which_inst,which_filter,grp_id,
		    track_id,req_id,n_exp)
         rows = sorted(rows, key=lambda row: row[1])
      except:
         raise Http404("Encountered a problem while loading. Please contact the site administrator.")
      context = {'rows': rows}
      return render(request, 'events/obs_requests24.html', context)
   else:
      return HttpResponseRedirect('login')

##############################################################################################################
@login_required(login_url='/db/login/')
def active_obs_requests(request):
   from django.utils import timezone
   """
   Will display all active observation requests.
   """
   if request.user.is_authenticated():
      try:
         obs_requests = ObsRequest.objects.filter(request_status='AC')
	 field_id = [k.field for k in obs_requests]
	 field = [k.name for k in field_id]
	 t_sample = [k.t_sample for k in obs_requests]
	 exptime = [k.exptime for k in obs_requests]
	 timestamp = [k.timestamp.strftime("%Y-%m-%dT%H:%M:%S") for k in obs_requests]  
	 time_expire = [k.time_expire.strftime("%Y-%m-%dT%H:%M:%S") for k in obs_requests] 
	 request_status = [k.request_status for k in obs_requests]   
	 request_type = [k.request_type for k in obs_requests]
	 which_site = [k.which_site for k in obs_requests]
	 which_inst = [k.which_inst for k in obs_requests]
	 which_filter = [k.which_filter for k in obs_requests]
	 grp_id = [k.grp_id for k in obs_requests]
	 track_id = [k.track_id for k in obs_requests]
	 req_id = [k.req_id for k in obs_requests] 
	 n_exp  = [k.n_exp for k in obs_requests]    
         rows = zip(field,t_sample,exptime,timestamp,time_expire,request_status,
	            request_type,which_site,which_inst,which_filter,grp_id,
		    track_id,req_id,n_exp)
         rows = sorted(rows, key=lambda row: row[1])
      except:
         raise Http404("Encountered a problem while loading. Please contact the site administrator.")
      context = {'rows': rows}
      return render(request, 'events/active_obs_requests.html', context)
   else:
      return HttpResponseRedirect('login')

##############################################################################################################
@login_required(login_url='/db/login/')
def tap(request):
   """
   Will load the TAP page.
   """
   if request.user.is_authenticated():
      try:
	 list_ev = Event.objects.select_related().filter(status__in=['MO']).annotate(latest_tap=Max('tap__timestamp'))
	 latest_ev_tap = Tap.objects.filter(timestamp__in=[e.latest_tap for e in list_ev])
         time_now = datetime.now()
         time_now_jd = Time(time_now).jd
         ##### TAP query goes here ###
	 selection_tap = latest_ev_tap.order_by('omega').reverse()
         #####
         ev_id = []
         timestamp = []
         check_list = []
         for f in selection_tap:
            if f.event_id not in check_list:
               ev_id.append(f.event_id)
               timestamp.append(f.timestamp)
            check_list.append(f.event_id)
         ra = []
         dec = []
         names_list = []
         cadence = []
         nexp = []
         texp = []
         priority = []
         imag = []
         tsamp = []
         omega_s = []
         sig_omega_s = []
         omega_peak = []
         colors = []
         visibility = []
	 field_names = []
         count = 0
         for i in ev_id:
            evnm = EventName.objects.filter(event=i)
            names = [k.name for k in evnm]
            ev_ra = Event.objects.all().get(pk=i).ev_ra
            ev_dec = Event.objects.all().get(pk=i).ev_dec
	    field_name = (Event.objects.get(id=i)).field.name
            sampling_time = Tap.objects.all().get(event=i, timestamp=timestamp[count]).tsamp
            time_exp = Tap.objects.all().get(event=i, timestamp=timestamp[count]).texp
            prior = Tap.objects.all().get(event=i, timestamp=timestamp[count]).priority
            if prior == 'A':
               colors.append('#FE2E2E')
            elif prior == 'H':
               colors.append('#FA8258')
            elif prior == 'M':
               colors.append('#F4FA58')
            elif prior == 'L':
               colors.append('#A9F5A9')
            else:
               colors.append('#808080')
            baseline = Tap.objects.all().get(event=i, timestamp=timestamp[count]).imag
            oms = Tap.objects.all().get(event=i, timestamp=timestamp[count]).omega
            omsp = Tap.objects.all().get(event=i, timestamp=timestamp[count]).peak_omega
            vis = Tap.objects.all().get(event=i, timestamp=timestamp[count]).visibility
            texp.append(time_exp)
            tsamp.append(sampling_time)
            priority.append(prior)
            imag.append(baseline)
            omega_s.append(oms)
            omega_peak.append(omsp)
            names_list.append(names)
            visibility.append(vis)
            ra.append(ev_ra)
            dec.append(ev_dec)
	    field_names.append(field_name)
            count = count + 1
         #### TAP rows need to be defined here ####
         rows = zip(colors, ev_id, names_list, ra, dec, texp, priority, tsamp, imag, omega_s,
        	    omega_peak, visibility, field_names)
         rowsrej = ''
         time1 = 'Unknown' # This should be an estimate of when the target list will be uploaded next (in minutes)
         #time2 = str(blg_visibility(mlsites=['CPT','COJ','LSC'])) # This should be an estimate of the bulge visibility on <nsite> sites (in hours)
         time2 = 'test' # This should be an estimate of the bulge visibility on <nsite> sites (in hours)
         nsite = '3' # The number of sites the bulge is visible from for time2 hours
         occupy = '<font color="red"> Unknown</font>' # This should be a string (can include html)
         ##########################################
      except:
         raise Http404("Encountered a problem while loading. Please contact the site administrator.")
      context = {'rows': rows, 'rowsrej':rowsrej, 'time_now': time_now, 'time_now_jd': time_now_jd,
        	 'time1':time1, 'time2':time2, 'nsite':nsite, 'occupy':occupy}
      return render(request, 'events/tap.html', context)
   else:
      return HttpResponseRedirect('login')

##############################################################################################################
@login_required(login_url='/db/login/')
def set_tap_status(request):
    """View to enable users to manually set the REA status of an event in the
    TAP list"""
    
    if request.user.is_authenticated():
        
        (tap_targets,priorities) = get_events_from_tap_list()
                
        if request.method == "POST":
        
            form = TapStatusForm(request.POST)
            
            if form.is_valid():
                
                post = form.save(commit=False)
                
                (status, message) = update_db_2.update_tap_status(post.event, 
                                                                  post.priority)
                
                return render(request, 'events/set_tap_status.html', \
                                    {'form': form, 'tap_targets': tap_targets,
                                     'priorities': priorities,
                                     'message': message})
            
            else:
                
                form = TapStatusForm()
                
                return render(request, 'events/set_tap_status.html', \
                                    {'form': form, 'tap_targets': tap_targets,\
                                     'priorities': priorities,\
                                    'message':'Form entry was invalid.  Please try again.'})
            
        else:
            form = TapStatusForm()
                
            return render(request, 'events/set_tap_status.html', \
                                    {'form': form, 'tap_targets': tap_targets,\
                                     'priorities': priorities,\
                                    'message':'OK'})
                                        
    else:
        
        return HttpResponseRedirect('login')

@login_required(login_url='/db/login/')
def set_event_status(request):
    """View to enable users to manually set the REA status of an event in the
    TAP list"""
    
    if request.user.is_authenticated():
        
        qs = Event.objects.all().order_by('year').reverse()
        
        events = []
        
        for q in qs:
        
            names = query_db.get_event_names(q.pk)
            name = query_db.combine_event_names(names)
            
            events.append( ( q, name+'(PK='+str(q.pk)+')', q.status) )
        
        events = tuple(events)
        
        states = (
                      ('NF', 'Not in footprint'),
                      ('AC', 'active'),
                      ('MO', 'monitor'),
                      ('AN', 'anomaly'),
                      ('EX', 'expired')
                   )
        
        
        if request.method == "POST":
        
            eform = EventAnomalyStatusForm(request.POST)
            nform = EventNameForm(request.POST)
                        
            if eform.is_valid() and nform.is_valid():
                
                epost = eform.save(commit=False)
                npost = nform.save(commit=False)
                
                event = Event.objects.get(pk=npost.name)
                
                (status, message) = update_db_2.update_event_status(event, 
                                                                    epost.status)
                
                return render(request, 'events/set_event_anomaly_status.html', \
                                    {'eform': eform, 'nform': nform,
                                    'events': events, 'states': states,
                                     'message': message})
            
            else:
                
                eform = EventAnomalyStatusForm()
                nform = EventNameForm()
                
                return render(request, 'events/set_event_anomaly_status.html', \
                                    {'eform': eform, 'nform': nform,
                                    'events': events, 'states': states,
                                    'message':'Form entry was invalid.  Please try again.'})
            
        else:

            eform = EventAnomalyStatusForm()
            nform = EventNameForm()
                
            return render(request, 'events/set_event_anomaly_status.html', \
                                    {'eform': eform, 'nform': nform,
                                    'events': events, 'states': states,
                                    'message':'OK'})
                                        
    else:
        
        return HttpResponseRedirect('login')

 
def get_events_from_tap_list():
    """Function to return a list of all current events"""
    
    
    priority_settings = {'A':'REA High',
                         'L':'REA Low',
                         'B':'REA Post-High',
                         'N':'None'}
    
    priorities = []
    
    for key, value in priority_settings.items():
        
        priorities.append( (key, value) )
    
    priorities = tuple(priorities)
    
    tap_list = query_db.get_tap_list()
    
    tap_targets = []
    
    for target in tap_list:
        
        tap_targets.append( (target.event, target.names+'(PK='+str(target.pk)+'): '+priority_settings[target.priority]) )
    
    return tap_targets, priorities
    
##############################################################################################################
@login_required(login_url='/db/login/')
def list_year(request, year):
   """
   Will list all events in database for a given year. 
   """
   if request.user.is_authenticated():
      events = Event.objects.filter(year=str(year))
      ev_id = [k.pk for k in events]
      field = [k.field.name.replace(' footprint','') for k in events]
      ra = [k.ev_ra for k in events]
      dec = [k.ev_dec for k in events]
      status = [k.status for k in events]
      year_disc = [k.year for k in events]
      names_list = []
      for i in range(len(events)):
         evnm = EventName.objects.filter(event=events[i])
         names = [k.name for k in evnm]
         names_list.append(names)
      rows = zip(ev_id, names_list, field, ra, dec, status, year_disc)
      rows = sorted(rows, key=lambda row: row[1])
      context = {'rows': rows}
      return render(request, 'events/list_events.html', context)
   else:
      return HttpResponseRedirect('login')

##############################################################################################################
@login_required(login_url='/db/login/')
def list_all(request):
   """
   Will list all events in database. 
   """
   if request.user.is_authenticated():
      events = Event.objects.all()
      ev_id = [k.pk for k in events]
      field = [k.field.name.replace(' footprint','') for k in events]
      ra = [k.ev_ra for k in events]
      dec = [k.ev_dec for k in events]
      status = [k.status for k in events]
      year_disc = [k.year for k in events]
      names_list = []
      for i in range(len(events)):
         evnm = EventName.objects.filter(event=events[i])
         names = [k.name for k in evnm]
         names_list.append(names)
      rows = zip(ev_id, names_list, field, ra, dec, status, year_disc)
      rows = sorted(rows, key=lambda row: row[1])
      context = {'rows': rows}
      return render(request, 'events/list_events.html', context)
   else:
      return HttpResponseRedirect('login')

##############################################################################################################
@login_required(login_url='/db/login/')
def show_event_by_id(request, event_id):
   """
   Will set up a single event page and display the lightcurve.
   """
   if request.user.is_authenticated():
      time_now = datetime.now()
      time_now_jd = Time(time_now).jd
      possible_status = { 
         'NF':'Not in footprint',
         'AC':'active',
         'MO':'monitor',
         'AN':'anomaly',
         'EX':'expired'}
      try:
         ev_ra = Event.objects.get(pk=event_id).ev_ra
         ev_dec = Event.objects.get(pk=event_id).ev_dec
         ev_names = EventName.objects.filter(event_id=event_id)
         flag = 0
         ev_ogle, ev_moa, ev_kmt = '', '', ''
         for name in ev_names:
            if 'OGLE' in name.name and flag==0:
               ev_ogle = name.name
               flag = 1
            if 'MOA' in name.name:
               ev_moa = name.name
            if 'KMT' in name.name:
               ev_kmt = name.name
         # Get the names for this event ID from all surveys
         # Keep just one so that we can generate the url link to /microlensing.zah.uni-heidelberg.de
         if 'ev_ogle':
            ev_name = ev_ogle
            survey_name = "OGLE"
            event_number = ev_name.split('-')[-1]
         elif 'ev_moa':
            ev_name = ev_moa
            survey_name = "MOA"
            event_number = ev_name.split('-')[-1]
         elif 'ev_kmt':
            ev_name = ev_kmt
            survey_name = "KMT"
            event_number = ev_name.split('-')[-1]
         field_id =  Event.objects.get(pk=event_id).field.id
         field = Field.objects.get(id=field_id).name
         # Get list of all observations and select the one with the most recent time.
         try:
            event = Event.objects.get(id=event_id)
            status_recent = Event.objects.get(pk=event_id).status	    
            single_recent = SingleModel.objects.select_related().filter(event=event).values().latest('last_updated')
            Tmax = single_recent['Tmax']
            e_Tmax = single_recent['e_Tmax']
            tau = single_recent['tau']
            e_tau = single_recent['e_tau']
            umin = single_recent['umin']
            e_umin = single_recent['e_umin']
            last_updated = single_recent['last_updated']
            last_updated_hjd =  Time(last_updated).jd
            status = status_recent
            ogle_url = ''
            if "OGLE" in ev_name:
               ogle_url = 'http://ogle.astrouw.edu.pl/ogle4/ews/%s/%s.html' % (ev_name.split('-')[1], 'blg-'+ev_name.split('-')[-1])
         except:
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
	 try:
            obs_recent = DataFile.objects.select_related().filter(event=event).values().latest('last_obs')
            last_obs = obs_recent['last_obs']
            last_obs_hjd = Time(last_obs).jd
            tel_id = obs_recent['datafile'].split('/')[-1].split('_')
            if len(tel_id) == 2:
               tel_id = tel_id[0]+'_'
            else:
               tel_id = obs_recent['datafile'].split('/')[-1][0]
            last_obs_tel = site_dict[tel_id][-1]
         except:
            last_obs = "N/A"
            last_obs_hjd = "N/A"
	    last_obs_tel = "N/A"
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
         context = {'event_id':event_id, 'event_name':ev_names,
        	    'ev_ra':ev_ra, 'ev_dec':ev_dec, 'field':field, 'last_obs':last_obs, 
        	    'Tmax':Tmax, 'e_Tmax':e_Tmax, 'tau':tau, 'e_tau':e_tau, 'umin':umin, 
        	    'e_umin':e_umin, 'last_updated':last_updated, 'last_updated_hjd':last_updated_hjd,
        	    'last_obs':last_obs, 'last_obs_hjd':last_obs_hjd, 'status':possible_status[status],
        	    'last_obs_tel':last_obs_tel, 'ogle_url':ogle_url, 'time_now': time_now, 
        	    'time_now_jd': time_now_jd, 'the_script': script, 'the_div': div}
      except Event.DoesNotExist:
         raise Http404("Event does not exist.")
      return render(request, 'events/show_event_by_id.html', context)
   else:
      return HttpResponseRedirect('login')

##############################################################################################################
@login_required(login_url='/db/login/')
def show_event(request, event_name):
   """
   Will set up a single event page and display the lightcurve.
   """
   if request.user.is_authenticated():
      time_now = datetime.now()
      time_now_jd = Time(time_now).jd
      possible_status = { 
         'NF':'Not in footprint',
         'AC':'active',
         'MO':'monitor',
         'AN':'anomaly',
         'EX':'expired'}
      try:
         # Convert shorthand format to long format to make compatible with the DB
         event_name = short_to_long_name(event_name)
         this_event_number = event_name.split('-')[-1]
         next_event_number = str(int(this_event_number)+1).zfill(4)
         prev_event_number = str(int(this_event_number)-1).zfill(4)
         next_name = event_name.replace(this_event_number, next_event_number)
         prev_name = event_name.replace(this_event_number, prev_event_number)	 
         # Get the ID for this event
         event_id = EventName.objects.get(name=event_name).event_id
         ev_ra = Event.objects.get(pk=event_id).ev_ra
         ev_dec = Event.objects.get(pk=event_id).ev_dec
         ev_names = EventName.objects.filter(event_id=event_id)
         flag = 0
         ev_ogle, ev_moa, ev_kmt = '', '', ''
         for name in ev_names:
            if 'OGLE' in name.name and flag==0:
               ev_ogle = name.name
               flag = 1
            if 'MOA' in name.name:
               ev_moa = name.name
            if 'KMT' in name.name:
               ev_kmt = name.name
         # Get the names for this event ID from all surveys
         # Keep just one so that we can generate the url link to /microlensing.zah.uni-heidelberg.de
         if 'ev_ogle':
            ev_name = ev_ogle
            survey_name = "OGLE"
            event_number = ev_name.split('-')[-1]
         elif 'ev_moa':
            ev_name = ev_moa
            survey_name = "MOA"
            event_number = ev_name.split('-')[-1]
         elif 'ev_kmt':
            ev_name = ev_kmt
            survey_name = "KMT"
            event_number = ev_name.split('-')[-1]
         field_id =  Event.objects.get(pk=event_id).field.id
         field = Field.objects.get(id=field_id).name
         # Get list of all observations and select the one with the most recent time.
         try:
            event = Event.objects.get(id=event_id)
            status_recent = Event.objects.get(pk=event_id).status	    
            single_recent = SingleModel.objects.select_related().filter(event=event).filter(modeler='ARTEMiS').values().latest('last_updated')
            Tmax = single_recent['Tmax']
            e_Tmax = single_recent['e_Tmax']
            tau = single_recent['tau']
            e_tau = single_recent['e_tau']
            umin = single_recent['umin']
            e_umin = single_recent['e_umin']
            last_updated = single_recent['last_updated']
            last_updated_hjd =  Time(last_updated).jd
            status = status_recent
            ogle_url = ''
            if "OGLE" in ev_name:
               ogle_url = 'http://ogle.astrouw.edu.pl/ogle4/ews/%s/%s.html' % (ev_name.split('-')[1], 'blg-'+ev_name.split('-')[-1])
         except:
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
	 try:
            obs_recent = DataFile.objects.select_related().filter(event=event).values().latest('last_hjd')
            last_obs_hjd = obs_recent['last_hjd']
            last_obs = Time(float(last_obs_hjd), format='jd', scale='utc').iso
            tel_id = obs_recent['datafile'].split('/')[-1].split('_')
            if len(tel_id) == 2:
               tel_id = tel_id[0]+'_'
            else:
               tel_id = obs_recent['datafile'].split('/')[-1][0]
            last_obs_tel = site_dict[tel_id][-1]
         except:
            last_obs = "N/A"
            last_obs_hjd = "N/A"
	    last_obs_tel = "N/A"
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
         context = {'event_id':event_id, 'event_names':ev_names, 
        	    'this_name':event_name, 
        	    'prev_name':prev_name, 'next_name':next_name,
        	    'ev_ra':ev_ra, 'ev_dec':ev_dec, 'field':field, 'last_obs':last_obs, 
        	    'Tmax':Tmax, 'e_Tmax':e_Tmax, 'tau':tau, 'e_tau':e_tau, 'umin':umin, 
        	    'e_umin':e_umin, 'last_updated':last_updated, 'last_updated_hjd':last_updated_hjd,
        	    'last_obs':last_obs, 'last_obs_hjd':last_obs_hjd, 'status':possible_status[status],
        	    'last_obs_tel':last_obs_tel, 'ogle_url':ogle_url, 'time_now': time_now, 
        	    'time_now_jd': time_now_jd, 'the_script': script, 'the_div': div}
      except EventName.DoesNotExist:
         raise Http404("Event does not exist in DB.")
      except ValueError:
         raise Http404("Unrecognized event name. Please provide name in standard short or long notation.")	 
      return render(request, 'events/show_event.html', context)
   else:
      return HttpResponseRedirect('login')

##############################################################################################################
@login_required(login_url='/db/login/')
def display_obs_monitor(request):
    """Display of functions which monitor the observing system, observations
    requested and data taken."""
    
    rome_start = datetime.strptime('2017-04-01','%Y-%m-%d')
    rome_start = rome_start.replace(tzinfo=pytz.UTC)
    now = datetime.utcnow()
    now = now.replace(tzinfo=pytz.UTC)
    
    if request.user.is_authenticated():
        
        (script1,div1,start_date1,end_date1) = obs_monitor.analyze_requested_vs_observed(monitor_period_days=5.0)
        (script2,div2,start_date2,end_date2) = obs_monitor.analyze_percentage_completed(start_date=rome_start,
                                                                                        end_date=now)
        if script1 == None and div1 == None:
            
            script1 = ''
            div1 = 'Timeout: response too slow'
            
        elif script1 == None and div1 != None:
            
            script1 = ''
        
        if script2 == None and div2 == None:
            
            script2 = ''
            div2 = 'Timeout: response too slow'
            
        elif script2 == None and div2 != None:
            
            script2 = ''
        
        context = {'req_vs_obs_plot_script': script1, 'req_vs_obs_plot_div': div1,
                   'completion_plot_script': script2, 'completion_plot_div': div2,
                   'req_vs_obs_start_date': start_date1.strftime('%Y-%m-%dT%H:%M:%S'), 
                   'req_vs_obs_end_date':end_date1.strftime('%Y-%m-%dT%H:%M:%S'),
                   'completion_start_date': start_date2.strftime('%Y-%m-%dT%H:%M:%S'), 
                   'completion_end_date':end_date2.strftime('%Y-%m-%dT%H:%M:%S')}

        return render(request, 'events/obs_monitor_display.html', context)
      
    else:

        return HttpResponseRedirect('login')

##############################################################################################################
@login_required(login_url='/db/login/')
def event_obs_details(request, event_name):
   """
   Will set up a single event page with current observing details.
   """
   if request.user.is_authenticated():
      # Convert shorthand format to long format to make compatible with the DB
      event_name = short_to_long_name(event_name)
      # Get the ID for this event
      event_id = EventName.objects.get(name=event_name).event_id
      # Define pie chart plotting
      # arguments are [telescopes], [colors], [number_observations], ndata, event_id
      def pie_chart(tels, cols, num_obs, ndata, event_id):
         from pylab import figure, rcParams, title, legend, savefig, close, axes, pie
         from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
         import os
         fig = figure(num=11, figsize=[10, 10])
         ax = fig.add_subplot(111)
         rcParams['axes.titlesize'] = 10.0
         rcParams['xtick.labelsize'] = 14.0
         rcParams['legend.fontsize'] = 22.0
         rcParams['font.size'] = 22.0
         colors=cols
         fracs=num_obs
         patches = ax.pie(fracs, colors=cols, labels=tels, labeldistance=0.95, explode=None, autopct='%1.f%%', shadow=False)
         for pie_wedge in patches[0]:
            pie_wedge.set_edgecolor('white')
 
         title = "Observations: "+str(ndata)
         legend([k[0]+': '+str(k[1]) for k in zip(tels, num_obs)],loc=(-.12,-.12), framealpha=0.4)
         canvas = FigureCanvas(fig)
         filename = settings.MEDIA_ROOT+str(event_id)+".png"
         if (os.path.exists(filename) ):
             os.remove(filename)
         # save the new file
         canvas.print_figure(filename)
         # close the figure
         close(11)
 
      time_now = datetime.now()
      time_now_jd = Time(time_now).jd
      possible_status = {
         'NF':'Not in footprint',
         'AC':'active',
         'MO':'monitor',
         'AN':'anomaly',
         'EX':'expired'}
      try:
         ev_ra = Event.objects.get(pk=event_id).ev_ra
         ev_dec = Event.objects.get(pk=event_id).ev_dec
         ev_names = EventName.objects.filter(event_id=event_id)
         flag = 0
         ev_ogle, ev_moa, ev_kmt = '', '', ''
         for name in ev_names:
            if 'OGLE' in name.name and flag==0:
               ev_ogle = name.name
               flag = 1
            if 'MOA' in name.name:
               ev_moa = name.name
            if 'KMT' in name.name:
               ev_kmt = name.name
         # Get the names for this event ID from all surveys
         # Keep just one so that we can generate the url link to /microlensing.zah.uni-heidelberg.de
         if 'ev_ogle':
            ev_name = ev_ogle
            survey_name = "OGLE"
            event_number = ev_name.split('-')[-1]
         elif 'ev_moa':
            ev_name = ev_moa
            survey_name = "MOA"
            event_number = ev_name.split('-')[-1]
         elif 'ev_kmt':
            ev_name = ev_kmt
            survey_name = "KMT"
            event_number = ev_name.split('-')[-1]
         field = Event.objects.get(pk=event_id).field.name
         # Get list of all observations and select the one with the most recent time.
         try:
            event = Event.objects.get(id=event_id)
            single_recent = SingleModel.objects.select_related().filter(event=event).values().latest('last_updated')
            obs_recent = DataFile.objects.select_related().filter(event=event).values().latest('last_hjd')
            status_recent = Event.objects.get(pk=event_id).status
            #status_recent = RobonetStatus.objects.select_related().filter(event=event).values().latest('timestamp')
            # Make sure duplicate entries are avoided. Start adding by most recent files
            data_all = DataFile.objects.filter(event_id=event_id).order_by('last_hjd').reverse()
            data = []
            check_list = []
            for f in data_all:
               if f.datafile not in check_list:
        	  data.append(f)
               check_list.append(f.datafile)
            labels = []
            values = []
            colors = []
            for i in data:
               if 'LCOGT' in i.tel:
        	  labels.append(i.tel)
        	  values.append(i.ndata)
        	  try:
        	     colors.append('#'+col_dict[site_dict[i.datafile.split('/')[-1][0]][1]])
        	  except:
        	     import random
        	     r = lambda: random.randint(0,255)
        	     rand_col = '#%02X%02X%02X' % (r(),r(),r())
        	     colors.append(rand_col)
            #ndata = sum([(i.ndata) for i in data]) # Contains ALL data from ALL telescopes
            ndata = sum(values) # Contains only LCOGT data
            pie_chart(labels, colors, values, ndata, event_id)
            if labels == []:
               my_pie = 'No RoboNet data'
            else:
               my_pie = '<img src="/media/%s.png" height="300" width="300">' % str(event_id)
            try:
               cadence = Tap.objects.filter(event_id=event_id)[0].tsamp
            except:
               cadence = -1
            last_obs_hjd = obs_recent['last_hjd']
            last_obs = Time(float(last_obs_hjd), format='jd', scale='utc').iso
            last_updated = single_recent['last_updated']
            last_updated_hjd =  Time(last_updated).jd
            tel_id = obs_recent['datafile'].split('/')[-1].split('_')
            if len(tel_id) == 2:
               tel_id = tel_id[0]+'_'
            else:
               tel_id = obs_recent['datafile'].split('/')[-1][0]
            last_obs_tel = site_dict[tel_id][-1]
            status = status_recent
            ogle_url = ''
            if "OGLE" in ev_name:
               ogle_url = 'http://ogle.astrouw.edu.pl/ogle4/ews/%s/%s.html' % (ev_name.split('-')[1], 'blg-'+ev_name.split('-')[-1])
         except:
            #pie_url = ''
            my_pie = 'Image Failed to Load'
            cadence = -1
            ndata = 0
            last_obs = "N/A"
            last_obs_hjd = "N/A"
            last_updated = "N/A"
            last_updated_hjd = "N/A"
            last_obs_tel = "N/A"
	    try:
               status = Event.objects.get(pk=event_id).status
	    except:
	       status = "EX"
	    ogle_url = ''
	    try:
	       if "OGLE" in ev_name:
                  ogle_url = 'http://ogle.astrouw.edu.pl/ogle4/ews/%s/%s.html' % (ev_name.split('-')[1], 'blg-'+ev_name.split('-')[-1])
	    except:
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
         context = {'event_id': event_id, 'event_name': ev_names, 'field': field,
        	    'ev_ra': ev_ra, 'ev_dec':ev_dec, 'cadence':cadence,
        	    #'pie_url':pie_url,
        	    'my_pie':my_pie,
        	    'last_obs':last_obs, 'last_obs_hjd':last_obs_hjd,
        	    'status':possible_status[status],
        	    'last_obs_tel':last_obs_tel, 'ogle_url':ogle_url, 'time_now': time_now,
        	    'time_now_jd': time_now_jd}
      except Event.DoesNotExist:
         raise Http404("Event does not exist.")
      return render(request, 'events/event_obs_details.html', context)
   else:
      return HttpResponseRedirect('login')
 

##############################################################################################################
@login_required(login_url='/db/login/')
def query_obs_requests(request):
    """Function to provide an endpoint for users to query what observation
    requests have been made for a specific target"""
    
    if request.user.is_authenticated():
        if request.method == "POST":
            form = QueryObsRequestForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                qs = ObsRequest.objects.filter(
                        field = post.field,
                        )
                    
                obs_list = []
                for q in qs:
                    obs = { 'id':q.grp_id, 'field': q.field, \
                            'submit_date':q.timestamp.strftime("%Y-%m-%dT%H:%M:%S"),\
                            'expire_date':q.time_expire.strftime("%Y-%m-%dT%H:%M:%S")
                            }
                    obs_list.append(obs)
                return render(request, 'events/query_obs_requests.html', \
                                    {'form': form, 'observations': obs_list,
                                     'message': 'OK: got query set'})
            else:
                form = QueryObsRequestForm()
                return render(request, 'events/query_obs_requests.html', \
                                    {'form': form, 'qs': [],\
                                    'message':'Form entry was invalid.  Please try again.'})
        else:
            form = QueryObsRequestForm()
            return render(request, 'events/query_obs_requests.html', \
                                    {'form': form, 'qs': [],
                                    'message': 'OK'})
    else:
        return HttpResponseRedirect('login')


##############################################################################################################
@api_view(['GET'])
@authentication_classes((TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def query_obs_by_date(request, timestamp, time_expire, request_status):
    """Function to provide an endpoint for users to query what observation
    requests have been made within a specified date range"""
    
    if request.user.is_authenticated():
        
        if request.method == "GET":

            qs = ObsRequest.objects.filter(
                        timestamp__gt = timestamp,
                        time_expire__lte = time_expire,
                        request_status = request_status)
                
            obs_list = []
                
            for q in qs:
                obs = { 'pk': q.pk, 'grp_id':q.grp_id, 'track_id': q.track_id,
                        'submit_date':q.timestamp.strftime("%Y-%m-%dT%H:%M:%S"),
                        'expire_date':q.time_expire.strftime("%Y-%m-%dT%H:%M:%S"),
                        'request_status': q.request_status
                        }
                        
                obs_list.append(obs)
            
            if len(obs_list) == 0:
                
                message = 'DBREPLY: No matching observations'
                
            else:
                
                message = 'DBREPLY: Got observations list'
            
            return render(request, 'events/query_obs_by_date.html', \
                                    {'observations': obs_list,
                                     'message': message})
                                     
    else:

        return HttpResponseRedirect('login')



##############################################################################################################
@login_required(login_url='/db/login/')
def record_obs_request(request):
    """Function to allow new (submitted) observation requests to be 
    recorded in the database"""
        
    if request.user.is_authenticated():
        if request.method == "POST":
            form = RecordObsRequestForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                status = update_db_2.add_request(post.field,post.t_sample,\
                            post.exptime, timestamp=post.timestamp, \
                            time_expire=post.time_expire,n_exp=post.n_exp)
                
                return render(request, 'events/record_obs_request.html', \
                                    {'form': form, 'message': status})
            else:
                form = RecordObsRequestForm()
                # Add form data to output for debugging
                return render(request, 'events/record_obs_request.html', \
                                    {'form': form, \
                                    'message':'Form entry was invalid.<br> Reason: <br>'+\
                                    repr(form.errors)+'<br>Please try again.'})
        else:
            form = RecordObsRequestForm()
            return render(request, 'events/record_obs_request.html', \
                                    {'form': form, 
                                    'message': 'none'})
    else:
        return HttpResponseRedirect('login')

##############################################################################################################
@login_required(login_url='/db/login/')
def record_sub_obs_request_form(request):
    """Function to provide a web form to allow new sub-requests to be 
    added to the database"""
    
    if request.user.is_authenticated():
        
        if request.method == "POST":
            
            form = RecordSubObsRequestForm(request.POST)
            
            if form.is_valid():
                
                post = form.save(commit=False)

                (update_ok,message1) = update_db_2.add_sub_request(post.sr_id,
                                                           post.grp_id,
                                                           post.track_id,
                                                           post.window_start,
                                                           post.window_end, 
                                                           post.status, 
                                                           post.time_executed)
                                
                if update_ok:
                    
                    message = 'DBREPLY: Subrequest successfully added to database: '+message1
                    
                else:

                    if 'Subrequest already exists' in message:
                        
                        (update_ok,message2) = update_db_2.update_sub_request(post.sr_id,
                                                           post.grp_id,
                                                           post.track_id,
                                                           post.window_start,
                                                           post.window_end, 
                                                           post.status, 
                                                           post.time_executed)
                    message = message+' '+message2
                    
                return render(request, 'events/record_sub_obs_request_form.html', \
                                    {'form': form, 'message': message})
            else:
                
                form = RecordSubObsRequestForm()

                return render(request, 'events/record_sub_obs_request_form.html', \
                                    {'form': form, \
                                    'message':'Form entry was invalid.<br> Reason: <br>'+\
                                    repr(form.errors)+'<br>Please try again.'})
                                    
        else:

            form = RecordSubObsRequestForm()

            return render(request, 'events/record_sub_obs_request_form.html', \
                                    {'form': form, 
                                    'message': 'none'})

    else:

        return HttpResponseRedirect('login')
        
@api_view(['POST'])
@authentication_classes((TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def record_sub_obs_request(request, sr_id, grp_id, track_id, 
                           window_start,window_end,status,time_executed=None):
    """Function to provide an API endpoint to allow new sub-requests to be 
    added to the database"""
    
    if request.user.is_authenticated():
        
        
        (update_ok,message) = update_db_2.add_sub_request(sr_id,
                                                           grp_id,
                                                           track_id,
                                                           window_start,
                                                           window_end, 
                                                           status, 
                                                           time_executed)
        
        if update_ok:
                
            message = 'DBREPLY: Subrequest successfully added to database'
                
        else:

            if 'Subrequest already exists' in message:
                
                (update_ok,message) = update_db_2.update_sub_request(sr_id,
                                                   grp_id,
                                                   track_id,
                                                   window_start,
                                                   window_end, 
                                                   status, 
                                                   time_executed)
        
        return render(request, 'events/record_sub_obs_request.html', \
                            {'message': message})
                                
    else:

        return HttpResponseRedirect('login')

@api_view(['POST'])
@authentication_classes((TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def test_token(request):
    content = {
        'user': unicode(request.user),  # `django.contrib.auth.User` instance.
        'auth': unicode(request.auth),  # None
    }
    return Response(content)
    
##############################################################################################################
@login_required(login_url='/db/login/')
def add_operator(request):
    """Function to allow new operator to be 
    recorded in the database"""
        
    if request.user.is_authenticated():
        if request.method == "POST":
            form = OperatorForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                status = update_db_2.add_operator(post.name)
                
                return render(request, 'events/add_operator.html', \
                                    {'form': form, 'message': status})
            else:
                form = OperatorForm(request.POST)
                # Add form data to output for debugging
                return render(request, 'events/add_operator.html', \
                                    {'form': form, \
                                    'message':'Form entry was invalid.<br> Reason: <br>'+\
                                    repr(form.errors)+'<br>Please try again.'})
        else:
            form = OperatorForm(request.POST)
            return render(request, 'events/add_operator.html', \
                                    {'form': form, 
                                    'message': 'none'})
    else:
        return HttpResponseRedirect('login')

##############################################################################################################
@login_required(login_url='/db/login/')
def add_telescope(request):
    """Function to allow new telescope to be 
    recorded in the database"""
        
    if request.user.is_authenticated():
        if request.method == "POST":
            form = TelescopeForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                status = update_db_2.add_telescope(operator=post.operator,telescope_name=post.telescope_name,\
                            aperture=post.aperture, longitude=post.longitude, latitude=post.latitude,\
                            altitude=post.altitude, site=post.site)
                
                return render(request, 'events/add_telescope.html', \
                                    {'form': form, 'message': status})
            else:
                form = TelescopeForm(request.POST)
                # Add form data to output for debugging
                return render(request, 'events/add_telescope.html', \
                                    {'form': form, \
                                    'message':'Form entry was invalid.<br> Reason: <br>'+\
                                    repr(form.errors)+'<br>Please try again.'})
        else:
            form = TelescopeForm(request.POST)
            return render(request, 'events/add_telescope.html', \
                                    {'form': form, 
                                    'message': 'none'})
    else:
        return HttpResponseRedirect('login')

##############################################################################################################
@login_required(login_url='/db/login/')
def add_event(request):
    """Function to allow new event to be 
    recorded in the database"""
        
    if request.user.is_authenticated():
        if request.method == "POST":
            form = EventForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                status = update_db_2.add_event(field_name=post.field, operator_name=post.operator,
		                               ev_ra=post.ev_ra, ev_dec=post.ev_dec, status=post.status,
					       anomaly_rank=post.anomaly_rank, year=post.year)
                
                return render(request, 'events/add_event.html', \
                                    {'form': form, 'message': status})
            else:
                form = EventForm(request.POST)
                # Add form data to output for debugging
                return render(request, 'events/add_event.html', \
                                    {'form': form, \
                                    'message':'Form entry was invalid.<br> Reason: <br>'+\
                                    repr(form.errors)+'<br>Please try again.'})
        else:
            form = EventForm(request.POST)
            return render(request, 'events/add_event.html', \
                                    {'form': form, 
                                    'message': 'none'})
    else:
        return HttpResponseRedirect('login')

##############################################################################################################
@login_required(login_url='/db/login/')
def add_eventname(request):
    """Function to allow new eventname to be 
    recorded in the database"""
        
    if request.user.is_authenticated():
        if request.method == "POST":
            form = EventNameForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                status = update_db_2.add_event_name(event=post.event, operator=post.operator,
		                                    name=post.name)
                
                return render(request, 'events/add_eventname.html', \
                                    {'form': form, 'message': status})
            else:
                form = EventNameForm(request.POST)
                # Add form data to output for debugging
                return render(request, 'events/add_eventname.html', \
                                    {'form': form, \
                                    'message':'Form entry was invalid.<br> Reason: <br>'+\
                                    repr(form.errors)+'<br>Please try again.'})
        else:
            form = EventNameForm(request.POST)
            return render(request, 'events/add_eventname.html', \
                                    {'form': form, 
                                    'message': 'none'})
    else:
        return HttpResponseRedirect('login')

##############################################################################################################
@login_required(login_url='/db/login/')
def add_singlemodel(request):
    """Function to allow new Single Model to be 
    recorded in the database"""
        
    if request.user.is_authenticated():
        if request.method == "POST":
            form = SingleModelForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
		evname = EventName.objects.filter(event_id=post.event)[0].name
                status = update_db_2.add_single_lens(event_name=str(evname),
		                                     Tmax=post.Tmax,
						     tau=post.tau,
						     umin=post.umin,
						     e_Tmax=post.e_Tmax,
						     e_tau=post.e_tau,
						     e_umin=post.e_umin,
						     modeler=post.modeler,
						     rho=post.rho,
						     e_rho=post.e_rho,
						     pi_e_n=post.pi_e_n,
						     e_pi_e_n=post.e_pi_e_n,
						     pi_e_e=post.pi_e_e,
						     e_pi_e_e=post.e_pi_e_e,
						     last_updated=post.last_updated,
						     tap_omega=post.tap_omega,
						     chi_sq=post.chi_sq)
                
                return render(request, 'events/add_singlemodel.html', \
                                    {'form': form, 'message': status})
            else:
                form = SingleModelForm(request.POST)
                # Add form data to output for debugging
                return render(request, 'events/add_singlemodel.html', \
                                    {'form': form, \
                                    'message':'Form entry was invalid.<br> Reason: <br>'+\
                                    repr(form.errors)+'<br>Please try again.'})
        else:
            form = SingleModelForm(request.POST)
            return render(request, 'events/add_singlemodel.html', \
                                    {'form': form, 
                                    'message': 'none'})
    else:
        return HttpResponseRedirect('login')

##############################################################################################################
@login_required(login_url='/db/login/')
def add_binarymodel(request):
    """Function to allow new Binary Model to be 
    recorded in the database"""
        
    if request.user.is_authenticated():
        if request.method == "POST":
            form = BinaryModelForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
		evname = EventName.objects.filter(event_id=post.event)[0].name
                status = update_db_2.add_binary_lens(event_name=str(evname),
		                                     Tmax=post.Tmax,
						     tau=post.tau,
						     umin=post.umin,
						     e_Tmax=post.e_Tmax,
						     e_tau=post.e_tau,
						     e_umin=post.e_umin,
						     mass_ratio=post.mass_ratio,
						     e_mass_ratio=post.e_mass_ratio,
						     separation=post.separation,
 						     e_separation=post.e_separation,
 						     angle_a=post.angle_a,
 						     e_angle_a=post.e_angle_a,
 						     dsdt=post.dsdt,
 						     e_dsdt=post.e_dsdt,
 						     dadt=post.dadt,
 						     e_dadt=post.e_dadt,
						     modeler=post.modeler,
						     rho=post.rho,
						     e_rho=post.e_rho,
						     pi_e_n=post.pi_e_n,
						     e_pi_e_n=post.e_pi_e_n,
						     pi_e_e=post.pi_e_e,
						     e_pi_e_e=post.e_pi_e_e,
						     last_updated=post.last_updated,
						     chi_sq=post.chi_sq)
                
                return render(request, 'events/add_binarymodel.html', \
                                    {'form': form, 'message': status})
            else:
                form = BinaryModelForm(request.POST)
                # Add form data to output for debugging
                return render(request, 'events/add_binarymodel.html', \
                                    {'form': form, \
                                    'message':'Form entry was invalid.<br> Reason: <br>'+\
                                    repr(form.errors)+'<br>Please try again.'})
        else:
            form = BinaryModelForm(request.POST)
            return render(request, 'events/add_binarymodel.html', \
                                    {'form': form, 
                                    'message': 'none'})
    else:
        return HttpResponseRedirect('login')

##############################################################################################################
@login_required(login_url='/db/login/')
def add_eventreduction(request):
    """Function to allow new Event Reduction to be 
    recorded in the database"""
        
    if request.user.is_authenticated():
        if request.method == "POST":
            form = EventReductionForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
		evname = EventName.objects.filter(event_id=post.event)[0].name
                status = update_db_2.add_reduction(event_name=str(evname),
		                                   lc_file = post.lc_file,
						   timestamp = post.timestamp,
						   ref_image = post.ref_image,
						   target_found = post.target_found,
						   ron  = post.ron,
						   gain = post.gain,
                     				   oscanx1 = post.oscanx1,
						   oscanx2 = post.oscanx2,
						   oscany1 = post.oscany1,
						   oscany2 = post.oscany2,
						   imagex1 = post.imagex1,
						   imagex2 = post.imagex2,
		     				   imagey1 = post.imagey1,
						   imagey2 = post.imagey2,
						   minval = post.minval,
						   maxval  = post.maxval,
						   growsatx = post.growsatx,
		     				   growsaty  = post.growsaty,
						   coeff2  = post.coeff2,
						   coeff3 = post.coeff3,
		     				   sigclip  = post.sigclip,
						   sigfrac  = post.sigfrac,
						   flim = post.flim,
						   niter = post.niter,
						   use_reflist  = post.use_reflist,
						   max_nimages = post.max_nimages,
		     				   max_sky  = post.max_sky,
						   min_ell  = post.min_ell,
						   trans_type  = post.trans_type,
						   trans_auto  = post.trans_auto,
						   replace_cr = post.replace_cr,
		     				   min_scale  = post.min_scale,
						   max_scale = post.max_scale,
		     				   fov  = post.fov,
						   star_space = post.star_space,
						   init_mthresh = post.init_mthresh,
						   smooth_pro  = post.smooth_pro,
						   smooth_fwhm = post.smooth_fwhm,
		     				   var_deg  = post.var_deg,
						   det_thresh  = post.det_thresh,
						   psf_thresh  = post.psf_thresh,
						   psf_size = post.psf_size,
						   psf_comp_dist = post.psf_comp_dist,
		     				   psf_comp_flux = post.psf_comp_flux,
						   psf_corr_thresh = post.psf_corr_thresh,
						   ker_rad  = post.ker_rad,
						   lres_ker_rad = post.lres_ker_rad,
		     				   subframes_x  = post.subframes_x,
						   subframes_y  = post.subframes_y,
						   grow = post.grow,
						   ps_var  = post.ps_var,
						   back_var  = post.back_var,
						   diffpro = post.diffpro)
                
                return render(request, 'events/add_eventreduction.html', \
                                    {'form': form, 'message': status})
            else:
                form = EventReductionForm(request.POST)
                # Add form data to output for debugging
                return render(request, 'events/add_eventreduction.html', \
                                    {'form': form, \
                                    'message':'Form entry was invalid.<br> Reason: <br>'+\
                                    repr(form.errors)+'<br>Please try again.'})
        else:
            form = EventReductionForm(request.POST)
            return render(request, 'events/add_eventreduction.html', \
                                    {'form': form, 
                                    'message': 'none'})
    else:
        return HttpResponseRedirect('login')

##############################################################################################################
@login_required(login_url='/db/login/')
def add_tap(request):
    """Function to allow a new tap entry to be 
    recorded in the database"""
        
    if request.user.is_authenticated():
        if request.method == "POST":
            form = TapForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
		evname = EventName.objects.filter(event_id=post.event)[0].name
                status = update_db_2.add_tap(event_name=evname, 
		                             timestamp=post.timestamp, 
					     priority=post.priority, 
					     tsamp=post.tsamp, 
					     texp=post.texp, 
					     nexp=post.nexp,
					     telclass=post.telclass, 
					     imag=post.imag, 
					     omega=post.omega, 
					     err_omega=post.err_omega, 
					     peak_omega=post.peak_omega, 
					     blended=post.blended,
					     visibility=post.visibility, 
					     cost1m=post.cost1m, 
					     passband=post.passband,
					     ipp=post.ipp)
                
                return render(request, 'events/add_tap.html', \
                                    {'form': form, 'message': status})
            else:
                form = TapForm(request.POST)
                # Add form data to output for debugging
                return render(request, 'events/add_tap.html', \
                                    {'form': form, \
                                    'message':'Form entry was invalid.<br> Reason: <br>'+\
                                    repr(form.errors)+'<br>Please try again.'})
        else:
            form = TapForm(request.POST)
            return render(request, 'events/add_tap.html', \
                                    {'form': form, 
                                    'message': 'none'})
    else:
        return HttpResponseRedirect('login')

##############################################################################################################
@login_required(login_url='/db/login/')
def add_taplima(request):
    """Function to allow a new taplima entry to be 
    recorded in the database"""
        
    if request.user.is_authenticated():
        if request.method == "POST":
            form = TapLimaForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
		evname = EventName.objects.filter(event_id=post.event)[0].name
                status = update_db_2.add_taplima(event_name=evname, 
		                             timestamp=post.timestamp, 
					     priority=post.priority, 
					     tsamp=post.tsamp, 
					     texp=post.texp, 
					     nexp=post.nexp,
					     telclass=post.telclass, 
					     imag=post.imag, 
					     omega=post.omega, 
					     err_omega=post.err_omega, 
					     peak_omega=post.peak_omega, 
					     blended=post.blended,
					     visibility=post.visibility, 
					     cost1m=post.cost1m, 
					     passband=post.passband,
					     ipp=post.ipp)
                
                return render(request, 'events/add_taplima.html', \
                                    {'form': form, 'message': status})
            else:
                form = TapForm(request.POST)
                # Add form data to output for debugging
                return render(request, 'events/add_taplima.html', \
                                    {'form': form, \
                                    'message':'Form entry was invalid.<br> Reason: <br>'+\
                                    repr(form.errors)+'<br>Please try again.'})
        else:
            form = TapForm(request.POST)
            return render(request, 'events/add_taplima.html', \
                                    {'form': form, 
                                    'message': 'none'})
    else:
        return HttpResponseRedirect('login')


##############################################################################################################
@login_required(login_url='/db/login/')
def add_datafile(request):
    """Function to allow a new ARTEMiS datafile entry to be 
    recorded in the database"""
        
    if request.user.is_authenticated():
        if request.method == "POST":
            form = DataFileForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
		evname = EventName.objects.filter(event_id=post.event)[0].name
                status = update_db_2.add_datafile(event_name=evname,
						  datafile=post.datafile,
						  last_upd=post.last_upd,
						  last_hjd=post.last_hjd,
						  last_mag=post.last_mag, 
						  tel=post.tel, 
						  ndata=post.ndata, 
						  inst=post.inst, 
						  filt=post.filt, 
						  baseline=post.baseline, 
						  g=post.g)
                
                return render(request, 'events/add_datafile.html', \
                                    {'form': form, 'message': status})
            else:
                form = DataFileForm(request.POST)
                # Add form data to output for debugging
                return render(request, 'events/add_datafile.html', \
                                    {'form': form, \
                                    'message':'Form entry was invalid.<br> Reason: <br>'+\
                                    repr(form.errors)+'<br>Please try again.'})
        else:
            form = DataFileForm(request.POST)
            return render(request, 'events/add_datafile.html', \
                                    {'form': form, 
                                    'message': 'none'})
    else:
        return HttpResponseRedirect('login')

##############################################################################################################
@login_required(login_url='/db/login/')
def add_image(request):
    """Function to allow a new image entry to be 
    recorded in the database"""
        
    if request.user.is_authenticated():
        if request.method == "POST":
            form = ImageForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                status = update_db_2.add_image(field_name = post.field,
					       image_name = post.image_name,
					       date_obs = post.date_obs,
					       timestamp = post.timestamp,
					       tel = post.tel,
					       inst = post.inst,
					       filt = post.filt,
					       grp_id = post.grp_id,
					       track_id = post.track_id,
					       req_id = post.req_id,
					       airmass = post.airmass,
					       avg_fwhm = post.avg_fwhm,
					       avg_sky = post.avg_sky,
					       avg_sigsky = post.avg_sigsky,
					       moon_sep = post.moon_sep,
					       moon_phase = post.moon_phase,
					       moon_up = post.moon_up,
					       elongation = post.elongation,
					       nstars = post.nstars,
					       ztemp = post.ztemp,
					       shift_x = post.shift_x,
					       shift_y = post.shift_y,
					       quality = post.quality)
                
                return render(request, 'events/add_image.html', \
                                    {'form': form, 'message': status})
            else:
                form = ImageForm(request.POST)
                # Add form data to output for debugging
                return render(request, 'events/add_image.html', \
                                    {'form': form, \
                                    'message':'Form entry was invalid.<br> Reason: <br>'+\
                                    repr(form.errors)+'<br>Please try again.'})
        else:
            form = ImageForm(request.POST)
            return render(request, 'events/add_image.html', \
                                    {'form': form, 
                                    'message': 'none'})
    else:
        return HttpResponseRedirect('login')

##############################################################################################################
@login_required(login_url='/db/login/')
def record_data_file(request):
    """Function to allow ARTEMiS data files to be recorded in the database"""
    
    if request.user.is_authenticated():
        if request.method == "POST":
            fform = RecordDataFileForm(request.POST)
            eform = EventNameForm(request.POST)
            if fform.is_valid() and eform.is_valid():
                fpost = fform.save(commit=False)
                epost = eform.save(commit=False)
                params = extract_data_file_post_params(fpost,epost)
                
                (status,message) = update_db_2.add_datafile_via_api(params)
                
                return render(request, 'events/record_data_file.html', \
                                    {'fform': fform, 'eform':eform, \
                                    'message': message})
            else:
                fform = RecordDataFileForm()
                eform = EventNameForm(request.POST)
                return render(request, 'events/record_data_file.html', \
                                    {'fform': fform, 'eform': eform,\
                                    'message':'Form entry was invalid.  Please try again. \n'})
        else:
            fform = RecordDataFileForm()
            eform = EventNameForm(request.POST)
            return render(request, 'events/record_data_file.html', \
                                    {'fform': fform, 'eform': eform,
                                    'message': 'none'})
    else:
        return HttpResponseRedirect('login')

##############################################################################################################
def extract_data_file_post_params(fpost,epost):
    """Function to extract the parameters from a form post to a dictionary."""
    
    params = {'event_name': epost.name,\
              'datafile': fpost.datafile,\
              'last_mag': float(fpost.last_mag),\
              'tel': fpost.tel,
              'filt': fpost.filt,
              'baseline': float(fpost.baseline),
              'g': float(fpost.g),
              'ndata': int(fpost.ndata),
              'last_obs': fpost.last_obs,\
              'last_upd': fpost.last_upd
              }
    
    return params

##############################################################################################################
@login_required(login_url='/db/login/')
def data_quality_control(request):
    """Function to display quality control information from reception"""
        
    if request.user.is_authenticated():
        plot_path = db_plotting_utilities.plot_image_rejection_statistics()
        return render(request, 'events/data_quality_display.html', \
                                    {'plot_file': plot_path})
    else:
        return HttpResponseRedirect('login')

