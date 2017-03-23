from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, HttpResponseRedirect
from events.models import Field, Operator, Telescope, Instrument, Filter, Event, EventName, SingleModel, BinaryModel
from events.models import EventReduction, ObsRequest, EventStatus, DataFile, Tap, Image
from itertools import chain
from astropy.time import Time
from datetime import datetime, timedelta
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import components
import sys, os
#from events.forms import OperatorForm, TelescopeForm, InstrumentForm, FilterForm 
#from events.forms import EventForm, EventNameForm, SingleModelForm, BinaryModelForm, RobonetReductionForm
#from events.forms import RobonetRequestForm, RobonetStatusForm, DataFileForm, TapForm, ImageForm
from scripts.plotter import *
from scripts.local_conf import get_conf
from scripts.blgvis import *
from scripts.utilities import short_to_long_name

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
#@login_required
#@require_http_methods(['GET', 'POST'])
#def add_operator(request):
#   """
#   Adds a new operator name in the database.
#   This can be the survey name or the name of the follow-up group.
#   
#   Keyword arguments:
#   operator_name -- The operator name 
#                    (string, required)
#   """
#   #try:
#   form = OperatorForm(request.POST or None)
#   if request.POST and form.is_valid():
#      opname = Operator.objects.filter(name=request.POST['name'])
#      if len(opname) == 0:
#         form.save()
#	 return HttpResponse("New Operator successfully added.")
#      else:
#         return HttpResponse("An Operator with that name already exists.")
#   
#   d = {
#       'form': form,
#       }
#   #new_operator = Operator.objects.get_or_create(name=operator)
#   #new_operator.name = request.POST.get(operator)
#   #new_operator.save()
#   #if new_operator[-1] == False:
#   #   successful = False
#   #else:
#   #   successful = True
#   #except:
#   #   raise Http404("Encountered a problem while loading. Please contact the site administrator.")
#   #return HttpResponse("successful")
#   return render(request, 'add_operator.html', d)

##############################################################################################################
def dashboard(request):
   """
   Will display the database front view (dashboard).
   """
   if request.user.is_authenticated():
      try:
         status_time = datetime.now()
         date_today = str(status_time.year)+str(status_time.month).zfill(2)+str(status_time.day).zfill(2)
         status_time_jd = Time(status_time).jd
      except:
         raise Http404("Encountered a problem while loading. Please contact the site administrator.")
      context = {'status_time':status_time, 'status_time_jd':status_time_jd, 'date_today':date_today}
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
         download = open(filename,'rb')
         response = HttpResponse(download.read(),content_type='application/x-tar')
         response['Content-Disposition'] = 'attachment; filename="%s"' % filename.split('/')[-1]
      except:
         raise Http404("Encountered a problem while generating the tar file.")  
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
         download = open(filename,'rb')
         response = HttpResponse(download.read(),content_type='application/x-tar')
         response['Content-Disposition'] = 'attachment; filename="%s"' % filename.split('/')[-1]
      except:
         raise Http404("Encountered a problem while generating the tar file.")  
      return response
   else:
      return HttpResponseRedirect('login')

