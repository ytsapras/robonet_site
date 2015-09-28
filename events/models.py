import datetime

from django.db import models
from django.utils import timezone
from decimal import Decimal

# Generic Events class
class Event(models.Model):
   def __str__(self):
      #if self.ev_name_ogle != "...":
      #   return str(self.ev_name_ogle)
      #elif self.ev_name_moa != "...":
      #   return str(self.ev_name_moa)
      #elif self.ev_name_kmt != "...":
      #   return str(self.ev_name_kmt)
      #else:
      #   return "Unknown Event"
      return str(self.id)
   ev_name_ogle = models.CharField("OGLE id", max_length=200, default="...")
   ev_name_moa = models.CharField("MOA id", max_length=200, default="...")
   ev_name_kmt = models.CharField("KMT id", max_length=200, default="...")
   ev_ra = models.CharField("RA", max_length=50)
   ev_dec = models.CharField("Dec", max_length=50)
   # does the event have a bright neighbour?
   bright_neighbour = models.BooleanField("Bright neighbour", default=False)

# Survey parameters
class Ogle_Detail(models.Model):
   def __str__(self):
      return str(self.event)+' updated at '+str(self.last_updated)
   event = models.ForeignKey(Event)
   Tmax = models.DecimalField("Tmax", max_digits=12,decimal_places=4)
   tau = models.DecimalField("T_E", max_digits=12,decimal_places=4)
   umin = models.DecimalField("u_min", max_digits=12,decimal_places=4)
   last_updated = models.DateTimeField('date last updated')
   url_link = models.URLField("OGLE event url", max_length=400)
   
# MOA parameters
class Moa_Detail(models.Model):
   def __str__(self):
      return str(self.event)+' updated at '+str(self.last_updated)
   event = models.ForeignKey(Event)
   Tmax = models.DecimalField("Tmax", max_digits=12,decimal_places=4)
   tau = models.DecimalField("T_E", max_digits=12,decimal_places=4)
   umin = models.DecimalField("u_min", max_digits=12,decimal_places=4)
   last_updated = models.DateTimeField('date last updated')
   url_link = models.URLField("MOA event url", max_length=400)
   
# KMT parameters
class Kmt_Detail(models.Model):
   def __str__(self):
      return str(self.event)+' updated at '+str(self.last_updated)
   event = models.ForeignKey(Event)
   Tmax = models.DecimalField("Tmax", max_digits=12,decimal_places=4)
   tau = models.DecimalField("T_E", max_digits=12,decimal_places=4)
   umin = models.DecimalField("u_min", max_digits=12,decimal_places=4)
   last_updated = models.DateTimeField('date last updated')
   url_link = models.URLField("KMT event url", max_length=400)
   
# Single lens parameters
class Single_Model(models.Model):
   def __str__(self):
      return str(self.event)+' updated at '+str(self.last_updated)
   event = models.ForeignKey(Event)
   Tmax = models.DecimalField("Tmax", max_digits=12,decimal_places=4)
   e_Tmax = models.DecimalField("sig(Tmax)", max_digits=12,decimal_places=4)
   tau = models.DecimalField("T_E", max_digits=12,decimal_places=4)
   e_tau = models.DecimalField("sig(T_E)", max_digits=12,decimal_places=4)
   umin = models.DecimalField("u_min", max_digits=12,decimal_places=4)
   e_umin = models.DecimalField("sig(u_min)", max_digits=12,decimal_places=4)
   last_updated = models.DateTimeField('date last updated')
   
# Binary Lens parameters
class Binary_Model(models.Model):
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
   rho_finite =models.DecimalField("rho", max_digits=12,decimal_places=4)
   angle_a = models.DecimalField("alpha", max_digits=12,decimal_places=4)
   last_updated = models.DateTimeField('date last updated')

# Data Files
class Data_File(models.Model):
   def __str__(self):
      return str((self.datafile).split('/')[-1])
   event = models.ForeignKey(Event)
   datafile = models.CharField(max_length=1000)
   last_updated = models.DateTimeField('date last updated')
   last_magnitude = models.DecimalField(max_digits=10,decimal_places=2)
   telescope = models.CharField(max_length=50)
   version = models.IntegerField()
   ndata =models.IntegerField()
   
