import datetime

from django.db import models
from django.utils import timezone
from decimal import Decimal

# Known Operator (survey/follow-up)
class Operator(models.Model):
   """
   This can be the survey name or the name of the follow-up group. 
   All uppercase.

   Attributes:
   name -- The operator name 
          (string, required)
   """
   def __str__(self):
      return self.name
   name = models.CharField("Operator Name", max_length=50, default='OTHER')

# Known Telescopes
class Telescope(models.Model):
   """
   Known telescope names in the database.
   
   Attributes:
   operator -- The operator 
               (object, required) -- ForeignKey object
   name -- The telescope name 
               (string, required)
   aperture -- The telescope aperture 
               (float, optional)
   latitude -- The telescope latitude (N) in decimal degrees 
               (float, optional)
   longitude -- The telescope longitude (E) in decimal degrees 
                (float, optional)
   altitude -- The telescope altitude in meters 
               (float, optional)
   site -- The site name 
               (string, optional)
   """   
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
   """
   Known instrument names in the database for a specific telescope. 
   A single instrument can appear multiple times as it can be moved to 
   different telescopes.
   
   Attributes:
   telescope -- The telescope 
                (object, required) -- ForeignKey object
   name -- The instrument name 
                (string, required)
   pixscale -- The pixel scale of the CCD (arcsec/pix)
                (float, optional)
   """
   def __str__(self):
      return self.name
   telescope = models.ForeignKey(Telescope)
   name = models.CharField("Instrument name", max_length=50)
   pixscale = models.DecimalField("Pixel scale (arcsec/pix)", max_digits=12,
                                  decimal_places=4, null=True, blank=True)

# Known Filters
class Filter(models.Model):
   """
   Known filter names in the database for a specific instrument.
   A single filter can appear multiple times as it can exist for different 
   instruments.
   
   Attributes:
   instrument -- The instrument 
                 (object, required) -- ForeignKey object
   name -- The filter name 
                 (string, required)
   """
   def __str__(self):
      return self.name
   instrument = models.ForeignKey(Instrument)
   name = models.CharField("Filter name", max_length=50, blank=True)

# Known Fields
class Field(models.Model):
   """
   Known ROME/REA field name in the database.
   
   Keyword arguments:
   name -- The field name 
          (string, optional, default='Outside ROMEREA footprint')
   field_ra -- Field RA. 
          (string, optional, default='')
   field_dec -- Field DEC.
          (string, optional, default='')
   """
   def __str__(self):
      return self.name
   name = models.CharField("Field name", max_length=50, default='Outside ROMEREA footprint')
   field_ra = models.CharField("RA", max_length=50, default='')
   field_dec = models.CharField("Dec", max_length=50, default='')
   
# Generic Events class
class Event(models.Model):
   """
   Known events in the database.
   
   Attributes:
   field -- Field Object 
           (object, required) -- ForeignKey object
   operator -- Operator object
           (object, required) -- ForeignKey object
   ev_ra -- Event RA. (string, required)
   ev_dec -- Event DEC. (string, required)
   status -- Events status (string, optional, default='NF')
                      Available choices: 
		       'NF':'Not in footprint'
  	               'AC':'active'
	               'MO':'monitor'
  		       'AN':'anomaly'
  		       'EX':'expired'
   anomaly_rank -- The relative importance of the anomaly. -1 for no anomaly, or 
                                                       a positive decimal number. 
		                                 (float, optional, default=-1.0)
   year -- Year of discovery. (string, optional, default='')
   """
   def __str__(self):
      return "RA: "+str(self.ev_ra)+" Dec: "+str(self.ev_dec)+" ID: "+str(self.pk)
   # Which ROME field does this event belong to?
   field = models.ForeignKey(Field, related_name="ev_field_id")
   operator = models.ForeignKey(Operator, related_name="ev_operator_id")
   ev_ra = models.CharField("RA", max_length=50)
   ev_dec = models.CharField("Dec", max_length=50)
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
   # What is the relative importance of the anomaly?
   anomaly_rank = models.DecimalField("Anomaly Rank", max_digits=12, decimal_places=4, 
                                      default=Decimal('-1.0'))
   # Year the event was discovered
   year = models.CharField("Year of discovery", max_length=10, default='', blank=True)
   
