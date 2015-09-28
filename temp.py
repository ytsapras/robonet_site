python manage.py migrate
python manage.py shell

from events.models import Event, Single_Model, Binary_Model, Data_File, Robonet_Log, Robonet_Reduction, Robonet_Request, Robonet_Status, Ogle_Detail, Moa_Detail, Kmt_Detail
from django.utils import timezone

ev1 = Event(ev_name_ogle="OGLE-2015-BLG-1643", ev_ra="17:55:01.64", ev_dec="-29:16:00.3")
ev1.save()
ev2 = Event(ev_name_ogle="OGLE-2015-BLG-0017", ev_ra="17:35:32.16", ev_dec="-27:02:35.3")
ev2.save()
ev3 = Event(ev_name_moa="MOA-2015-BLG-531", ev_ra="18:19:12.56", ev_dec="-21:32:33.75", bright_neighbour=True)
ev3.save()

Event.objects.all()

e1 = Event.objects.get(ev_name_ogle="OGLE-2015-BLG-1643")
e1.ogle_detail_set.update_or_create(Tmax=2457275.553, tau=22.693, umin=0.129, last_updated=timezone.now(), url_link="http://ogle.astrouw.edu.pl/ogle4/ews/blg-1643.html")
e1.single_model_set.update_or_create(Tmax=2457275.553, tau=22.693, umin=0.129, Amax=7.785, I_base=17.142, last_updated=timezone.now())
e1.save()

# Update single Field in Model
Event.objects.filter(ev_name_moa="MOA-2015-BLG-531").update(ev_name_ogle="OGLE-2015-BLG-9999")

Event.objects.filter(ev_name_ogle="OGLE-2015-BLG-9999")

print e1.ev_name_ogle, e1.ev_ra
print e1.single_model_set.all().values()
print e1.single_model_set.all().values('tau')
print e1.single_model_set.all().values("last_updated")[e1.single_model_set.count()-1]
print Event.objects.filter(ev_name_moa__contains="MOA")
print e1.robonet_log_set.all().values('image_name')
print e1.robonet_log_set.all().values('image_name')
t0 = 2289.803
tE = 13421.354
u0 = 04234.000
A0 = 294145.6
I0 = 128.716
t_upd = timezone.now()

lc_file = '/fdsfds/fsdfdsf/OGLE-2015-BLG-1643.t'
timestamp = t_upd
version = 1
ref_image = 'e_201245_blah.fits'

e1.robonet_reduction_set.update_or_create(event = e1.id, lc_file = lc_file, timestamp = timestamp, version = version, ref_image = ref_image)
e1.save()

image_name = "lsc1m005-kb78-20150920-0076-e10.fits"
timestamp = timezone.now()
exptime = 288.0
filter1 = "air"
filter2 = "ip"
filter3 = "air"
telescope = "1m0-05"
instrument = "kb78"
group_id = "RBN20150920T14.00915103" 
track_id = "0000110736"
req_id = "0000426870"
airmass = 1.0443438
fwhm = 5.23
sky_bg = 8940.50011236
sd_bg = 10.3780135512
moon_sep = 9.7428017
elongation = 1.22448314607
nstars = 89
quality = "Rejected: High average sky background : Few stars in the frame: Too close to Moon"

e1.robonet_log_set.update_or_create(event = e1.id, image_name = image_name, timestamp = timestamp, exptime = exptime,filter1 = filter1, filter2 = filter2, filter3 = filter3, telescope = telescope, instrument = instrument, group_id = group_id, track_id = track_id, req_id = req_id, airmass = airmass, fwhm = fwhm,sky_bg = sky_bg, sd_bg = sd_bg, moon_sep = moon_sep, elongation = elongation, nstars = nstars, quality = quality)
e1.save()

e1.robonet_request_set.update_or_create(event = e1.id, timestamp=timezone.now(), onem_on=False, twom_on=True, t_sample=30.0, exptime=260)
e1.save()

e1.robonet_status_set.update_or_create(event = e1.id, timestamp=timezone.now(), priority='M', status='CH', comment="This is a test by YT", updated_by="YT")
e1.save()

# Add new event to database
def add_new_event(event_name, event_ra, event_dec, which_survey):
   # Write code to check values are sensible
   ev = Event(ev_name=event_name, ev_ra=event_ra, ev_dec=event_dec,\
              ev_survey=which_survey)
   ev.save()

# Update or Create Single Lens model parameters to database
def single_lens_par(event_name, t0, tE, u0, A0, I0, t_upd):
  # Write code to check values are sensible
  try:
      ev = Event.objects.get(ev_name=event_name)
      ev.single_model_set.update_or_create(Tmax=t0, tau=tE, umin=u0, Amax=A0, I_base=I0, last_updated=t_upd)
      ev.save()
   except Event.DoesNotExist:
      print "Event does not exist."

# Update or Add a data file to database
def up_data_file(event_name, full_path_to_datafile):
  # Write code to check values are sensible
  try:
      ev = Event.objects.get(ev_name=event_name)
      ev.data_file_set.update_or_create(datafile=full_path_to_datafile)
      ev.save()
   except Event.DoesNotExist:
      print "Event does not exist."

# Update Log with new image details
def log_image(event_name, ev_ra, ev_dec, image_name, timestamp, exptime, filter1, filter2, filter3, telescope, instrument, group_id, track_id, req_id, airmass, fwhm, sky_bg, sd_bg, moon_sep, elongation, nstars, quality):
# Write code to check values are sensible
  try:
      ev = Event.objects.get(ev_name=event_name)
      ev.robonet_log_set.update_or_create(event = event_name, image_name = image_name, timestamp = timestamp, exptime = exptime,filter1 = filter1, filter2 = filter2, filter3 = filter3, telescope = telescope, instrument = instrument, group_id = group_id, track_id = track_id, req_id = req_id, airmass = airmass, fwhm = fwhm,sky_bg = sky_bg, sd_bg = sd_bg, moon_sep = moon_sep, elongation = elongation, nstars = nstars, quality = quality)
      ev.save()
   except Event.DoesNotExist:
      print "Event does not exist."