# Logs
class Robonet_Log(models.Model):
   def __str__(self):
      return str(self.image_name)
   event = models.ForeignKey(Event)
   image_name = models.CharField(max_length=200)
   timestamp = models.DateTimeField('date created')
   exptime = models.DecimalField(max_digits=10,decimal_places=2)
   filter1 = models.CharField(max_length=12)
   filter2 = models.CharField(max_length=12)
   filter3 = models.CharField(max_length=12)
   telescope = models.CharField(max_length=50)
   instrument = models.CharField(max_length=50)
   group_id = models.CharField(max_length=80)
   track_id = models.CharField(max_length=80)
   req_id = models.CharField(max_length=80)
   airmass = models.DecimalField(max_digits=10,decimal_places=2)
   fwhm = models.DecimalField(max_digits=10,decimal_places=2)
   sky_bg = models.DecimalField(max_digits=10,decimal_places=2)
   sd_bg = models.DecimalField(max_digits=10,decimal_places=2)
   moon_sep = models.DecimalField(max_digits=10,decimal_places=2)
   elongation = models.DecimalField(max_digits=10,decimal_places=2)
   nstars = models.IntegerField()
   quality = models.CharField(max_length=400)

# Reductions
class Robonet_Reduction(models.Model):
   def __str__(self):
      return str(self.lc_file)
   event = models.ForeignKey(Event)
   # location of lightcurve file
   lc_file = models.CharField(max_length=1000)
   timestamp = models.DateTimeField('date created')
   version = models.IntegerField()
   ref_image = models.CharField(max_length=1000)
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
class Robonet_Request(models.Model):
   def __str__(self):
      return str(self.event)+' updated at '+str(self.timestamp)
   event = models.ForeignKey(Event)
   possible_types = ( 
   ('T', 'ToO'),
   ('M', 'Monitor'),
   ('S', 'Single')
   )
   timestamp = models.DateTimeField('date last updated')
   # observe on 1m telescopes?
   onem_on = models.BooleanField(default=False)
   # observe on 2m telescopes?
   twom_on = models.BooleanField(default=False)
   # t_sample = cadence to use (in minutes)
   t_sample = models.DecimalField(max_digits=6,decimal_places=2)
   # exposure time (in seconds)
   exptime = models.IntegerField()
   # ToO flag
   request_type = models.CharField(max_length=12, choices=possible_types, default='M')
   # Which filter to use?
   which_filter = models.CharField(max_length=12,default='ip')

# RoboNet observing parameters
class Robonet_Status(models.Model):
   def __str__(self):
      return str(self.event)+' updated at '+str(self.timestamp)
   event = models.ForeignKey(Event)
   possible_status = ( 
      ('CH', 'check'),
      ('AC', 'active'),
      ('AN', 'anomaly'),
      ('RE', 'rejected'),
      ('EX', 'expired')
   )
   possible_priority = (
      ('A','anomaly'),
      ('H','high'),
      ('M','medium'),
      ('L','low')
   )
   timestamp = models.DateTimeField('date last updated')
   # Priority flag for human observers (anomaly, high, medium, low)
   priority = models.CharField(max_length=12, choices=possible_priority, default='L')
   # Event status (check, active, anomaly, rejected, expired)
   status = models.CharField(max_length=12, choices=possible_status, default='AC')
   # Comment (for internal RoboNet users)
   comment = models.CharField(max_length=200, default='--')
   # Updated by (<user>/automatic)?
   updated_by = models.CharField(max_length=25, default='--')
   
#class Question(models.Model):
#   def __str__(self):
#      return self.question_text
#   def was_published_recently(self):
#      return self.pub_date >= timezone.now() - datetime.timedelta(days=1)
#   question_text = models.CharField(max_length=200)
#   pub_date = models.DateTimeField('date published')