# Generic Events Name class
# EventName uses two foreign keys so related_name needs to be set
class EventName(models.Model):
   """
   Known event names in the database. Multiple event names can refer to a
   single event at specific coordinates.
   
   Attributes:
   event -- Event object 
           (object, required) -- ForeignKey object
   operator -- Operator object
           (object, required) -- ForeignKey object
   name -- Event name as given by Operator
           (string, required)						     
   """
   def __str__(self):
      return "Name:"+str(self.name)+" ID: "+str(self.event_id)
   event = models.ForeignKey(Event, related_name="event_id")
   operator = models.ForeignKey(Operator, related_name="operator_id")
   name = models.CharField("Survey Event Name", max_length=50)

# Single lens parameters
class SingleModel(models.Model):
   """
   Single Lens model parameters
   in the database.
   
   Attributes:
   event  -- The event object
             (object, required) -- ForeignKey object
   Tmax -- Time of maximum magnification.
           (float, required)
   e_Tmax -- Error in Tmax 
            (float, optional, default=None)
   tau -- Event timescale (in days). 
          (float, required)
   e_tau -- error in tau. 
            (float, optional, default=None)
   umin -- Minimum impact parameter (in units of R_E). 
          (float, required)
   e_umin -- Error in umin. 
            (float, optional, default=None)
   rho -- Finite source size (in units of R_E).
          (float, optional, default=None)
   e_rho -- Error in rho.
            (float, optional, default=None)
   pi_e_n -- E,N component of the parallax vector.
             (float, optional, default=None)
   e_pi_e_n -- Error in pi_e_n.
              (float, optional, default=None)      
   pi_e_e -- E,E component of the parallax vector.
             (float, optional, default=None)
   e_pi_e_e -- Error in pi_e_e.
              (float, optional, default=None) 
   modeler -- Name of the modeler.
              (string, optional, default='')
   last_updated -- datetime of last update. (datetime, required)
        	 e.g. datetime(2016, 9, 23, 15, 26, 13, 104683, tzinfo=<UTC>)
   tap_omega -- Omega value to be updated by TAP. 
              (float, optional, default=None)
   chi_sq -- Chi square of the fit
              (float, optional, default=None)
   """
   def __str__(self):
      return str(self.event)+' updated at '+str(self.last_updated)
   event = models.ForeignKey(Event)
   Tmax = models.DecimalField("Tmax", max_digits=12,decimal_places=4)
   e_Tmax = models.DecimalField("sig(Tmax)", max_digits=12,decimal_places=4,
                                     null=True, blank=True)
   tau = models.DecimalField("T_E", max_digits=12,decimal_places=4)
   e_tau = models.DecimalField("sig(T_E)", max_digits=12,decimal_places=4,
                                     null=True, blank=True)
   umin = models.DecimalField("u_min", max_digits=12,decimal_places=4)
   e_umin = models.DecimalField("sig(u_min)", max_digits=12,decimal_places=4,
                                     null=True, blank=True)
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
   tap_omega = models.DecimalField("TAP Omega", max_digits=12,decimal_places=4,
                                    null=True, blank=True)
   chi_sq = models.DecimalField("Chi sq", max_digits=12,decimal_places=4,
                                    null=True, blank=True)
   
