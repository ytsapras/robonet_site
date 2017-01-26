import datetime

from django.db import models
from django.utils import timezone
from decimal import Decimal

# Known Operator (survey/follow-up)
class Operator(models.Model):
   def __str__(self):
      return self.name
   name = models.CharField("Operator Name", max_length=50, default='Other')

# Known Telescopes
class Telescope(models.Model):
   def __str__(self):
      return self.name
   operator = models.ForeignKey(Operator)
   name = models.CharField("Telescope name", max_length=100)
   aperture = models.DecimalField("Telescope Aperture (m)", max_digits=6,
                                  decimal_places=2, null=True, blank=True)
   latitude = models.DecimalField("Latitude (N) in decimal degrees",
                                  max_digits=8, decimal_places=4, null=True,
				  blank=True)
   longitude = models.DecimalField("Longitude (E) in decimal degrees",
                                   max_digits=8, decimal_places=4, null=True,
				   blank=True)
   altitude = models.DecimalField("Altitude (m)", max_digits=8,
                                  decimal_places=4, null=True, blank=True)
   site = models.CharField("Site name", max_length=100, blank=True, default="")

# Known Instruments
class Instrument(models.Model):
   def __str__(self):
      return self.name
   telescope = models.ForeignKey(Telescope)
   name = models.CharField("Instrument name", max_length=50)
   pixscale = models.DecimalField("Pixel scale (arcsec/pix)", max_digits=12,
                                  decimal_places=4, null=True, blank=True)

# Known Filters
class Filter(models.Model):
   def __str__(self):
      return self.name
   instrument = models.ForeignKey(Instrument)
   name = models.CharField("Filter name", max_length=50, blank=True)

# Generic Events class
class Event(models.Model):
   def __str__(self):
      return "RA: "+str(self.ev_ra)+" Dec: "+str(self.ev_dec)+" ID: "+str(self.pk)
   ev_ra = models.CharField("RA", max_length=50)
   ev_dec = models.CharField("Dec", max_length=50)
   # does the event have a bright neighbour?
   bright_neighbour = models.BooleanField("Bright neighbour", default=False)
   # Event status (not in ROME footprint, active (in ROME footprint), monitor (60m REA cadence), 
   #               anomaly (20m REA cadence), expired)
   possible_status = (
      ('NF', 'Not in footprint'),
      ('AC', 'active'),
      ('MO', 'monitor'),
      ('AN', 'anomaly'),
      ('EX', 'expired')
   )
   status = models.CharField("Event status", max_length=30, choices=possible_status,
                             default='NF')
   # Which ROME field does this event belong to? Options: -1 (None) or an integer from 1 to N,
   # where N is the number of fields monitored (20)
   field = models.IntegerField("Field Number", default=-1)
   # What is the relative importance of the anomaly?
   anomaly_rank = models.DecimalField("Anomaly Rank", max_digits=12, decimal_places=4, 
                                      default=Decimal('-1.0'))

# Generic Events Name class
# EventName uses two foreign keys so related_name needs to be set
class EventName(models.Model):
   def __str__(self):
      return "Name:"+str(self.name)+" ID: "+str(self.event_id)
   event = models.ForeignKey(Event, related_name="event_id")
   operator = models.ForeignKey(Operator, related_name="operator_id")
   name = models.CharField("Survey Event Name", max_length=50)

# Single lens parameters
class SingleModel(models.Model):
   def __str__(self):
      return str(self.event)+' updated at '+str(self.last_updated)
   event = models.ForeignKey(Event)
   Tmax = models.DecimalField("Tmax", max_digits=12,decimal_places=4)
   e_Tmax = models.DecimalField("sig(Tmax)", max_digits=12,decimal_places=4)
   tau = models.DecimalField("T_E", max_digits=12,decimal_places=4)
   e_tau = models.DecimalField("sig(T_E)", max_digits=12,decimal_places=4)
   umin = models.DecimalField("u_min", max_digits=12,decimal_places=4)
   e_umin = models.DecimalField("sig(u_min)", max_digits=12,decimal_places=4)
   rho = models.DecimalField("rho", max_digits=12,decimal_places=4,
                             null=True, blank=True)
   e_rho = models.DecimalField("sig(rho)", max_digits=12,decimal_places=4,
                             null=True, blank=True)
   pi_e_n = models.DecimalField("Parallax EN", max_digits=12,decimal_places=4,
                                null=True, blank=True)
   e_pi_e_n = models.DecimalField("sig(Parallax EN)", max_digits=12,decimal_places=4,
                                null=True, blank=True)
   pi_e_e = models.DecimalField("Parallax EE", max_digits=12,decimal_places=4,
                                null=True, blank=True)
   e_pi_e_e = models.DecimalField("sig(Parallax EE)", max_digits=12,decimal_places=4,
                                null=True, blank=True)
   modeler = models.CharField("Modeler", max_length=25, blank=True, default="")
   last_updated = models.DateTimeField('date last updated')