##############################################################################################################
@login_required(login_url='/db/login/')
def obs_log(request, date):
   """
   Will display the observation log for the given date.
   Date must be provided in the format: YYYYMMDD
   """
   if request.user.is_authenticated():
      try:
         date_min = datetime(int(date[0:4]), int(date[4:6]), int(date[6:8]))
         date_max = date_min + timedelta(hours=24)
      except:
         raise Http404("Encountered an error: Date must be provided in the format: YYYYMMDD")
      try:
         images = Image.objects.filter(date_obs__range=(date_min, date_max))
         filenames = [k.image_name for k in images]
         times = [k.date_obs for k in images]
         objects = [EventName.objects.filter(event_id = k.event.pk)[0].name for k in images]
         ras = [k.event.ev_ra for k in images]
         decs = [k.event.ev_dec for k in images]
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
         rows = zip(filenames, times, objects, ras, decs, filts, tels, insts, grp_ids, track_ids,
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
def tap(request):
   """
   Will load the TAP page.
   """
   if request.user.is_authenticated():
      try:
         time_now = datetime.now()
         time_now_jd = Time(time_now).jd
         ##### TAP query goes here ###
         #selection_model = SingleModel.objects.filter(umin__lte=0.00001, tau__lte=30)
         selection_tap = Tap.objects.filter(omega__gte=6.0).order_by('timestamp').reverse()
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
         count = 0
         for i in ev_id:
            evnm = EventName.objects.filter(event=i)
            names = [k.name for k in evnm]
            ev_ra = Event.objects.all().get(pk=i).ev_ra
            ev_dec = Event.objects.all().get(pk=i).ev_dec
            sampling_time = Tap.objects.all().get(event=i, timestamp=timestamp[count]).tsamp
            exposures = Tap.objects.all().get(event=i, timestamp=timestamp[count]).nexp
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
            soms = Tap.objects.all().get(event=i, timestamp=timestamp[count]).err_omega
            omsp = Tap.objects.all().get(event=i, timestamp=timestamp[count]).peak_omega
            vis = Tap.objects.all().get(event=i, timestamp=timestamp[count]).visibility
            nexp.append(exposures)
            texp.append(time_exp)
            cadence.append('Unknown')
            tsamp.append(sampling_time)
            priority.append(prior)
            imag.append(baseline)
            omega_s.append(oms)
            sig_omega_s.append(soms)
            omega_peak.append(omsp)
            names_list.append(names)
            visibility.append(vis)
            ra.append(ev_ra)
            dec.append(ev_dec)
            count = count + 1
         #### TAP rows need to be defined here ####
         rows = zip(colors, ev_id, names_list, ra, dec, cadence, nexp, texp, priority, tsamp, imag, omega_s,
        	    sig_omega_s, omega_peak, visibility)
         rowsrej = ''
         time1 = 'Unknown' # This should be an estimate of when the target list will be uploaded next (in minutes)
         time2 = str(blg_visibility(mlsites=['CPT','COJ','LSC'])) # This should be an estimate of the bulge visibility on <nsite> sites (in hours)
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
            single_recent = SingleModel.objects.select_related().filter(event=event).values().latest('last_updated')
            obs_recent = DataFile.objects.select_related().filter(event=event).values().latest('last_obs')
            #status_recent = RobonetStatus.objects.select_related().filter(event=event).values().latest('timestamp')
            status_recent = Event.objects.get(pk=event_id).status
            last_obs = obs_recent['last_obs']
            last_obs_hjd = Time(last_obs).jd
            tel_id = obs_recent['datafile'].split('/')[-1].split('_')
            if len(tel_id) == 2:
               tel_id = tel_id[0]+'_'
            else:
               tel_id = obs_recent['datafile'].split('/')[-1][0]
            last_obs_tel = site_dict[tel_id][-1]
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
            single_recent = SingleModel.objects.select_related().filter(event=event).values().latest('last_updated')
            obs_recent = DataFile.objects.select_related().filter(event=event).values().latest('last_obs')
            #status_recent = RobonetStatus.objects.select_related().filter(event=event).values().latest('timestamp')
            status_recent = Event.objects.get(pk=event_id).status
            last_obs = obs_recent['last_obs']
            last_obs_hjd = Time(last_obs).jd
            tel_id = obs_recent['datafile'].split('/')[-1].split('_')
            if len(tel_id) == 2:
               tel_id = tel_id[0]+'_'
            else:
               tel_id = obs_recent['datafile'].split('/')[-1][0]
            last_obs_tel = site_dict[tel_id][-1]
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
            obs_recent = DataFile.objects.select_related().filter(event=event).values().latest('last_obs')
            status_recent = Event.objects.get(pk=event_id).status
            #status_recent = RobonetStatus.objects.select_related().filter(event=event).values().latest('timestamp')
            # Make sure duplicate entries are avoided. Start adding by most recent files
            data_all = DataFile.objects.filter(event_id=event_id).order_by('last_upd').reverse()
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
            # Generate the plot.ly pie chart
            ######### Online Mode #########
            #import plotly.plotly as py
            #import plotly.graph_objs as go
            ######### Offline Mode #########
            #from plotly.offline import download_plotlyjs, plot
            #import plotly.graph_objs as go
            #fig = {
            #	 'data': [{'labels': labels,
            #		  'values': values,
            #		  'type': 'pie',
            #		  'textposition':"none",
            #		  'textinfo':"percent",
            #		  'textfont':{'size':'12'},
            #		  'showlegend':'false'}],
            #	 'layout': {'title': 'Obsevations:'+str(ndata),
            #		    'showlegend':'false',
            #		    'height':'200',
            #		    'width':'200',
            #		    'autosize':'false',
            #		    'margin':{'t':'50','l':'75','r':'0','b':'10'},
            #		    'separators':'.,'}
            #}
            ######### Online mode ##########
            # Get the correspongin plotly url for the chart
            #plotly_url = py.plot(fig, filename='Observations by site', auto_open=False)
            # Save the url in a variable to pass to the template
            #pie_url = '<iframe width="200" height="200" frameborder="0" seamless="seamless" scrolling="no" src='+plotly_url+'.embed?width=200&height=200&link=false&showlegend=false></iframe>'
            ################################
            ######### Offline mode #########
            # Get the correspongin plotly url for the chart
            #plotly_url = plot(fig, filename=plotly_path+'pie.html', auto_open=False)
            # Save the url in a variable to pass to the template
            #pie_url = '''<iframe width="200" height="200" frameborder="0" seamless="seamless" scrolling="no" src=\"'''+plotly_url+'''.embed?width=200&height=200&link=false&showlegend=false\"></iframe>'''
            ################################
            last_obs = obs_recent['last_obs']
            last_obs_hjd = Time(last_obs).jd
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
 