# Binary Lens parameters
class BinaryModel(models.Model):
   """
   Known Binary Lens model parameters
   in the database.
   
   Attributes:
   event  -- The event object
             (object, required) -- ForeignKey object
   Tmax -- Time of maximum magnification.
           (float, required)
   e_Tmax -- Trror in Tmax 
            (float, optional, default=None)
   tau -- Tvent timescale (in days). 
          (float, required)
   e_tau -- Trror in tau. 
           (float, optional, default=None)
   umin -- Minimum impact parameter (in units of R_E). 
          (float, required)
   e_umin -- Error in umin. 
            (float, optional, default=None)
   mass_ratio -- Mass ratio q between the two lens components.
                 (float, required)
   e_mass_ratio -- Error in q
                  (float, optional, default=None)
   separation -- Separation between the two lens components
                 (in units of R_E)
		 (float, required)
   e_separation -- Error in separation
                  (float, optional, default=None)
   angle_a -- Trajectory angle with respect to the binary axis.
              (float, required)
   e_angle_a -- Error in trajectory angle.
              (float, optional, default=None)
   dsdt -- Orbital motion ds/dt
           (float, optional, default=None)
   e_dsdt -- Error in ds/dt
           (float, optional, default=None)
   dadt -- Orbinatl motion da/dt
           (float, optional, default=None)
   e_dadt -- Error in da/dt
           (float, optional, default=None)
   rho -- Finite source size (in units of R_E).
          (float, optional, default=None)
   e_rho -- error in rho.
            (float, optional, default=None)
   pi_e_n -- E,N component of the parallax vector.
             (float, optional, default=None)
   e_pi_e_n -- error in pi_e_n.
              (float, optional, default=None)      
   pi_e_e -- E,E component of the parallax vector.
             (float, optional, default=None)
   e_pi_e_e -- error in pi_e_e.
              (float, optional, default=None) 
   modeler -- Name of the modeler.
              (string, optional, default='')
   last_updated -- datetime of last update. (datetime, required)
        	 e.g. datetime(2016, 9, 23, 15, 26, 13, 104683, tzinfo=<UTC>)
   chi_sq -- Chi square of the fit
              (float, optional, default=None)
   """
   def __str__(self):
      return str(self.event)+' updated at '+str(self.last_updated)
   event = models.ForeignKey(Event)
   Tmax = models.DecimalField("Tmax", max_digits=12,decimal_places=4)
   e_Tmax = models.DecimalField("sig(Tmax)", max_digits=12,decimal_places=4,
                                     null=True, blank=True)
   tau  = models.DecimalField("T_E", max_digits=12,decimal_places=4)
   e_tau = models.DecimalField("sig(T_E)", max_digits=12,decimal_places=4,
                                     null=True, blank=True)
   umin = models.DecimalField("u_min", max_digits=12,decimal_places=4)
   e_umin = models.DecimalField("u_min", max_digits=12,decimal_places=4,
                                     null=True, blank=True)
   mass_ratio = models.DecimalField("q", max_digits=12,decimal_places=4)
   e_mass_ratio = models.DecimalField("q", max_digits=12,decimal_places=4,
                                     null=True, blank=True)
   separation = models.DecimalField("s", max_digits=12,decimal_places=4)
   e_separation = models.DecimalField("s", max_digits=12,decimal_places=4,
                                     null=True, blank=True)
   angle_a = models.DecimalField("alpha", max_digits=12,decimal_places=4)
   e_angle_a = models.DecimalField("sig(alpha)", max_digits=12,decimal_places=4,
                                     null=True, blank=True)
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
   chi_sq = models.DecimalField("Chi sq", max_digits=12,decimal_places=4,
                                    null=True, blank=True)