# Binary Lens parameters
class BinaryModel(models.Model):
   def __str__(self):
      return str(self.event)+' updated at '+str(self.last_updated)
   event = models.ForeignKey(Event)
   Tmax = models.DecimalField("Tmax", max_digits=12,decimal_places=4)
   e_Tmax = models.DecimalField("sig(Tmax)", max_digits=12,decimal_places=4)
   tau  = models.DecimalField("T_E", max_digits=12,decimal_places=4)
   e_tau = models.DecimalField("sig(T_E)", max_digits=12,decimal_places=4)
   umin = models.DecimalField("u_min", max_digits=12,decimal_places=4)
   e_umin = models.DecimalField("u_min", max_digits=12,decimal_places=4)
   mass_ratio = models.DecimalField("q", max_digits=12,decimal_places=4)
   e_mass_ratio = models.DecimalField("q", max_digits=12,decimal_places=4)
   separation = models.DecimalField("s", max_digits=12,decimal_places=4)
   e_separation = models.DecimalField("s", max_digits=12,decimal_places=4)
   angle_a = models.DecimalField("alpha", max_digits=12,decimal_places=4)
   e_angle_a = models.DecimalField("sig(alpha)", max_digits=12,decimal_places=4)
   rho = models.DecimalField("rho", max_digits=12,decimal_places=4,
                             null=True, blank=True)
   e_rho = models.DecimalField("sig(rho)", max_digits=12,decimal_places=4,
                               null=True, blank=True)
   pi_e_n = models.DecimalField("Parallax EN", max_digits=12,decimal_places=4,
                                null=True, blank=True)
   e_pi_e_n = models.DecimalField("sig(Parallax EN)", max_digits=12,decimal_places=4,
                                  null=True, blank=True)
   pi_e_e = models.DecimalField("Parallax EE", max_digits=12,decimal_places=4,
                                null=True, blank=True)
   e_pi_e_e = models.DecimalField("sig(Parallax EE)", max_digits=12,decimal_places=4,
                                  null=True, blank=True)
   dsdt = models.DecimalField("Orbital motion ds/dt", max_digits=12,decimal_places=4,
                              null=True, blank=True)
   e_dsdt = models.DecimalField("sig(Orbital motion ds/dt)", max_digits=12, decimal_places=4,
                                null=True, blank=True)
   dadt = models.DecimalField("Orbital motion da/dt", max_digits=12,decimal_places=4,
                              null=True, blank=True)
   e_dadt = models.DecimalField("sig(Orbital motion da/dt)", max_digits=12,decimal_places=4,
                                null=True, blank=True)
   modeler = models.CharField("Modeler", max_length=25, blank=True, default="")
   last_updated = models.DateTimeField('date last updated')