# Update reduction with new details
def lc_out(event_name, lc_file, timestamp, version, ref_image, ron, gain, oscanx1,oscanx2,oscany1,oscany2,imagex1,imagex2,imagey1,imagey2,minval,maxval,growsatx,growsaty,coeff2,coeff3,sigclip,sigfrac,flim,niter,use_reflist,max_nimages,max_sky,min_ell,trans_type,trans_auto,replace_cr,min_scale,max_scale,fov,star_space,init_mthresh,smooth_pro,smooth_fwhm,var_deg,det_thresh,psf_thresh,psf_size,psf_comp_dist,psf_comp_flux,psf_corr_thresh,ker_rad,lres_ker_rad,subframes_x,subframes_y,grow,ps_var,back_var,diffpro):
# Write code to check values are sensible
  try:
      ev = Event.objects.get(ev_name=event_name)
      ev.robonet_reductions_set.update_or_create(event = event_name, lc_file = lc_file, timestamp = timestamp, version = version, ref_image = ref_image, ron = ron, gain = gain, oscanx1 = oscanx1 ,oscanx2 = oscanx2 ,oscany1 = oscany1,oscany2 = oscany2, imagex1 = imagex1, imagex2 = imagex2, imagey1 = imagey1, imagey2 = imagey2, minval = minval, maxval = maxval, growsatx = growsatx, growsaty = growsaty, coeff2 = coeff2, coeff3 = coeff3, sigclip = sigclip, sigfrac = sigfrac, flim = flim, niter = niter, use_reflist = use_reflist, max_nimages = max_nimages, max_sky = max_sky, min_ell = min_ell, trans_type = trans_type, trans_auto = trans_auto, replace_cr = replace_cr, min_scale = min_scale, max_scale = max_scale, fov = fov, star_space = star_space, init_mthresh = init_mthresh, smooth_pro = smooth_pro, smooth_fwhm = smooth_fwhm, var_deg = var_deg, det_thresh = det_thresh, psf_thresh = psf_thresh, psf_size = psf_size, psf_comp_dist = psf_comp_dist, psf_comp_flux = psf_comp_flux, psf_corr_thresh = psf_corr_thresh, ker_rad = ker_rad, lres_ker_rad = lres_ker_rad, subframes_x = subframes_x, subframes_y = subframes_y, grow = grow, ps_var = ps_var, back_var = back_var, diffpro = diffpro)
      ev.save()
   except Event.DoesNotExist:
      print "Event does not exist."

lc_file = '/fdsfds/fsdfdsf/OGLE-2015-BLG-1643.t'
timestamp = t_upd
version = 1
ref_image = 'e_201245_blah.fits'
data_file = "OGLE-2015-BLG-1643.K.dat"
e1.robonet_reduction_set.update_or_create(event = e1.id, lc_file = lc_file, timestamp = timestamp, version = version, ref_image = ref_image)
e1.save()

e1.data_file_set.update_or_create(event = e1.id, datafile= data_file, last_updated=timezone.now(),last_magnitude=16.534,telescope="1m0-05",version=1,ndata=10)
e1.save()

log_image(e.ev_name,"lsc1m005-kb78-20150920-0076-e10.fits", timezone.now(), 288.0, "air", "ip", "air", "1m0-05", "kb78", "RBN20150920T14.00915103", "0000110736", "0000426870", 1.0443438, 5.23, 8940.50011236, 10.3780135512, 9.7428017, 1.22448314607, 89, "Rejected: High average sky background : Few stars in the frame: Too close to Moon")


e.robonet_reductions_set.update_or_create()
e.save()

Robonet_Log.objects.all()

delme = Single_Model.objects.all()[3]
delme.delete()

Data_File.objects.all().values()

kwargs = {'event':'OGLE-2015-BLG-9999', 'lc_file':'/lightcurve_file.lc', 'timestamp':timezone.now(), 'version':1,
          'ref_image':'/reference.fits', 'ron':0.0, 'gain':1.0,
          'oscanx1':1, 'oscanx2':50, 'oscany1':1, 'oscany2':500, 'imagex1':51, 'imagex2':1000,
	  'imagey1':1, 'imagey2':1000, 'minval':1.0, 'maxval':55000.0, 'growsatx':0,
	  'growsaty':0, 'coeff2':1.0e-06, 'coeff3':1.0e-12,
	  'sigclip':4.5, 'sigfrac':0.5, 'flim':2.0, 'niter':4, 'use_reflist':0, 'max_nimages':1,
	  'max_sky':5000.0, 'min_ell':0.8, 'trans_type':'polynomial', 'trans_auto':0, 'replace_cr':0,
	  'min_scale':0.99, 'max_scale':1.01,
	  'fov':0.1, 'star_space':30, 'init_mthresh':1.0, 'smooth_pro':2, 'smooth_fwhm':3.0,
	  'var_deg':1, 'det_thresh':2.0, 'psf_thresh':8.0, 'psf_size':8.0, 'psf_comp_dist':0.7,
	  'psf_comp_flux':0.1, 'psf_corr_thresh':0.9, 'ker_rad':2.0, 'lres_ker_rad':2.0,
	  'subframes_x':1, 'subframes_y':1, 'grow':0.0, 'ps_var':0, 'back_var':1, 'diffpro':0}