# Reductions
class EventReduction(models.Model):
   """
   Known light curve location for a specific event and pipeline event reduction parameters 
   in the database. Also stores the reference frame name and DanDIA parameters 
   used to generate the lightcurve.
   
   Attributes:
   event  -- The event object. 
                 (object, required) -- ForeignKey object.
   lc_file -- The lightcurve file. 
             (string, required)
   timestamp -- The date the lightcurve file was created. 
                (datetime, required)
                 e.g. datetime(2016, 9, 23, 15, 26, 13, 104683, tzinfo=<UTC>)
   target_found -- Has the target been identified by the pipeline? 
                  (boolean, required, default=False)
   ref_image -- Reference image used. 
                (string, required)
   -+-+- DanDIA parameters -+-+-
   ron -- CCD readout noise (in ADU) 
          (float, optional, default=0.0)
   gain -- CCD gain. (e-/ADU) 
           (float, optional, default=1.0)
   oscanx1 -- Overscan strip coordinate x1 
              (integer, optional, default=1)
   oscanx2 -- Overscan strip coordinate x2 
              (integer, optional, default=50)
   oscany1 -- Overscan strip coordinate y1 
              (integer, optional, default=1)
   oscany2 -- Overscan strip coordinate y2 
              (integer, optional, default=500)
   imagex1 -- Image region coordinate x1 
              (integer, optional, default=51)
   imagex2 -- Image region coordinate x2 
              (integer, optional, default=1000)
   imagey1 -- Image region coordinate y1 
              (integer, optional, default=1)
   imagey2 -- Image region coordinate y2 
              (integer, optional, default=1000)
   minval -- Minimum useful pixel value in a raw image (ADU). 
            (float, optional, default=1.0)
   maxval -- maximum useful pixel value in a raw image (ADU). 
            (float, optional, default=55000.0)
   growsatx -- Half box size in the x direction (pix) to be used for growing 
               saturated bad pixels in the bad pixel mask for each science image.
	       This parameter should be non-negative.
	       (integer, optional, default=0)
   growsaty -- Half box size in the y direction (pix) to be used for growing 
               saturated bad pixels in the bad pixel mask for each science image.
	       This parameter should be non-negative.
	       (integer, optional, default=0)
   coeff2 -- Coefficient a1 in the linearisation equation: 
             Xnew = X + a1*X^2 + a2*X^3
             where X represents the image counts after bias level and bias pattern
	     correction.
	     (float, optional, default=1.0e-06)
   coeff3  -- Coefficient a1 in the linearisation equation: 
              Xnew = X + a1*X^2 + a2*X^3
              where X represents the image counts after bias level and bias pattern
	      correction.
	     (float, optional, default=1.0e-12)
   sigclip -- Threshold in units of sigma for cosmic ray detection on the Laplacian
              image. This parameter should be positive.
	      (float, optional, default=4.5)
   sigfrac -- Fraction of "sigclip" to be used as a threshold for cosmic ray growth.
              This parameter should be positive.
	      (float, optional, default=0.5)
   flim --.Minimum contrast between the Laplacian image and the fine structure image.
           This parameter should be positive.
	   (float, optional, default=2.0)
   niter -- Maximum number of iterations to perform.
            This parameter should be positive.
            (integer, optional, default=4)
   use_reflist -- Use images in reflist.<filt>.txt?
            (integer, optional, default=0 (No))
   max_nimages -- Maximum number of images to combine for reference.
            (integer, optional, default=1)
   max_sky -- Maximum acceptable value for sky background.
            (float, optional, default=5000.0)
   min_ell -- Minimum PSF ellipticity for image to be used in reference.
            (float, optional, default=0.8)
   trans_type -- Type of coordinate transformation to fit when fitting a coordinate
                 transformation between two images. 
		 Options:["shift"=General pixel shift, "rot_shift"=Rotation and 
		 general pixel shift, "rot_mag_shift"=Rotation magnification 
		 and general pixel shift, "linear"=Linear, "polynomial"=Polynomial]
		 (string, optional, default='polynomial')
   trans_auto -- Use automatic determination of the coordinate transformation type
                 when fitting a coordinate transformation between two images? 
		 (integer, optional, default=0 (No))
   replace_cr -- Replace cosmic ray pixels? (integer, optional, default=0 (No))
   min_scale -- Minimum possible transformation scale factor (magnification) between
                any two images.
                (float, optional, default=0.99)
   max_scale -- Maximum possible transformation scale factor (magnification) between
                any two images.
                (float, optional, default=1.01)
   fov -- Field of view of the CCD camera (deg).
                (float, optional, default=0.1)
   star_space -- Average spacing (pix) between stars.
                (integer, optional, default=30) 
   init_mthresh -- Initial distance threshold (pix) to reject false star matches.
                (float, optional, default=1.0)
   smooth_pro -- Smooth image? (integer, optional, default=2)
   smooth_fwhm -- Amount of smoothing to perform (float, optional, default=3.0)
   var_deg -- Polynomial degree of the spatial variation of the model used to 
              represent the image PSF.
              (0=Constant, 1=Linear, 2=Quadratic, 3=Cubic)
	      (integer, optional, default=1)
   det_thresh -- Detection threshold used to detect stars in units of image sky
                 sigma. 
                (float, optional, default=2.0)
   psf_thresh -- Detection threshold used to detect candidate PSF stars in units
                 of image sky sigma.
                 (float, optional, default=8.0)
   psf_size --  Size of the model PSF stamp in units of FWHM.
               (float, optional, default=8.0)
   psf_comp_dist -- Any star within a distance "0.5*psf_comp_dist*psf_size",
                    in units of FWHM, of another star is considered to be a companion
		    of that star for PSF star selection.
		    (float, optional, default=0.7)
   psf_comp_flux -- Maximum flux ratio that any companion star may have for a star to
                    be considered a PSF star.
		    (float, optional, default=0.1)
   psf_corr_thres -- Minimum correlation coefficient of a star with the image PSF 
                     model in order to be considered a PSF star.
		     (float, optional, default=0.9)
   ker_rad -- Radius of the kernel pixel array in units of image FWHM.
             (float, optional, default=2.0)
   lres_ker_rad -- Threshold radius of the kernel pixel array, in units of image FWHM,
                   beyond which kernel pixels are of lower resolution.
		   (float, optional, default=2.0)
   subframes_x -- Number of subdivisions in the x direction used in defining the grid 
                  of kernel solutions. 
		  (integer, optional, default=1)
   subframes_y -- Number of subdivisions in the y direction used in defining the grid
                  of kernel solutions. 
		  (integer, optional, default=1)
   grow -- Amount of overlap between the image regions used for the kernel solutions.
                  (float, optional, default = 0.0)
   ps_var -- Use spatially variable photometric scale factor? 
                  (integer, optional, default=0 (No))
   back_var -- Use spatially variable differential background. 
                  (integer, optional, default=1 (Yes))
   diffpro -- Switch for the method of difference image creation.
                  (integer, optional, default=0 (No))
   """
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