# Reductions
class RobonetReduction(models.Model):
   def __str__(self):
      return str(self.event)+' '+str(self.lc_file)
   event = models.ForeignKey(Event)
   # location of lightcurve file
   lc_file = models.CharField(max_length=1000)
   timestamp = models.DateTimeField('date created')
   ref_image = models.CharField(max_length=1000)
   target_found = models.BooleanField(default=False)
   # DanDIA parameters
   trans_types = (
      ('S', 'shift'),
      ('R', 'rot_shift'),
      ('M', 'rot_mag_shift'),
      ('L', 'linear'),
      ('P', 'polynomial')
   )
   # CCD par
   ron = models.DecimalField(max_digits=10,decimal_places=2,default=Decimal('0.0'))
   gain = models.DecimalField(max_digits=10,decimal_places=2,default=Decimal('1.0'))
   # S1 par
   oscanx1 = models.IntegerField(default=1)
   oscanx2 = models.IntegerField(default=50)
   oscany1 = models.IntegerField(default=1)
   oscany2 = models.IntegerField(default=500)
   imagex1 = models.IntegerField(default=51)
   imagex2 = models.IntegerField(default=1000)
   imagey1 = models.IntegerField(default=1)
   imagey2 = models.IntegerField(default=1000)
   minval = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('1.0'))
   maxval = models.DecimalField(max_digits=10,decimal_places=2,default=Decimal('55000.0'))
   growsatx = models.IntegerField(default=0)
   growsaty = models.IntegerField(default=0)
   coeff2 = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('1.0e-06'))
   coeff3 = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('1.0e-12'))
   # S2 par
   sigclip = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('4.5'))
   sigfrac = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('0.5'))
   flim = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('2.0'))
   niter = models.IntegerField(default=4)
   # S3 par
   use_reflist = models.IntegerField(default=0)
   max_nimages = models.IntegerField(default=1)
   max_sky = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('5000.0'))
   min_ell = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('0.8'))
   trans_type = models.CharField(max_length=100,choices=trans_types,default='P')
   trans_auto = models.IntegerField(default=0)
   replace_cr = models.IntegerField(default=0)
   min_scale = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('0.99'))
   max_scale = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('1.01'))
   fov = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('0.1'))
   star_space = models.IntegerField(default=30)
   init_mthresh = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('1.0'))
   smooth_pro = models.IntegerField(default=2)
   smooth_fwhm = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('3.0'))
   # S4 par
   var_deg = models.IntegerField(default=1)
   det_thresh = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('2.0'))
   psf_thresh = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('8.0'))
   psf_size =  models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('8.0'))
   psf_comp_dist = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('0.7'))
   psf_comp_flux = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('0.1'))
   psf_corr_thresh = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('0.9'))
   # S5 par - same as S3
   # S6 par
   ker_rad = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('2.0'))
   lres_ker_rad = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('2.0'))
   subframes_x = models.IntegerField(default=1)
   subframes_y = models.IntegerField(default=1)
   grow = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('0.0'))
   ps_var = models.IntegerField(default=0)
   back_var = models.IntegerField(default=1)
   # niter same as S2
   diffpro = models.IntegerField(default=0)
   # S7 par - same as S6

# RoboNet observing parameters
class RobonetRequest(models.Model):
   def __str__(self):
      return str(self.event)+' updated at '+str(self.timestamp)
   event = models.ForeignKey(Event)
   possible_types = (
   ('T', 'ToO'),
   ('M', 'Monitor'),
   ('S', 'Single')
   )
   timestamp = models.DateTimeField('date last updated', blank=True)
   # observe on 0.4m telescopes?
   pfrm_on = models.BooleanField(default=False)
   # observe on 1m telescopes?
   onem_on = models.BooleanField(default=False)
   # observe on 2m telescopes?
   twom_on = models.BooleanField(default=False)
   # t_sample = cadence to use (in minutes)
   t_sample = models.DecimalField(max_digits=6,decimal_places=2)
   # exposure time (in seconds)
   exptime = models.IntegerField()
   # ToO flag
   request_type = models.CharField(max_length=20, choices=possible_types, default='M')
   # Which filter to use?
   which_filter = models.CharField(max_length=20, default='', blank=True)
   # Which instrument to use?
   which_inst = models.CharField(max_length=20, default='', blank=True)
   # Expiry date of request
   time_expire = models.DateTimeField('request expiry date', blank=True)
   # Group ID
   grp_id = models.CharField(max_length=30, default='', blank=True)
   # Track ID
   track_id = models.CharField(max_length=30, default='', blank=True)
   # Request ID
   req_id =  models.CharField(max_length=30, default='', blank=True)
   # Number of exposures requested
   n_exp = models.IntegerField(default=1)

# RoboNet event status parameters
class RobonetStatus(models.Model):
   def __str__(self):
      return str(self.event)+' updated at '+str(self.timestamp)
   event = models.ForeignKey(Event)
   possible_status = (
      ('NF', 'Not in footprint'),
      ('AC', 'active'),
      ('MO', 'monitor'),
      ('AN', 'anomaly'),
      ('EX', 'expired')
   )
   timestamp = models.DateTimeField('date last updated')
   # Event status (check, active, anomaly, rejected, expired)
   status = models.CharField(max_length=12, choices=possible_status, default='NF')
   # Comment (for internal RoboNet users)
   comment = models.CharField(max_length=200, default='--')
   # Updated by (<user>/automatic)?
   updated_by = models.CharField(max_length=25, default='--')
   # Recommended cadence (in hours)
   rec_cad = models.DecimalField("Recommended cadence (hr)", max_digits=6,decimal_places=2,
                                 null=True, blank=True)
   # Recommended exposure time (in seconds)
   rec_texp =  models.IntegerField("Recommended t_exp (sec)", null=True, blank=True)
   # Recommended number of exposures
   rec_nexp = models.IntegerField("Recommended n_exp", null=True, blank=True)
   # Recommended telescope aperture class
   rec_telclass = models.CharField("Recommended telescope class", max_length=12, default='',
                                   blank=True)