# Observing request parameters
class ObsRequest(models.Model):
   """
   Known observing requests in the database.
   
   Attributes:
   field -- The field object. 
                 (object, required) -- ForeignKey object
   t_sample -- Sampling interval to use. (in minutes) 
              (float, required)
   exptime -- Exposure time to use. (in seconds) (integer, required) 
   timestamp -- The request submission time.
                (datetime, optional, default=timezone.now())
        	e.g. datetime(2016, 9, 23, 15, 26, 13, 104683, tzinfo=<UTC>)
   time_expire -- When the request expires.
                  (datetime, optional, default=timezone.now()+24 hours)
   request_status -- Status of obs request (ACtive or EXpired)
                   (string, optional, default='AC')
   pfrm_on -- Observe on 0.4m network?
              (Boolean, optional, default=False)
   onem_on -- Observe on 1m network? 
              (boolean, optional, default=False)
   twom_on -- Observe on 2m network? 
              (boolean, optional, default=False)
   request_type -- Observation request class 
                   (string, optional, default='L')
                    'A':'REA High - 20 min cadence',
		    'M':'REA Low - 60 min cadence', 
		    'L':'ROME Standard - every 7 hours'
   which_filter -- Filter identifier string. 
                   (string, optional, default='')
   which_inst -- Instrument identifier string. 
                   (string, optional, default='')
   grp_id -- Group ID
             (string, optional, default='')
   track_id -- Track ID
              (string, optional, default='')
   req_id -- Request ID  
            (string, optional, default='')
   n_exp -- Number of exposures to obtain.
            (integer, optional, default=1)
   """
   def __str__(self):
      return str(self.field)+' updated at '+str(self.timestamp)
   field = models.ForeignKey(Field)
   possible_types = (
   ('A', 'REA High - 20 min cadence'),
   ('M', 'REA Low - 60 min cadence'),
   ('L', 'ROME Standard - every 7 hours')
   )
   status_choice = (
   ('AC', 'ACTIVE'),
   ('EX', 'EXPIRED'),
   ('CN', 'CANCELLED')
   )
   timestamp = models.DateTimeField('request submit date', blank=True)
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
   request_type = models.CharField(max_length=40, choices=possible_types, default='L')
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
   req_id =  models.CharField(max_length=300, default='', blank=True)
   # Number of exposures requested
   n_exp = models.IntegerField(default=1)
   request_status = models.CharField(max_length=40, choices=status_choice, default='AC')

# Event status parameters
class EventStatus(models.Model):
   """
   Known event status in the database.
   
   Attributes:
   event -- The event object. 
                (object, required) -- ForeignKey object
   timestamp -- The request submission time.
                (datetime, optional, default=timezone.now())
        	e.g. datetime(2016, 9, 23, 15, 26, 13, 104683, tzinfo=<UTC>)
   status -- Event status.
             (NF:not in footprint, AC:active, MO:monitor, AN:anomaly, EX:expired)
             (string, optional, default='NF')
   comment -- Comment field. 
             (string, optional, default='')
   updated_by -- Updated by which user? 
                 (string, optional, default='')
   rec_cad -- Recommended cadence (in hours).
              (float, optional, default=0)
   rec_texp -- Recommended exposure time (in seconds).
              (float, optional, default=0)
   rec_nexp -- Recommended number of exposures.
              (integer, optional, default=0)
   rec_telclass -- Recommended telescope class.
              (string, optional, default='1m')
   """
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
   rec_telclass = models.CharField("Recommended telescope class", max_length=12, default='1m',
                                   blank=True)

# ARTEMiS data files (.dat)
class DataFile(models.Model):
   """
   All ARTEMiS data files known to the database.
   Uses the .dat files rsynced from ARTEMiS.
   
   Attributes:
   event -- The event object. 
                (object, required) -- ForeignKey object
   datafile -- Full path to the data file. 
              (string, required)
   last_upd -- Datetime of last update. (datetime, required, 
                                         default=timezone.now())
   last_obs -- Datetime of last observation. (datetime, required, 
                                         default=timezone.now())
   last_mag -- Last recorded magnitude. 
               (float, required)
   tel -- Telescope identifier. 
         (string, required)
   inst -- Instrument used for the observations.
           (string, optional, default='')
   filt -- Filter used for the observations.
           (string, optional, default='')
   baseline -- I0 blend parameter from ARTEMiS .align file.
               (float, optional, default=22.0)
   g -- g blend parameter from ARTEMiS .align file.
        (float, optional, default=0.0)
   ndata -- Number of data points. 
         (integer, required)
   """
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
   """
   Known TAP entries in the database.
      
   Keyword arguments:
   event -- The event object. 
                (object, required) --ForeignKey object
   timestamp -- The TAP submission time.
                (datetime, optional, default=timezone.now())
        	e.g. datetime(2016, 9, 23, 15, 26, 13, 104683, tzinfo=<UTC>)
   priority -- Priority flag for human observers.
	       (string, optional, default='N')
	        'A':'REA High',
		'L':'REA Low',
		'B':'REA Post-High'
		'N':'None'
   tsamp -- Recommended cadence (in hours).
            (float, optional, default=0)
   texp -- Recommended exposure time (in seconds).
           (integer, optional, default=0)
   nexp -- Recommended number of exposures.
           (integer, optional, default=1)
   telclass --  Recommended telescope aperture class.
                (string, optional, default='1m')
   imag -- Current I magnitude.
           (float, optional, default=22.0)
   omega -- omega_s.
            (float, optional, default=None)
   err_omega -- sig(omega_s).
                (float, optional, default=None)
   peak_omega -- omega_s at peak
                 (float, optional, default=None)
   blended -- target blended?
             (boolean, optional, default=False)
   visibility -- Current target visibility (in hours)
                 (float, optional, default=None)
   cost1m -- Estimated observational cost per night for the 1m network (in minutes)
                 (float, optional, default=None)
   passband -- Passband for which the priority function has been evaluated
                 (string, optional, default='SDSS-i')
   ipp -- Inter Proposal Priority Value
          (float, optional, default='1.0')
   """
   def __str__(self):
      return str(self.event)+' priority: '+str(self.priority)
   event = models.ForeignKey(Event)
   possible_priority = (
      ('A','REA High'),
      ('L','REA Low'),
      ('B','REA Post-High'),
      ('N','None')
   )
   timestamp = models.DateTimeField('Date generated')
   # Priority flag for human observers (rea high, rea low, rea post-high, none)
   priority = models.CharField(max_length=12, choices=possible_priority, default='N')
   # Recommended cadence (in hours): Can only take two possible values : 60 or 20 min
   tsamp = models.DecimalField(max_digits=6,decimal_places=2, default=0, blank=True)
   # Recommended exposure time (in seconds)
   texp = models.IntegerField(default=0, blank=True)
   # Recommended number of exposures
   nexp = models.IntegerField(default=1, blank=True)
   # Recommended telescope aperture class
   telclass = models.CharField(max_length=12, default='1m', blank=True)
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
   # Passband for which the priority function has been evaluated
   passband = models.CharField(max_length=12, default='SDSS-i', blank=True)
   # Inter Proposal Priority value
   ipp = models.DecimalField(max_digits=10,decimal_places=3, blank=True, default=1.0)
   