# ARTEMiS data files (.dat)
class DataFile(models.Model):
   def __str__(self):
      return str(self.event)+' '+str((self.datafile).split('/')[-1])
   event = models.ForeignKey(Event)
   datafile = models.CharField(max_length=1000)
   # Date the file was last updated
   last_upd = models.DateTimeField('date last updated')
   # Date of last observation in file
   last_obs = models.DateTimeField('date of last observation')
   # Last known magnitude
   last_mag = models.DecimalField(max_digits=10,decimal_places=2)
   # Telescope where observations were taken
   tel = models.CharField(max_length=50, blank=True, default='')
   # instrument used for the observations
   inst = models.CharField(max_length=50, blank=True, default='')
   # Filter used for the obsevations
   filt = models.CharField(max_length=50, blank=True, default='')
   # blend parameters from ARTEMiS (.align) for lightcurve calibration
   baseline = models.DecimalField(max_digits=6, decimal_places=2, default=22.0, blank=True)
   g = models.DecimalField(max_digits=6, decimal_places=2, default=0.0, blank=True)
   # Number of data points in file
   ndata =models.IntegerField()

# TAP parameters
class Tap(models.Model):
   def __str__(self):
      return str(self.event)+' priority: '+str(self.priority)
   event = models.ForeignKey(Event)
   possible_priority = (
      ('A','anomaly'),
      ('H','high'),
      ('M','medium'),
      ('L','low')
   )
   timestamp = models.DateTimeField('Date generated')
   # Priority flag for human observers (anomaly, high, medium, low)
   priority = models.CharField(max_length=12, choices=possible_priority, default='L')
   # Recommended cadence (in hours)
   tsamp = models.DecimalField(max_digits=6,decimal_places=2, default=0, blank=True)
   # Recommended exposure time (in seconds)
   texp = models.IntegerField(default=0, blank=True)
   # Recommended number of exposures
   nexp = models.IntegerField(default=0, blank=True)
   # Recommended telescope aperture class
   telclass = models.CharField(max_length=12, default='', blank=True)
   # Current I magnitude
   imag = models.DecimalField(max_digits=6,decimal_places=2, blank=True, default=22.0)
   # omega_s
   omega = models.DecimalField(max_digits=6,decimal_places=2, blank=True, null=True)
   # sig(omega_s)
   err_omega= models.DecimalField(max_digits=6,decimal_places=2, blank=True, null=True)
   # omega_s @ peak
   peak_omega = models.DecimalField(max_digits=6,decimal_places=2, blank=True, null=True)
   # target blended?
   blended = models.BooleanField(default=False)
   # visibility for the event now (in hours)
   visibility = models.DecimalField(max_digits=6,decimal_places=2, blank=True, null=True)
   # cost in minutes for the 1m network
   cost1m = models.DecimalField(max_digits=6,decimal_places=2, blank=True, null=True)
   # Survey field cadence (average number of visits per night)
   cadence = models.DecimalField(max_digits=6,decimal_places=2, blank=True, null=True)
   
# Image parameters
class Image(models.Model):
   def __str__(self):
      return str(self.event)+' Image: '+str(self.image_name)
   event = models.ForeignKey(Event)
   image_name = models.CharField(max_length=200)
   timestamp = models.DateTimeField('Date received')
   date_obs = models.DateTimeField('Date of observation')
   # Telescope where image was taken
   tel = models.CharField(max_length=50, blank=True, default='')
   # instrument used for the observation
   inst = models.CharField(max_length=50, blank=True, default='')
   # Filter used for the obsevation
   filt = models.CharField(max_length=50, blank=True, default='')
   # Group ID
   grp_id = models.CharField(max_length=30, default='', blank=True)
   # Track ID
   track_id = models.CharField(max_length=30, default='', blank=True)
   # Request ID
   req_id =  models.CharField(max_length=30, default='', blank=True)
   airmass = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
   avg_fwhm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
   avg_sky = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
   # Error in sky background counts
   avg_sigsky = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
   # Moon-target separation (in degrees)
   moon_sep = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
   # Moon phase (% of Full)
   moon_phase = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
   # Was the moon above the horizon at the time of this observation?
   moon_up = models.BooleanField(default=False)
   elongation = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
   nstars = models.IntegerField(blank=True, null=True)
   ztemp = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
   quality = models.CharField(max_length=400, blank=True, default='')
   # Which ROME field?
   rome_field = models.IntegerField(blank=True, null=True)
   # Parameters to be completed after target has been identified
   target_hjd = models.DecimalField(max_digits=20, decimal_places=5, blank=True, null=True)
   target_mag = models.DecimalField(max_digits=15, decimal_places=5, blank=True, null=True)
   target_magerr = models.DecimalField(max_digits=15, decimal_places=5, blank=True, null=True)
   target_skybg = models.DecimalField(max_digits=15, decimal_places=5, blank=True, null=True)
   target_fwhm = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)