# Image parameters
class Image(models.Model):
   """
   Images known to the database. 
   
   Attributes:
   field -- The field object. 
                (object, required) -- ForeignKey object
   image_name -- The name of the image.
                (string, required)
   date_obs -- The date of observation.
                (datetime, required)
        	e.g. datetime(2016, 9, 23, 15, 26, 13, 104683, tzinfo=<UTC>)
   timestamp -- The time the image was written/updated in the database.
                (datetime, optional, default=timezone.now())
        	e.g. datetime(2016, 9, 23, 15, 26, 13, 104683, tzinfo=<UTC>)
   tel -- Telescope where the image was taken.
         (string, optional, default='')
   inst -- Instrument used for the observation.
           (string, optional, default='')
   filt -- Filter used for the observation.
           (string, optional, default='')
   grp_id -- Group ID.
            (string, optional, default='')
   track_id -- Tracking ID.
              (string, optional, default='')
   req_id -- Observing Request ID.
             (string, optional, default='')
   airmass -- Airmass of observation.
             (float, optional, default=None)
   avg_fwhm -- Average FWHM of stars in image.
              (float, optional, default=None)
   avg_sky -- Average sky background counts in image.
             (float, optional, default=None)  
   avg_sigsky -- Error in sky background counts.
                (float, optional, default=None)  
   moon_sep -- Moon-target separation (in degrees).
              (float, optional, default=None)  
   moon_phase -- Moon phase (% of Full).
                 (float, optional, default=None)  
   moon_up -- Was the moon above the horizon at the time of this observation?
             (boolean, optional, default=False)
   elongation -- Detected object elongation.
                 (float, optional, default=None)
   nstars -- Number of stars detected.
             (integer, optional, default=None)	     
   ztemp -- ztemp parameter.
                 (float, optional, default=None)   
   quality -- Image quality description.
                 (string, optional, default='')
   """
   def __str__(self):
      return str(self.field)+' Image: '+str(self.image_name)
   field = models.ForeignKey(Field)
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