# Survey parameters
#class Ogle_Detail(models.Model):
#   def __str__(self):
#      return str(self.event)+' updated at '+str(self.last_updated)
#   event = models.ForeignKey(Event)
#   Tmax = models.DecimalField("Tmax", max_digits=12,decimal_places=4)
#   tau = models.DecimalField("T_E", max_digits=12,decimal_places=4)
#   umin = models.DecimalField("u_min", max_digits=12,decimal_places=4)
#   last_updated = models.DateTimeField('date last updated')
#   url_link = models.URLField("OGLE event url", max_length=400)
#   
# MOA parameters
#class Moa_Detail(models.Model):
#   def __str__(self):
#      return str(self.event)+' updated at '+str(self.last_updated)
#   event = models.ForeignKey(Event)
#   Tmax = models.DecimalField("Tmax", max_digits=12,decimal_places=4)
#   tau = models.DecimalField("T_E", max_digits=12,decimal_places=4)
#   umin = models.DecimalField("u_min", max_digits=12,decimal_places=4)
#   last_updated = models.DateTimeField('date last updated')
#   url_link = models.URLField("MOA event url", max_length=400)
#   
# KMT parameters
#class Kmt_Detail(models.Model):
#   def __str__(self):
#      return str(self.event)+' updated at '+str(self.last_updated)
#   event = models.ForeignKey(Event)
#   Tmax = models.DecimalField("Tmax", max_digits=12,decimal_places=4)
#   tau = models.DecimalField("T_E", max_digits=12,decimal_places=4)
#   umin = models.DecimalField("u_min", max_digits=12,decimal_places=4)
#   last_updated = models.DateTimeField('date last updated')
#   url_link = models.URLField("KMT event url", max_length=400)
#  
## Data Files
#class Data_File(models.Model):
#   def __str__(self):
#      return str((self.datafile).split('/')[-1])
#   event = models.ForeignKey(Event)
#   datafile = models.CharField(max_length=1000)
#   last_updated = models.DateTimeField('date last updated')
#   last_magnitude = models.DecimalField(max_digits=10,decimal_places=2)
#   telescope = models.CharField(max_length=50)
#   version = models.IntegerField()
#   ndata =models.IntegerField()
#
## Logs
#class Robonet_Log(models.Model):
#   def __str__(self):
#      return str(self.image_name)
#   event = models.ForeignKey(Event)
#   image_name = models.CharField(max_length=200)
#   timestamp = models.DateTimeField('date created')
#   exptime = models.DecimalField(max_digits=10,decimal_places=2)
#   filter1 = models.CharField(max_length=12)
#   filter2 = models.CharField(max_length=12)
#   filter3 = models.CharField(max_length=12)
#   telescope = models.CharField(max_length=50)
#   instrument = models.CharField(max_length=50)
#   group_id = models.CharField(max_length=80)
#   track_id = models.CharField(max_length=80)
#   req_id = models.CharField(max_length=80)
#   airmass = models.DecimalField(max_digits=10,decimal_places=2)
#   fwhm = models.DecimalField(max_digits=10,decimal_places=2)
#   sky_bg = models.DecimalField(max_digits=10,decimal_places=2)
#   sd_bg = models.DecimalField(max_digits=10,decimal_places=2)
#   moon_sep = models.DecimalField(max_digits=10,decimal_places=2)
#   elongation = models.DecimalField(max_digits=10,decimal_places=2)
#   nstars = models.IntegerField()
#   quality = models.CharField(max_length=400)
#
## Reductions
#class Robonet_Reduction(models.Model):
#   def __str__(self):
#      return str(self.lc_file)
#   event = models.ForeignKey(Event)
#   # location of lightcurve file
#   lc_file = models.CharField(max_length=1000)
#   timestamp = models.DateTimeField('date created')
#   version = models.IntegerField()
#   ref_image = models.CharField(max_length=1000)
#   # DanDIA parameters
#   trans_types = (
#      ('S', 'shift'),
#      ('R', 'rot_shift'),
#      ('M', 'rot_mag_shift'),
#      ('L', 'linear'),
#      ('P', 'polynomial')
#   )
#   # CCD par
#   ron = models.DecimalField(max_digits=10,decimal_places=2,default=Decimal('0.0'))
#   gain = models.DecimalField(max_digits=10,decimal_places=2,default=Decimal('1.0'))
#   # S1 par
#   oscanx1 = models.IntegerField(default=1)
#   oscanx2 = models.IntegerField(default=50)
#   oscany1 = models.IntegerField(default=1)
#   oscany2 = models.IntegerField(default=500)
#   imagex1 = models.IntegerField(default=51)
#   imagex2 = models.IntegerField(default=1000)
#   imagey1 = models.IntegerField(default=1)
#   imagey2 = models.IntegerField(default=1000)
#   minval = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('1.0'))
#   maxval = models.DecimalField(max_digits=10,decimal_places=2,default=Decimal('55000.0'))
#   growsatx = models.IntegerField(default=0)
#   growsaty = models.IntegerField(default=0)
#   coeff2 = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('1.0e-06'))
#   coeff3 = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('1.0e-12'))
#   # S2 par
#   sigclip = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('4.5'))
#   sigfrac = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('0.5'))
#   flim = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('2.0'))
#   niter = models.IntegerField(default=4)
#   # S3 par
#   use_reflist = models.IntegerField(default=0)
#   max_nimages = models.IntegerField(default=1)
#   max_sky = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('5000.0'))
#   min_ell = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('0.8'))
#   trans_type = models.CharField(max_length=100,choices=trans_types,default='P')
#   trans_auto = models.IntegerField(default=0)
#   replace_cr = models.IntegerField(default=0)
#   min_scale = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('0.99'))
#   max_scale = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('1.01'))
#   fov = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('0.1'))
#   star_space = models.IntegerField(default=30)
#   init_mthresh = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('1.0'))
#   smooth_pro = models.IntegerField(default=2)
#   smooth_fwhm = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('3.0'))
#   # S4 par
#   var_deg = models.IntegerField(default=1)
#   det_thresh = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('2.0'))
#   psf_thresh = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('8.0'))
#   psf_size =  models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('8.0'))
#   psf_comp_dist = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('0.7'))
#   psf_comp_flux = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('0.1'))
#   psf_corr_thresh = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('0.9'))
#   # S5 par - same as S3
#   # S6 par
#   ker_rad = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('2.0'))
#   lres_ker_rad = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('2.0'))
#   subframes_x = models.IntegerField(default=1)
#   subframes_y = models.IntegerField(default=1)
#   grow = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('0.0'))
#   ps_var = models.IntegerField(default=0)
#   back_var = models.IntegerField(default=1)
#   # niter same as S2
#   diffpro = models.IntegerField(default=0)
#   # S7 par - same as S6
#
## RoboNet observing parameters
#class Robonet_Request(models.Model):
#   def __str__(self):
#      return str(self.event)+' updated at '+str(self.timestamp)
#   event = models.ForeignKey(Event)
#   possible_types = (
#   ('T', 'ToO'),
#   ('M', 'Monitor'),
#   ('S', 'Single')
#   )
#   timestamp = models.DateTimeField('date last updated')
#   # observe on 1m telescopes?
#   onem_on = models.BooleanField(default=False)
#   # observe on 2m telescopes?
#   twom_on = models.BooleanField(default=False)
#   # t_sample = cadence to use (in minutes)
#   t_sample = models.DecimalField(max_digits=6,decimal_places=2)
#   # exposure time (in seconds)
#   exptime = models.IntegerField()
#   # ToO flag
#   request_type = models.CharField(max_length=12, choices=possible_types, default='M')
#   # Which filter to use?
#   which_filter = models.CharField(max_length=12,default='ip')
#
## RoboNet event status parameters
#class Robonet_Status(models.Model):
#   def __str__(self):
#      return str(self.event)+' updated at '+str(self.timestamp)
#   event = models.ForeignKey(Event)
#   possible_status = (
#      ('CH', 'check'),
#      ('AC', 'active'),
#      ('AN', 'anomaly'),
#      ('RE', 'rejected'),
#      ('EX', 'expired')
#   )
#   possible_priority = (
#      ('A','anomaly'),
#      ('H','high'),
#      ('M','medium'),
#      ('L','low')
#   )
#   timestamp = models.DateTimeField('date last updated')
#   # Priority flag for human observers (anomaly, high, medium, low)
#   priority = models.CharField(max_length=12, choices=possible_priority, default='L')
#   # Event status (check, active, anomaly, rejected, expired)
#   status = models.CharField(max_length=12, choices=possible_status, default='AC')
#   # Comment (for internal RoboNet users)
#   comment = models.CharField(max_length=200, default='--')
#   # Updated by (<user>/automatic)?
#   updated_by = models.CharField(max_length=25, default='--')
#   # Priority value calculated based on parameters
#   omega = models.DecimalField(max_digits=6,decimal_places=3,default=Decimal('0.0'))
#
##class Question(models.Model):
##   def __str__(self):
##	return self.question_text
##   def was_published_recently(self):
##	return self.pub_date >= timezone.now() - datetime.timedelta(days=1)
##   question_text = models.CharField(max_length=200)
##   pub_date = models.DateTimeField('date published')
#
#class Binary_Model(models.Model):
#   def __str__(self):
#      return str(self.event)+' updated at '+str(self.last_updated)
#   event = models.ForeignKey(Event)
#   Tmax = models.DecimalField("Tmax", max_digits=12,decimal_places=4)
#   e_Tmax = models.DecimalField("sig(Tmax)", max_digits=12,decimal_places=4)
#   tau  = models.DecimalField("T_E", max_digits=12,decimal_places=4)
#   e_tau = models.DecimalField("sig(T_E)", max_digits=12,decimal_places=4)
#   umin = models.DecimalField("u_min", max_digits=12,decimal_places=4)
#   e_umin = models.DecimalField("u_min", max_digits=12,decimal_places=4)
#   mass_ratio = models.DecimalField("q", max_digits=12,decimal_places=4)
#   e_mass_ratio = models.DecimalField("q", max_digits=12,decimal_places=4)
#   separation = models.DecimalField("s", max_digits=12,decimal_places=4)
#   e_separation = models.DecimalField("s", max_digits=12,decimal_places=4)
#   rho_finite =models.DecimalField("rho", max_digits=12,decimal_places=4)
#   angle_a = models.DecimalField("alpha", max_digits=12,decimal_places=4)
#   last_updated = models.DateTimeField('date last updated')
## Data Files
#class Data_File(models.Model):
#   def __str__(self):
#      return str((self.datafile).split('/')[-1])
#   event = models.ForeignKey(Event)
#   datafile = models.CharField(max_length=1000)
#   last_updated = models.DateTimeField('date last updated')
#   last_magnitude = models.DecimalField(max_digits=10,decimal_places=2)
#   telescope = models.CharField(max_length=50)
#   version = models.IntegerField()
#   ndata =models.IntegerField()
#
## Logs
#class Robonet_Log(models.Model):
#   def __str__(self):
#      return str(self.image_name)
#   event = models.ForeignKey(Event)
#   image_name = models.CharField(max_length=200)
#   timestamp = models.DateTimeField('date created')
#   exptime = models.DecimalField(max_digits=10,decimal_places=2)
#   filter1 = models.CharField(max_length=12)
#   filter2 = models.CharField(max_length=12)
#   filter3 = models.CharField(max_length=12)
#   telescope = models.CharField(max_length=50)
#   instrument = models.CharField(max_length=50)
#   group_id = models.CharField(max_length=80)
#   track_id = models.CharField(max_length=80)
#   req_id = models.CharField(max_length=80)
#   airmass = models.DecimalField(max_digits=10,decimal_places=2)
#   fwhm = models.DecimalField(max_digits=10,decimal_places=2)
#   sky_bg = models.DecimalField(max_digits=10,decimal_places=2)
#   sd_bg = models.DecimalField(max_digits=10,decimal_places=2)
#   moon_sep = models.DecimalField(max_digits=10,decimal_places=2)
#   elongation = models.DecimalField(max_digits=10,decimal_places=2)
#   nstars = models.IntegerField()
#   quality = models.CharField(max_length=400)
#
## Reductions
#class Robonet_Reduction(models.Model):
#   def __str__(self):
#      return str(self.lc_file)
#   event = models.ForeignKey(Event)
#   # location of lightcurve file
#   lc_file = models.CharField(max_length=1000)
#   timestamp = models.DateTimeField('date created')
#   version = models.IntegerField()
#   ref_image = models.CharField(max_length=1000)
#   # DanDIA parameters
#   trans_types = (
#      ('S', 'shift'),
#      ('R', 'rot_shift'),
#      ('M', 'rot_mag_shift'),
#      ('L', 'linear'),
#      ('P', 'polynomial')
#   )
#   # CCD par
#   ron = models.DecimalField(max_digits=10,decimal_places=2,default=Decimal('0.0'))
#   gain = models.DecimalField(max_digits=10,decimal_places=2,default=Decimal('1.0'))
#   # S1 par
#   oscanx1 = models.IntegerField(default=1)
#   oscanx2 = models.IntegerField(default=50)
#   oscany1 = models.IntegerField(default=1)
#   oscany2 = models.IntegerField(default=500)
#   imagex1 = models.IntegerField(default=51)
#   imagex2 = models.IntegerField(default=1000)
#   imagey1 = models.IntegerField(default=1)
#   imagey2 = models.IntegerField(default=1000)
#   minval = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('1.0'))
#   maxval = models.DecimalField(max_digits=10,decimal_places=2,default=Decimal('55000.0'))
#   growsatx = models.IntegerField(default=0)
#   growsaty = models.IntegerField(default=0)
#   coeff2 = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('1.0e-06'))
#   coeff3 = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('1.0e-12'))
#   # S2 par
#   sigclip = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('4.5'))
#   sigfrac = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('0.5'))
#   flim = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('2.0'))
#   niter = models.IntegerField(default=4)
#   # S3 par
#   use_reflist = models.IntegerField(default=0)
#   max_nimages = models.IntegerField(default=1)
#   max_sky = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('5000.0'))
#   min_ell = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('0.8'))
#   trans_type = models.CharField(max_length=100,choices=trans_types,default='P')
#   trans_auto = models.IntegerField(default=0)
#   replace_cr = models.IntegerField(default=0)
#   min_scale = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('0.99'))
#   max_scale = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('1.01'))
#   fov = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('0.1'))
#   star_space = models.IntegerField(default=30)
#   init_mthresh = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('1.0'))
#   smooth_pro = models.IntegerField(default=2)
#   smooth_fwhm = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('3.0'))
#   # S4 par
#   var_deg = models.IntegerField(default=1)
#   det_thresh = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('2.0'))
#   psf_thresh = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('8.0'))
#   psf_size =  models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('8.0'))
#   psf_comp_dist = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('0.7'))
#   psf_comp_flux = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('0.1'))
#   psf_corr_thresh = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('0.9'))
#   # S5 par - same as S3
#   # S6 par
#   ker_rad = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('2.0'))
#   lres_ker_rad = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('2.0'))
#   subframes_x = models.IntegerField(default=1)
#   subframes_y = models.IntegerField(default=1)
#   grow = models.DecimalField(max_digits=6,decimal_places=2,default=Decimal('0.0'))
#   ps_var = models.IntegerField(default=0)
#   back_var = models.IntegerField(default=1)
#   # niter same as S2
#   diffpro = models.IntegerField(default=0)
#   # S7 par - same as S6
#
## RoboNet observing parameters
#class Robonet_Request(models.Model):
#   def __str__(self):
#      return str(self.event)+' updated at '+str(self.timestamp)
#   event = models.ForeignKey(Event)
#   possible_types = (
#   ('T', 'ToO'),
#   ('M', 'Monitor'),
#   ('S', 'Single')
#   )
#   timestamp = models.DateTimeField('date last updated')
#   # observe on 1m telescopes?
#   onem_on = models.BooleanField(default=False)
#   # observe on 2m telescopes?
#   twom_on = models.BooleanField(default=False)
#   # t_sample = cadence to use (in minutes)
#   t_sample = models.DecimalField(max_digits=6,decimal_places=2)
#   # exposure time (in seconds)
#   exptime = models.IntegerField()
#   # ToO flag
#   request_type = models.CharField(max_length=12, choices=possible_types, default='M')
#   # Which filter to use?
#   which_filter = models.CharField(max_length=12,default='ip')
#
## RoboNet event status parameters
#class Robonet_Status(models.Model):
#   def __str__(self):
#      return str(self.event)+' updated at '+str(self.timestamp)
#   event = models.ForeignKey(Event)
#   possible_status = (
#      ('CH', 'check'),
#      ('AC', 'active'),
#      ('AN', 'anomaly'),
#      ('RE', 'rejected'),
#      ('EX', 'expired')
#   )
#   possible_priority = (
#      ('A','anomaly'),
#      ('H','high'),
#      ('M','medium'),
#      ('L','low')
#   )
#   timestamp = models.DateTimeField('date last updated')
#   # Priority flag for human observers (anomaly, high, medium, low)
#   priority = models.CharField(max_length=12, choices=possible_priority, default='L')
#   # Event status (check, active, anomaly, rejected, expired)
#   status = models.CharField(max_length=12, choices=possible_status, default='AC')
#   # Comment (for internal RoboNet users)
#   comment = models.CharField(max_length=200, default='--')
#   # Updated by (<user>/automatic)?
#   updated_by = models.CharField(max_length=25, default='--')
#   # Priority value calculated based on parameters
#   omega = models.DecimalField(max_digits=6,decimal_places=3,default=Decimal('0.0'))
#class Question(models.Model):
#   def __str__(self):
#      return self.question_text
#   def was_published_recently(self):
#      return self.pub_date >= timezone.now() - datetime.timedelta(days=1)
#   question_text = models.CharField(max_length=200)
#   pub_date = models.DateTimeField('date published')

