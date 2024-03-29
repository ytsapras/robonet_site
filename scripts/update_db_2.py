#################################################################################
# Collection of routines to update the RoboNet database tables
# Keywords match the class model fields in ../robonet_site/events/models.py
#
# Written by Yiannis Tsapras Oct 2016
# Last update:
#################################################################################

# Import dependencies
import os
import sys
from . import local_conf
robonet_site = local_conf.get_conf('robonet_site')
sys.path.append(robonet_site)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'robonet_site.settings')
from django.core import management
from django.conf import settings
from django.utils import timezone
from django import setup
from datetime import datetime, timedelta
from decimal import InvalidOperation
setup()

from events.models import Field, Operator, Telescope, Instrument, Filter, Event, EventName, SingleModel, BinaryModel
from events.models import EventReduction, ObsRequest, EventStatus, DataFile, Tap, TapLima, Image, SubObsRequest
from . import api_tools, query_db, rea_obs
import pytz

##################################################################################
def add_operator(operator_name):
   """
   Adds a new operator name in the database.
   This can be the survey name or the name of the follow-up group.

   Keyword arguments:
   operator_name -- The operator name
                    (string, required)
   """
   # Make it upper-case - all Operators are upper case
   operator_name = operator_name.upper()
   new_operator = Operator.objects.get_or_create(name=operator_name)
   if new_operator[-1] == False:
      successful = False
   else:
      successful = True
   return successful

##################################################################################
def add_telescope(operator, telescope_name, aperture=0.0, latitude=0.0,
                  longitude=0.0, altitude=0.0, site=""):
    """
    Adds a new telescope name in the database.

    Keyword arguments:
    operator -- The name of the operator
               (string, required)
    telescope_name -- The telescope name
                     (string, required)
    aperture -- The telescope aperture
              (float, optional, default=0.0)
    latitude -- The telescope latitude (N) in decimal degrees
               (float, optional, default=0.0)
    longitude -- The telescope longitude (E) in decimal degrees
                (float, optional, default=0.0)
    altitude -- The telescope altitude in meters
               (float, optional, default=0.0)
    site -- The site name
               (string, optional, default="")
    """
    known_telescope = Telescope.objects.filter(name=telescope_name).exists()
    # If the telescope already exists there's no need to add it
    if known_telescope == True:
        print('An entry for this telescope already exists.')
        successful = False
    else:
        # Check that requested operator name is a known operator
        unknown_operator = False
        try:
            operator_id = Operator.objects.get(name=operator).id
            operator_obj = Operator.objects.get(id=operator_id)
        except:
            print('Event not added: Unknown Operator: %s' % operator)
            unknown_operator = True
    if unknown_operator==False:
        add_new = Telescope(operator=operator_obj, name=telescope_name,
                             aperture=aperture, latitude=latitude,
                             longitude=longitude, altitude=altitude,site=site)
        add_new.save()
        successful = True
    else:
        successful = False
    return successful

##################################################################################
def add_instrument(telescope, instrument_name, pixscale=0.0):
   """
   Adds a new instrument name in the database for a specific telescope.
   A single instrument can appear multiple times as it can be moved to
   different telescopes.

   Keyword arguments:
   telescope -- The telescope
                (object, required) -- ForeignKey object
   instrument_name -- The instrument name
                (string, required)
   pixscale -- The pixel scale of the CCD (arcsec/pix)
                (float, optional)
   """
   # Is this a known instrument on this telescope?
   known_tel_inst = Instrument.objects.filter(telescope=telescope).filter(name=instrument_name).exists()
   # If it is a known instrument for this telescope do not try to add it
   if (known_tel_inst==True):
      successful = False
   # If it is a new unknown instrument try to add it
   if (known_tel_inst==False):
      try:
         add_new = Instrument(telescope=telescope, name=instrument_name,
                              pixscale=pixscale)
         add_new.save()
         successful = True
      except:
         successful = False
   return successful

##################################################################################
def add_filter(instrument, filter_name):
   """
   Adds a new filter name in the database for a specific instrument.
   A single filter can appear multiple times as it can exist for different
   instruments.

   Keyword arguments:
   instrument -- The instrument
                 (object, required) -- ForeignKey object
   filter_name -- The filter name
                 (string, required)
   """
   # Is this a known filter on this instrument?
   known_inst_filt = Filter.objects.filter(instrument=instrument).filter(name=filter_name).exists()
   # If it is a known filter for this instrument do not try to add it
   if (known_inst_filt==True):
      successful = False
   # If it is a new unknown filter try to add it
   if (known_inst_filt==False):
      try:
         add_new = Filter(instrument=instrument, name=filter_name)
         add_new.save()
         successful = True
      except:
         successful = False
   return successful

##################################################################################
def add_field(field_name = 'Outside ROMEREA footprint', field_ra = '', field_dec = ''):
   """
   Adds a new field name in the database.

   Keyword arguments:
   field_name -- The field name
          (string, optional, default='Outside ROMEREA footprint')
   field_ra -- Field RA.
        	   e.g. "17:54:33.58"
          (string, optional, default='')
   field_dec -- Field DEC.
        	   e.g. "-30:31:02.02"
          (string, optional, default='')
   """
   new_field = Field.objects.filter(name=field_name)
   if len(new_field) == 1:
      successful = False
   else:
      add_new = Field(name=field_name, field_ra=field_ra, field_dec=field_dec)
      add_new.save()
      successful = True
   return successful

##################################################################################
def add_event(field_name, operator_name, ev_ra, ev_dec, status = 'NF',
              anomaly_rank = -1.0, year = str(datetime.now().year),
              ra_deg = None, dec_deg = None, ibase = None):
    """Add a new event to the database. Will return successful = True/False
    and either the coordinates of the object itself or those of the closest
    matching object.

    Keyword arguments:
    field_name -- Field name (string, required)
    operator_name -- Operator name (string, required)
    ev_ra -- Event RA. (string, required) e.g. "17:54:33.58"
    ev_dec -- Event DEC. (string, required) e.g. "-30:31:02.02"
    status -- Events status (string, optional, default='NF')
                                Available choices:
                                'NF':'Not in footprint'
                                'AC':'active'
                                'MO':'monitor'
                                'AN':'anomaly'
                                'EX':'expired'
    anomaly_rank -- The relative importance of the anomaly. -1 for no anomaly,
                    or a positive decimal number.
                    (float, optional, default=-1.0)
    year -- Year of discovery. (string, optional, default=<current year>)
    ra_deg -- Event RA (decimal degrees, optional)
    dec_deg -- Event Dec (decimal degrees, optional)
    ibase -- Event baseline magnitude (mag, optional)
    """

    # Check that requested field name is a known field
    unknown_field = False

    try:
        field_id = Field.objects.get(name=field_name).id
        field = Field.objects.get(id=field_id)

    except:
        print('Event not added: Unknown Field: %s' % field_name)
        unknown_field = True

    # Check that requested operator name is a known operator
    unknown_operator = False

    try:
        operator_id = Operator.objects.get(name=operator_name).id
        operator = Operator.objects.get(id=operator_id)

    except:
        print('Event not added: Unknown Operator: %s' % operator_name)
        unknown_operator = True

    # Check whether an event already exists at these coordinates
    coordinates_known = coords_exist(ev_ra, ev_dec)

    if (coordinates_known[0]==False and unknown_operator==False and unknown_field==False):

        try:

            add_new = Event(field=field, operator=operator,
                            ev_ra=ev_ra, ev_dec=ev_dec,
                            ra=ra_deg, dec=dec_deg,
                            status=status,
                            anomaly_rank=anomaly_rank,
                            year = year,
                            ibase = ibase)
            add_new.save()

            successful = True
            response = 'OK'

        except:

            successful = False
            response = 'Failed to add new event.'

    else:

        successful = False
        response = 'An event already exists with these coordinates.'
        ev_ra, ev_dec = coordinates_known[1], coordinates_known[2]

    return successful, ev_ra, ev_dec, response

##################################################################################
def add_event_name(event, operator, name):
    """
    Add a new event name to the database. Multiple event names can refer to a
    single event at specific coordinates.

    Keyword arguments:
    event -- Event object
        (object, required) -- ForeignKey object
    operator -- Operator object
        (object, required) -- ForeignKey object
    name -- Event name as given by Operator
        (string, required)
    """
    # Check whether an event with that name already exists
    if (check_exists(name)==False):
        try:
            add_new = EventName(event=event, operator=operator, name=name)
            add_new.save()
            successful = True
            response = 'OK'
        except:
            successful = False
            response = 'Failed to add a new event name. Invalid operator or event object.'
    else:
        successful = False
        response = 'This name is already associated with an event.'
    return successful, response

###################################################################################
def check_exists(event_name):
   """
   Check if event exists in database.

   Keyword arguments:
   event_name -- The event name
                 (string, required)
   """
   successful = EventName.objects.filter(name=event_name).exists()
   return successful

###################################################################################
def coords_exist(check_ra, check_dec):
    from astropy import units as u
    from astropy.coordinates import SkyCoord
    """
    Cross-survey identification check.
    Check if an event at these coordinates already exists in the database.
    If the coordinates are already in the database, returns successful = True
    Also returns the coordinates of the object itself or the closest match found.

    Keyword arguments:
    check_ra -- Event RA. (string, required)
        	   e.g. "17:54:33.58"
    check_dec -- Event DEC. (string, required)
        	   e.g. "-30:31:02.02"
    """
    ra, dec = check_ra, check_dec
    # Find, if they exist, a sublist of known events in that vicinity
    # If an exception arises, use all known events
    try:
        known_events = Event.objects.filter(ev_ra__contains=check_ra[0:5]).filter(ev_dec__contains=check_dec[0:5])
    except:
        known_events = Event.objects.all()
    successful = False
    # If there are no known events
    if not known_events:
        successful = False
    else:
        new_coords = SkyCoord(check_ra+' '+check_dec, unit=(u.hourangle, u.deg),
                            frame='icrs')
        match_found = False
        for event in known_events:
            known_coords = SkyCoord(event.ev_ra+' '+event.ev_dec,
	                         unit=(u.hourangle, u.deg),frame='icrs')
            # Calculate separation in arcsec
            separation = new_coords.separation(known_coords).arcsec
            if separation < 2.5:
                match_found = True
                successful = True
                #f = open('./matches.txt','a')
                #f.write('Coordinates '+check_ra+' '+check_dec+' match known object at '+event.ev_ra+' '+event.ev_dec)
                #print 'Found matching object at: '+event.ev_ra+' '+event.ev_dec
                matching_event = Event.objects.filter(ev_ra=event.ev_ra).filter(ev_dec=event.ev_dec)[0]
                known_names = EventName.objects.filter(event=event)
                #f.write(' with event name(s): ')
                #print 'with event name(s):'
                #for n in known_names:
                #   f.write(n.name)
                #   print n.name
                #f.write('\n')
                #f.close()
                ra, dec = event.ev_ra, event.ev_dec
                break
    return successful, ra, dec

###################################################################################
def add_single_lens(event_name, Tmax, tau, umin, last_updated,
            e_Tmax=None, e_tau=None, e_umin=None,
            modeler='', rho=None, e_rho=None, pi_e_n=None, e_pi_e_n=None,
            pi_e_e=None, e_pi_e_e=None, tap_omega=None, chi_sq=None):
    """
    Add Single Lens model parameters to the database.

    Keyword arguments:
    event_name  -- The event name.
                (string, required)
                e.g. "OGLE-2016-BLG-1234"
    Tmax -- Time of maximum magnification.
                (float, required)
                e.g. 2457135.422
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

    if check_exists(event_name)==True:
        # Get event identifier
        event_id = EventName.objects.get(name=event_name).event_id
        event = Event.objects.get(id=event_id)
    # Ensure that Tmax is given in full, e.g.2457135.422, not 7135.422
    if Tmax < 2450000.0:
        Tmax = Tmax + 2450000.0
        # Try adding single lens parameters in the database.
        add_new = SingleModel(event=event, Tmax=Tmax, e_Tmax=e_Tmax, tau=tau,
        		      e_tau=e_tau, umin=umin, e_umin=e_umin, rho=rho,
        		      e_rho=e_rho, pi_e_n=pi_e_n, e_pi_e_n=e_pi_e_n,
        		      pi_e_e=pi_e_e, e_pi_e_e=e_pi_e_e, modeler=modeler,
        		      last_updated=last_updated, tap_omega=tap_omega, chi_sq=chi_sq)
        add_new.save()
        successful = True
        response = 'OK'
    else:
        successful = False
        response = 'Event does not exist.'

    return successful, response

###################################################################################
def add_binary_lens(event_name, Tmax, tau, umin, last_updated, mass_ratio, separation, angle_a,
                    e_Tmax=None, e_tau=None, e_umin=None, e_mass_ratio=None,
                    e_separation=None, e_angle_a=None,  modeler='', rho=None,
                    e_rho=None, pi_e_n=None, e_pi_e_n=None, pi_e_e=None,
                    e_pi_e_e=None, dsdt=None, e_dsdt=None, dadt=None, e_dadt=None, chi_sq=None):
    """
    Add Binary Lens model parameters
    to the database.

    Keyword arguments:
    event_name  -- The event name.
             (string, required)
    	 e.g. "OGLE-2016-BLG-1234"
    Tmax -- Time of maximum magnification.
       (float, required)
        e.g. 2457135.422
    e_Tmax -- Trror in Tmax
        (float, required)
    tau -- Tvent timescale (in days).
      (float, required)
    e_tau -- Trror in tau.
       (float, required)
    umin -- Minimum impact parameter (in units of R_E).
      (float, required)
    e_umin -- Error in umin.
        (float, required)
    mass_ratio -- Mass ratio q between the two lens components.
             (float, required)
    e_mass_ratio -- Error in q
              (float, required)
    separation -- Separation between the two lens components
             (in units of R_E)
     (float, required)
    e_separation -- Error in separation
    angle_a -- Trajectory angle with respect to the binary axis.
          (float, required)
    e_angle_a -- Error in trajectory angle.
          (float, required)
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

    # Try adding binary lens parameters to database
    if check_exists(event_name)==True:
        # Get event identifier
        event_id = EventName.objects.get(name=event_name).event_id
        event = Event.objects.get(id=event_id)
        # Ensure that Tmax is given in full, e.g.2457135.422, not 7135.422
        if Tmax < 2450000.0:
            Tmax = Tmax + 2450000.0

        try:
            add_new = BinaryModel(event=event, Tmax=Tmax, e_Tmax=e_Tmax, tau=tau,
            		       mass_ratio=mass_ratio, e_mass_ratio=e_mass_ratio,
            		       separation=separation, e_separation=e_separation,
            		       angle_a=angle_a, e_angle_a=e_angle_a, e_tau=e_tau,
            		       umin=umin, e_umin=e_umin, rho=rho,
            		       e_rho=e_rho, pi_e_n=pi_e_n, e_pi_e_n=e_pi_e_n,
            		       pi_e_e=pi_e_e, e_pi_e_e=e_pi_e_e, modeler=modeler,
            		       dsdt=dsdt, e_dsdt=e_dsdt, dadt=dadt, e_dadt=e_dadt,
            		       last_updated=last_updated, chi_sq=chi_sq)
            add_new.save()
            successful = True
            response = 'OK'
        except:
            successful = False
            response = 'Failed to add new model.'
    else:
        successful = False
        response = 'Event does not exist.'
    return successful, response

################################################################################################################
def add_reduction(event_name, lc_file, timestamp, ref_image, target_found=False, ron=0.0, gain=1.0,
                     oscanx1=1, oscanx2=50, oscany1=1, oscany2=500, imagex1=51, imagex2=1000,
		     imagey1=1, imagey2=1000, minval=1.0, maxval=55000.0, growsatx=0,
		     growsaty=0, coeff2=1.0e-06, coeff3=1.0e-12,
		     sigclip=4.5, sigfrac=0.5, flim=2.0, niter=4, use_reflist=0, max_nimages=1,
		     max_sky=5000.0, min_ell=0.8, trans_type='polynomial', trans_auto=0, replace_cr=0,
		     min_scale=0.99, max_scale=1.01,
		     fov=0.1, star_space=30, init_mthresh=1.0, smooth_pro=2, smooth_fwhm=3.0,
		     var_deg=1, det_thresh=2.0, psf_thresh=8.0, psf_size=8.0, psf_comp_dist=0.7,
		     psf_comp_flux=0.1, psf_corr_thresh=0.9, ker_rad=2.0, lres_ker_rad=2.0,
		     subframes_x=1, subframes_y=1, grow=0.0, ps_var=0, back_var=1, diffpro=0):
   """
   Add or Update the lightcurve location and pipeline event reduction parameters
   in the database. Also stores the reference frame name and DanDIA parameters
   used to generate the lightcurve.

   Keyword arguments:
   event_name  -- The event name.
                 (string, required)
        	 e.g. "OGLE-2016-BLG-1234"
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
   if check_exists(event_name)==True:
      # Get event identifier
      event_id = EventName.objects.get(name=event_name).event_id
      event = Event.objects.get(id=event_id)
      try:
         add_new = EventReduction(event=event, lc_file=lc_file,
                           timestamp=timestamp, target_found=target_found, ref_image=ref_image,
			   ron=ron, gain=gain, oscanx1=oscanx1,oscanx2=oscanx2,
			   oscany1=oscany1, oscany2=oscany2, imagex1=imagex1,
			   imagex2=imagex2, imagey1=imagey1, imagey2=imagey2,
			   minval=minval, maxval=maxval, growsatx=growsatx,
			   growsaty=growsaty, coeff2=coeff2, coeff3=coeff3,
			   sigclip=sigclip, sigfrac=sigfrac, flim=flim, niter=niter,
			   use_reflist=use_reflist, max_nimages=max_nimages, max_sky=max_sky,
			   min_ell=min_ell, trans_type=trans_type, trans_auto=trans_auto,
			   replace_cr=replace_cr, min_scale=min_scale, max_scale=max_scale,
			   fov=fov, star_space=star_space, init_mthresh=init_mthresh,
			   smooth_pro=smooth_pro, smooth_fwhm=smooth_fwhm, var_deg=var_deg,
			   det_thresh=det_thresh, psf_thresh=psf_thresh, psf_size=psf_size,
			   psf_comp_dist=psf_comp_dist, psf_comp_flux=psf_comp_flux,
			   psf_corr_thresh=psf_corr_thresh, ker_rad=ker_rad,
			   lres_ker_rad=lres_ker_rad, subframes_x=subframes_x,
			   subframes_y=subframes_y, grow=grow, ps_var=ps_var, back_var=back_var,
			   diffpro=diffpro)
         add_new.save()
         successful = True
      except:
         successful = False
   else:
      successful = False
   return successful

################################################################################################################
def add_request(field_name, t_sample, exptime, timestamp=timezone.now(),
                time_expire=timezone.now()+timedelta(hours=24), pfrm_on = False,
                onem_on=False, twom_on=False, request_type='L', which_site='', which_filter='',
		which_inst='', grp_id='', track_id='', req_id='', n_exp=1, request_status = 'AC'):
   """
   Add observing request to the database.

   Keyword arguments:
   field_name -- The field name.
                 (string, required)
        	 e.g. 'ROME-FIELD-17'
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
   which_site -- Site identifier string.
                   (string, optional, default='')
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

   if Field.objects.filter(name=field_name).exists()==True:
      # Get field identifier
      field = Field.objects.get(name=field_name)
      field_object = Field.objects.get(id=field.id)
      observations_to_save = []
      try:
          add_new = ObsRequest(field=field_object, t_sample=t_sample, exptime=exptime,
                           timestamp=timestamp, time_expire=time_expire,
                           pfrm_on= pfrm_on, onem_on=onem_on, twom_on=twom_on,
		               request_type=request_type, which_site=which_site,
			       which_filter=which_filter,
			       which_inst=which_inst, grp_id=grp_id, track_id=track_id,
			       req_id=req_id, n_exp=n_exp, request_status=request_status)
          add_new.save()
          successful = True
      except:
          successful = False
   else:
      successful = False
   return successful

################################################################################################################
def add_sub_request(sr_id,request_grp_id, request_track_id,
                    window_start, window_end, status, time_executed):
    """
    Add observing sub-request to the database.

    Keyword arguments:
    sr_id -- The ID of the subrequest assigned by the LCO scheduler
                (string, required)
    request_grp_id -- The originating ObsRequest group_id.
                 (string, required)
    request_track_id -- The originating ObsRequest track_id.
                 (string, required)
    window_start -- First timestamp when the subrequest can be executed
                 (object, DateTime)
    window_end -- Last timestamp, after which the subrequest expires
                 (object, DateTime)
    status -- The last known state of the request in the LCO scheduler
                 (string, choice field)
                 ('PENDING', 'COMPLETED', 'CANCELED', 'WINDOW_EXPIRED')
    time_executed -- The timestamp of when the subrequest was executed
                 (object, optional, DateTime)
    """
    if ObsRequest.objects.filter(grp_id=request_grp_id).exists()==True:

        if SubObsRequest.objects.filter(sr_id=sr_id).exists() == False:

            try:
                if time_executed != None:

                    sr = SubObsRequest(sr_id=sr_id,
                                       grp_id=request_grp_id,
                                       track_id=request_track_id,
                                       window_start=window_start,
                                       window_end=window_end,
                                       status=status,
                                       time_executed=time_executed)
                else:

                    sr = SubObsRequest(sr_id=sr_id,
                                       grp_id=request_grp_id,
                                       track_id=request_track_id,
                                       window_start=window_start,
                                       window_end=window_end,
                                       status=status)

                sr.save()

                successful = True
                message = 'DBREPLY: Subrequest added'

            except:

                successful = False
                message = 'DBREPLY: Error during ingestion of subrequest'

        else:

            successful = False
            message = 'DBREPLY: Subrequest already exists'

    else:

        successful = False
        message = 'DBREPLY: Unrecognised Obsrequest group ID'

    return successful, message

def update_sub_request(sr_id,request_grp_id, request_track_id,
                    window_start, window_end, status, time_executed):
    """
    Update an existsing observing sub-request in the database.

    Keyword arguments:
    sr_id -- The ID of the subrequest assigned by the LCO scheduler
                (string, required)
    request_grp_id -- The originating ObsRequest group_id.
                 (string, required)
    request_track_id -- The originating ObsRequest track_id.
                 (string, required)
    window_start -- First timestamp when the subrequest can be executed
                 (object, DateTime)
    window_end -- Last timestamp, after which the subrequest expires
                 (object, DateTime)
    status -- The last known state of the request in the LCO scheduler
                 (string, choice field)
                 ('PENDING', 'COMPLETED', 'CANCELED', 'WINDOW_EXPIRED')
    time_executed -- The timestamp of when the subrequest was executed
                 (object, optional, DateTime)
    """
    if ObsRequest.objects.filter(grp_id=request_grp_id).exists()==True:

        if SubObsRequest.objects.filter(sr_id=sr_id).exists() == True:

            try:
                qs = SubObsRequest.objects.filter(sr_id=sr_id)
                sr = qs[0]

                sr.window_start = window_start
                sr.window_end = window_end
                sr.state = status

                if time_executed != None:

                    sr.time_executed = time_executed

                sr.save()
                successful = True
                message = 'DBREPLY: Subrequest updated'

            except:

                successful = False
                message = 'DBREPLY: Error during update of subrequest'

        else:

            successful = False
            message = 'DBREPLY: Subrequest is unknown to the database'

    else:

        successful = False
        message = 'DBREPLY: Unrecognised Obsrequest group ID'

    return successful, message

################################################################################################################
def update_tap_status(event, priority):
    """
    Update an existsing observing sub-request in the database.

    Keyword arguments:
    event -- Event object
                (string, required)
    event_id -- The event to be updated
                 (string, required)
    priority -- The priority to set, one of:
                (string, optional, default='N')
                    'A':'REA High',
                    'L':'REA Low',
                    'B':'REA Post-High'
                    'N':'None'
    """

    if Tap.objects.filter(event=event).exists()==True:

        if priority in [ 'A', 'L', 'B', 'N' ]:

            tsamp = rea_obs.get_rea_tsamp(priority)

            if priority != 'N' and tsamp == 0.0:

                successful = False
                message = 'DBREPLY: No valid sampling rate available for priority '+\
                        priority+' observations'

            else:

                try:

                    qs = Tap.objects.filter(event=event).order_by('timestamp').reverse()

                    tap_target = qs[0]

                    tap_target.priority = priority

                    tap_target.tsamp = tsamp

                    tap_target.save()

                    successful = True
                    message = 'DBREPLY: TAP status updated'

                except:

                    successful = False
                    message = 'DBREPLY: Error during update of TAP status'

        else:

            successful = False
            message = 'DBREPLY: Unrecognised TAP status setting'

    else:

        successful = False
        message = 'DBREPLY: Unrecognised TAP event'

    return successful, message

def update_event_status(event, state, override, interactive=False):
    """
    Update an existsing observing sub-request in the database.

    Keyword arguments:
    event -- Event object
                (string, required)
    state -- The priority to set, one of:
                (string, optional, default='NF')
                'NF', 'Not in footprint'
                'AC', 'active'
                'MO', 'monitor'
                'AN', 'anomaly'
                'EX', 'expired'
    override -- The manual override flag for TAP (True or False)
    """

    if Event.objects.filter(pk=event.pk).exists()==True:

        if state in [ 'NF', 'AC', 'MO', 'AN', 'EX' ]:

            try:

                qs = Event.objects.filter(pk=event.pk)

                e = qs[0]

                if e.override == False or interactive:
                    e.status = state
                    e.override = override
                    e.save()

                    successful = True
                    message = 'DBREPLY: event status updated'

                else:

                   successful = True
                   message = 'DBREPLY: event state manually overridden, no update made'

            except:

                successful = False
                message = 'DBREPLY: Error during update of event status'

        else:

            successful = False
            message = 'DBREPLY: Unrecognised event status setting'

    else:

        successful = False
        message = 'DBREPLY: Unrecognised event'

    return successful, message

def update_event(event_name, params):
    """Function to update the parameters of an event that is already known
    to the database.

    Only supports the parameters ra, dec and ibase.
    """

    qs = EventName.objects.filter(name=event_name)

    if len(qs) > 0:

        event = qs[0].event

        set_keys = ''

        for key, value in params.items():

            if key in ['ra', 'dec', 'ibase']:

                setattr(event,key,value)

                set_keys += key+' '

        event.save()

        successful = True
        message = 'DBREPLY: event '+set_keys+' updated'

    else:

        successful = False
        message = 'DBREPLY: Unrecognised event'

    return successful, message

################################################################################################################
def add_status(event_name, timestamp=timezone.now(), status='NF', comment='',
               updated_by='', rec_cad=0, rec_texp=0, rec_nexp=0, rec_telclass=''):
    """
    Add event status to the database.

    Keyword arguments:
    event_name -- The event name.
    (string, required)
    e.g. "OGLE-2016-BLG-1234"
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
    (string, optional, default='')
    """
    if check_exists(event_name)==True:
        # Get event identifier
        event_id = EventName.objects.get(name=event_name).event_id
        event = Event.objects.get(id=event_id)
        try:
            add_new = EventStatus(event=event, timestamp=timestamp, status=status,
            comment=comment, updated_by=updated_by, rec_cad=rec_cad,
            rec_texp=rec_texp, rec_nexp=rec_nexp,
            rec_telclass=rec_telclass)
            add_new.save()
            successful = True
        except:
            successful = False
    else:
        successful = False
    return successful

###################################################################################
def add_datafile(event_name, datafile, last_upd, last_hjd, last_mag, tel, ndata, inst='',
                 filt='', baseline=22.0, g=0.0):
    """
    Add a data file to the database.
    Uses the .dat files rsynced from ARTEMiS.

    Keyword arguments:
    event_name -- The event name.
                    (string, required)
    datafile -- Full path to the data file.
                    (string, required)
    last_upd -- Datetime of last update.
                    (datetime, required, default=timezone.now())
    last_hjd -- HJD of last observation. (float, required)
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
    # Check if the event already exists in the database.
    message = 'OK'
    if check_exists(event_name)==True:
        # Get event identifier
        event_id = EventName.objects.get(name=event_name).event_id
        event = Event.objects.get(id=event_id)
        try:
            add_new = DataFile(event=event, datafile=datafile, last_upd=last_upd,
                               last_hjd=last_hjd, last_mag=last_mag, tel=tel,
                               inst=inst, filt=filt, baseline=baseline,
                               g=g, ndata=ndata)
            add_new.save()
            successful = True
            message = 'OK'
        except:
            successful = False
            message = 'Error ingesting datafile to database'
    else:
        successful = False
        message = 'Error ingesting datafile - event not found'
    return successful, message

###################################################################################
def add_datafile_via_api(params):
    """
    Add a data file to the database.
    Uses the .dat files rsynced from ARTEMiS.

    Keyword arguments:
        params   dictionary with parameters:
        event_name     str       The event name.
        datafile       str       Full path to the data file.
        last_upd       datetime  Timestamp of last update.
        last_obs       datetime  Timestamp last observation.
        last_mag       float     Last recorded magnitude.
        tel            str       Telescope identifier.
        filt           str       Filter used for the observations.
        baseline       float     I0 blend parameter from ARTEMiS .align file.
        g              float     g blend parameter from ARTEMiS .align file.
        ndata          int       Number of data points.
    """

    status = True
    message = 'DBREPLY: OK'

    if check_exists(params['event_name'])==True:
        event_id = EventName.objects.get(name=params['event_name']).event_id
        event = Event.objects.get(id=event_id)

        if type(params['last_upd']) == type('foo'):
            last_upd = datetime.strptime(params['last_upd'],"%Y-%m-%dT%H:%M:%S")
        else:
            last_upd = params['last_upd']
        last_upd = last_upd.replace(tzinfo=pytz.UTC)

        qs = DataFile.objects.filter(datafile=params['datafile'])

        if len(qs) > 1:
            status = False
            message = 'DBREPLY: Error: multiple matching datafiles in the database'

        elif len(qs) == 1:
            file_entry = qs[0]
            if file_entry.last_upd >= last_upd:
                status = True
                message = 'DBREPLY: DB entry for this data file is up to date'
            else:
                try:
                    file_entry.last_upd = last_upd
                    file_entry.last_hjd = float(params['last_hjd'])
                    file_entry.last_mag = float(params['last_mag'])
                    file_entry.tel=params['tel']
                    file_entry.filt=params['filt']
                    file_entry.baseline=float(params['baseline'])
                    file_entry.g=float(params['g'])
                    file_entry.ndata=int(params['ndata'])
                    file_entry.save()
                    status = True
                    message = 'DBREPLY: Updated database entry'
                except InvalidOperation:
                    err = ''
                    for key, value in params.items():
                        err += str(key)+'='+str(value)+' '
                    message = 'DBREPLY: ERROR storing datafile entry.  Received parameters:\n'+err
                    status = False
        else:
            try:
                (new_file,result) = DataFile.objects.get_or_create(event=event,
                            datafile=params['datafile'],
                            last_upd=last_upd,
                            last_hjd=params['last_hjd'],
                            last_mag=float(params['last_mag']),
                            tel=params['tel'],
                            filt=params['filt'],
                            baseline=float(params['baseline']),
                            g=float(params['g']), ndata=int(params['ndata']))
                status = True
                message = 'DBREPLY: Created new database entry'

            except InvalidOperation:
                err = ''
                for key, value in params.items():
                    err += str(key)+'='+str(value)+' '
                message = 'DBREPLY: ERROR creating datafile entry.  Received parameters:\n'+err
                status = False
    else:
        status = False
        message = 'DBREPLY: Event not in database'

    return status, message

###################################################################################
def add_tap(event_name, timestamp=timezone.now(), priority='N', tsamp=0, texp=0, nexp=1,
            telclass='1m', imag=22.0, omega=None, err_omega=None, peak_omega=None, blended=False,
	    visibility=None, cost1m=None, passband='SDSS-i', ipp=1.0):
    """
    Add a TAP entry to the database.
    Assumes TAP has already evaluated the necessary parameters.

    Keyword arguments:
    event_name -- The event name.
    (string, required)
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
    # Check if the event already exists in the database.
    if check_exists(event_name)==True:
        # Get event identifier
        event_id = EventName.objects.get(name=event_name).event_id
        event = Event.objects.get(id=event_id)
        try:
            add_new = Tap(event=event, timestamp=timestamp, priority=priority, tsamp=tsamp,
            texp=texp, nexp=nexp, telclass=telclass, imag=imag, omega=omega,
            err_omega=err_omega, peak_omega=peak_omega, blended=blended,
            visibility=visibility, cost1m=cost1m, passband=passband, ipp=ipp)
            add_new.save()
            successful = True
        except:
            successful = False
    else:
        successful = False
    return successful

###################################################################################
def add_taplima(event_name, timestamp=timezone.now(), priority='N', tsamp=0, texp=0, nexp=1,
            telclass='1m', imag=22.0, omega=None, err_omega=None, peak_omega=None, blended=False,
	    visibility=None, cost1m=None, passband='SDSS-i', ipp=1.0):
    """
    Add a TAP entry to the database.
    Assumes TAP has already evaluated the necessary parameters.

    Keyword arguments:
    event_name -- The event name.
    (string, required)
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
    # Check if the event already exists in the database.
    if check_exists(event_name)==True:
        # Get event identifier
        event_id = EventName.objects.get(name=event_name).event_id
        event = Event.objects.get(id=event_id)
        try:
            add_new = TapLima(event=event, timestamp=timestamp, priority=priority, tsamp=tsamp,
            texp=texp, nexp=nexp, telclass=telclass, imag=imag, omega=omega,
            err_omega=err_omega, peak_omega=peak_omega, blended=blended,
            visibility=visibility, cost1m=cost1m, passband=passband, ipp=ipp)
            add_new.save()
            successful = True
        except:
            successful = False
    else:
        successful = False
    return successful

###################################################################################
def add_image(field_name, image_name, date_obs, timestamp=timezone.now(), tel='', inst='',
              filt='', grp_id='', track_id='', req_id='', airmass=None, avg_fwhm=None,
              avg_sky=None, avg_sigsky=None, moon_sep=None, moon_phase=None, moon_up=False,
              elongation=None, nstars=None, ztemp=None, shift_x=None, shift_y=None, quality=''):
    """Add or update an image entry to the database. If the image already exists, it only allows
   the user to set the target_* parameters.

   Keyword arguments:
   field_name -- The field name.
                (string, required)
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
   shift_x -- x-axis WCS shift from template image in pixels
             (integer, optional, default=None)
   shift_y -- y-axis WCS shift from template image in pixels
             (integer, optional, default=None)
   quality -- Image quality description.
                 (string, optional, default='')
    """

    # Check if the field already exists in the database.
    if Field.objects.filter(name=field_name).exists()==True:

        field = Field.objects.get(name=field_name)
        field_object = Field.objects.get(id=field.id)

 #       try:
        add_new = Image(field=field_object, image_name=image_name, date_obs=date_obs, timestamp=timestamp,
                        tel=tel, inst=inst, filt=filt, grp_id=grp_id, track_id=track_id, req_id=req_id,
                        airmass=airmass, avg_fwhm=avg_fwhm, avg_sky=avg_sky, avg_sigsky=avg_sigsky,
                        moon_sep=moon_sep, moon_phase=moon_phase, moon_up=moon_up, elongation=elongation,
                        nstars=nstars, ztemp=ztemp, shift_x=shift_x, shift_y=shift_y, quality=quality)

        add_new.save()

        successful = True

 #       except:

 #           successful = False

    else:

        successful = False

    return successful

def update_image(image_name, date_obs, timestamp=timezone.now(),
                 tel='', inst='',filt='', grp_id='', track_id='', req_id='',
                 airmass=None, avg_fwhm=None,avg_sky=None, avg_sigsky=None,
                 moon_sep=None, moon_phase=None, moon_up=False, elongation=None,
                 nstars=None, ztemp=None, shift_x=None, shift_y=None, quality=''):
    """
    Update an existing image entry in the database.

    Keyword arguments:

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
    shift_x -- x-axis WCS shift from template image in pixels
                (integer, optional, default=None)
    shift_y -- y-axis WCS shift from template image in pixels
                (integer, optional, default=None)
    quality -- Image quality description.
                (string, optional, default='')
    """

    qs = Image.objects.filter(image_name=image_name)
    if len(qs) > 0:
        image = qs[0]
        image.date_obs = date_obs
        image.timestamp = timestamp
        image.tel = tel
        image.inst = inst
        image.filt = filt
        image.grp_id = grp_id
        image.track_id = track_id
        image.req_id= req_id
        if airmass != None:
            image.airmass = airmass
        if avg_fwhm != None:
            image.avg_fwhm = avg_fwhm
        if avg_sky != None:
            image.avg_sky = avg_sky
        if avg_sigsky != None:
            image.avg_sigsky = avg_sigsky
        if moon_sep != None:
            image.moon_sep = moon_sep
        if moon_phase != None:
            image.moon_phase = moon_phase
        if moon_up != None:
            image.moon_up = moon_up
        if elongation != None:
            image.elongation = elongation
        if nstars != None:
            image.nstars = nstars
        if ztemp != None:
            image.ztemp = ztemp
        if shift_x != None:
            image.shift_x = shift_x
        if shift_y != None:
            image.shift_y = shift_y
        if quality != None:
            image.quality = quality

        image.save()
        return True
    else:
        return False


###################################################################################
def expire_old_obs(log=None):
    """Function to identify observations in the DB which have exceeded their
    expiry date and set their status to 'EX'"""

    if log!=None:
        log.info('Expiring active observations that have exceeded their expiry date')

    qs = query_db.get_old_active_obs()
    if log!=None:
        log.info(' -> Found '+str(len(qs)))

    for obs in qs:
        obs.request_status = 'EX'
        obs.save()
        if log!=None:
            log.info(' -> Expired '+obs.grp_id+' expiry date='+\
                    obs.time_expire.strftime('%Y-%m-%dT%H:%M:%S'))

###################################################################################
def run_test2():
    from astropy.time import Time
    year = str(datetime.now().year)
    # Path to ARTEMiS files
    artemis_col = local_conf.get_conf('artemis_cols')
    artemis = local_conf.get_conf('artemis')
    # Color & site definitions for plotting
    colors = artemis_col+"colours.sig.cfg"
    colordef = artemis_col+"colourdef.sig.cfg"
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

    #Populate User database
    from django.contrib.auth.models import User
    my_users = {
               'rstreet':[xxx, 'Rachel', 'Street', 'rstreet@lco.global', True, True],
               'ebachelet':[xxx, 'Etienne', 'Bachelet', 'etibachelet@gmail.com', True, True],
               'mhundetmark':[xxx, 'Markus', 'Hundertmark', 'markus.hundertmark@uni-heidelberg.de', True, True],
               'dbramich':[xxx, 'Dan', 'Bramich', 'dan.bramich@hotmail.co.uk', False, False],
               'mdominik':[xxx, 'Martin', 'Dominik', 'md35@st-andrews.ac.uk', False, False],
               'khorne':[xxx, 'Keith', 'Horne', 'kdh1@st-andrews.ac.uk', False, False],
               'jwambsganss':[xxx, 'Joachim', 'Wambsganss', 'jkw@ari.uni-heidelberg.de', False, False],
               'vbozza':[xxx, 'Valerio', 'Bozza', 'valboz@sa.infn.it', False, False],
               'acassan':[xxx, 'Arnaud', 'Cassan', 'cassan@iap.fr', False, False],
               'smao':[xxx, 'Shude', 'Mao', 'shude.mao@gmail.com', False, False],
               'asaha':[xxx, 'Abhijit', 'Saha', 'saha@noao.edu', False, False],
               'zweichen':[xxx, 'Zang', 'Weichen', '3130102785@zju.edu.cn', False, False],
               'twang':[xxx, 'Tianshu', 'Wang', 'wts15@mails.tsinghua.edu.cn', False, False]
              }
    for i in my_users.keys():
        user = User.objects.create_user(i, password = my_users[i][0], first_name = my_users[i][1],
                                      last_name = my_users[i][2], email = my_users[i][3])
        user.is_superuser = my_users[i][4]
        user.is_staff = my_users[i][5]
        user.save()

    # Populate Operator database
    for s in ['OGLE', 'MOA', 'KMTNET', 'PLANET', 'ROMEREA', 'MICROFUN', 'OTHER']:
        add_operator(s)

    # Populate Telescope database
    from random import uniform
    for i in site_dict.keys():
        tel_name = site_dict[i][-1]
        print(tel_name)
        if ('LCOGT' in tel_name) or ('Liverpool' in tel_name) or ('Faulkes' in tel_name):
            # Get the appropriate pk for RoboNet
            operator = 'ROMEREA'
        if ('SSO' in tel_name) or ('Faulkes South' in tel_name):
            longitude = -31.27
            latitude = 149.07
            altitude = 1116.0
            site = 'COJ'
        elif 'CTIO' in tel_name:
            longitude = -30.17
            latitude = -70.81
            altitude = 2198.0
            site = 'LSC'
        elif 'SAAO' in tel_name:
            longitude = -32.38
            latitude = 20.81
            altitude = 1460.0
            site = 'CPT'
        elif 'Liverpool' in tel_name:
            longitude = 28.76
            latitude = -17.88
            altitude = 2396.0
            site = 'LAP'
        elif 'Faulkes North' in tel_name:
            longitude = 20.71
            latitude = -156.26
            altitude = 3055.0
            site = 'OGG'
        #else:
        #    longitude = None
        #    latitude = None
        #    altitude = None
        #    site = ''
        elif 'OGLE' in tel_name:
            operator = 'OGLE'
            longitude = -29.01
            latitude = -70.70
            altitude = 2275.0
            site = 'LCO'
        elif 'MOA' in tel_name:
            operator = 'MOA'
            longitude = -43.99
            latitude = 170.47
            altitude = 1029.0
            site = 'MJUO'
        else:
            operator = 'OTHER'
            longitude = None
            latitude = None
            altitude = None
            site = ''
            aperture = float(tel_name.split()[-1][:-1])
        #print operator, tel_name, aperture, site
        add_telescope(operator=operator, name=tel_name, longitude=longitude,
            latitude=latitude, altitude=altitude, aperture=aperture, site=site)

    # Populate Instrument database
    for i in Telescope.objects.all().values():
        inst = i['name'] +' CCD camera'
        telescope = Telescope.objects.get(name=i['name'])
        if all(x not in i['name'] for x in ['LCOGT', 'OGLE', 'MOA 1.8m', 'Faulkes']):
            add_instrument(telescope=telescope, instrument_name=inst)

    # Add known instruments at existing telescopes
    telescope = Telescope.objects.get(name='Faulkes South 2.0m')
    inst = 'fs01'
    pixscale = 0.304
    add_instrument(telescope=telescope, instrument_name=inst, pixscale=pixscale)

    telescope = Telescope.objects.get(name='Faulkes North 2.0m')
    inst = 'fs02'
    pixscale = 0.301
    add_instrument(telescope=telescope, instrument_name=inst, pixscale=pixscale)

    telescope = Telescope.objects.get(name='LCOGT SSO A 1m')
    inst = 'fl12'
    pixscale = 0.389
    add_instrument(telescope=telescope, instrument_name=inst, pixscale=pixscale)

    telescope = Telescope.objects.get(name='LCOGT SSO B 1m')
    inst = 'fl11'
    pixscale = 0.389
    add_instrument(telescope=telescope, instrument_name=inst, pixscale=pixscale)

    telescope = Telescope.objects.get(name='LCOGT CTIO A 1m')
    inst = 'fl15'
    pixscale = 0.389
    add_instrument(telescope=telescope, instrument_name=inst, pixscale=pixscale)

    telescope = Telescope.objects.get(name='LCOGT CTIO B 1m')
    inst = 'fl03'
    pixscale = 0.389
    add_instrument(telescope=telescope, instrument_name=inst, pixscale=pixscale)

    telescope = Telescope.objects.get(name='LCOGT CTIO C 1m')
    inst = 'fl04'
    pixscale = 0.389
    add_instrument(telescope=telescope, instrument_name=inst, pixscale=pixscale)

    telescope = Telescope.objects.get(name='LCOGT SAAO A 1m')
    inst = 'fl16'
    pixscale = 0.389
    add_instrument(telescope=telescope, instrument_name=inst, pixscale=pixscale)

    telescope = Telescope.objects.get(name='LCOGT SAAO B 1m')
    inst = 'fl14'
    pixscale = 0.389
    add_instrument(telescope=telescope, instrument_name=inst, pixscale=pixscale)

    telescope = Telescope.objects.get(name='LCOGT SAAO C 1m')
    inst = 'fl06'
    pixscale = 0.389
    add_instrument(telescope=telescope, instrument_name=inst, pixscale=pixscale)

    telescope = Telescope.objects.get(name='OGLE 1.3m')
    inst = 'OGLE-IV mosaic camera'
    pixscale = 0.26
    add_instrument(telescope=telescope, instrument_name=inst, pixscale=pixscale)

    telescope = Telescope.objects.get(name='MOA 1.8m')
    inst = 'MOA-cam3'
    pixscale = 0.58
    add_instrument(telescope=telescope, instrument_name=inst, pixscale=pixscale)

    # Populate filter database
    filters = ['Bessell-U', 'Bessell-B', 'Bessell-V','Bessell-R','Bessell-I', 'SDSS-u',
                'SDSS-g', 'SDSS-r', 'SDSS-i', 'SDSS-z', 'H-alpha']
    for i in Instrument.objects.all():
        for j in filters:
            add_filter(instrument=i, filter_name=j)

    # Populate Field database
    from rome_fields_dict import field_dict
    for i in field_dict.keys():
        add_field(field_name=i, field_ra=field_dict[i][2], field_dec=field_dict[i][3])

    # Add an empty field for outside footprint
    add_field()

    # Populate Event database with MOA event coordinates
    # and EventName database with MOA event names
    from glob import glob
    import numpy as np
    from utilities import sex2decdeg
    from field_check import romecheck
    moa_event_list = glob(artemis+'PublishedParameters/'+year+'/MOA/*.model')
    count = 0
    operator_name = 'MOA'
    for i in moa_event_list:
        data = open(i).read().split()
        ev_ra = data[0]
        ev_dec = data[1]
        # Convert from sexagesimal to decimal degrees
        ev_ra_deg, ev_dec_deg = sex2decdeg(ev_ra, ev_dec)
        name = data[2].replace('KB'+year[2:],'MOA-'+year+'-BLG-')
        #print 'Doing '+name
        #print 'Trying to add event ...'
        t = Time(datetime.now())
        tjd = t.jd - 2450000.0
        if (float(data[3]) <= 2450000.0):
            tmax = float(data[3])+2450000.0
        else:
            tmax = float(data[3])
        if abs(tjd-tmax) <= 5.0*float(data[5]):
            guess_status = 'AC'
        else:
            guess_status = 'EX'
        # Find field
        id_field, rate = romecheck(ev_ra_deg, ev_dec_deg)
        if id_field == -1:
            field_name = "Outside ROMEREA footprint"
            guess_status = 'NF'
        else:
            field_name = sorted(field_dict.keys())[id_field]
        x = add_event(field_name=field_name, operator_name=operator_name, ev_ra=ev_ra, ev_dec=ev_dec,
        status=guess_status, anomaly_rank = -1.0, year=year)
        #print 'Trying to filter for event ...'
        event = Event.objects.filter(ev_ra=x[1]).filter(ev_dec=x[2])[0]
        operator = Operator.objects.get(name='MOA')
        #print 'Trying to add event name ...'
        y = add_event_name(event=event, operator=operator, name=name)
        count = count + 1
        print(count)

    # Populate Event database with OGLE event coordinates
    # and EventName database with OGLE event names
    from glob import glob
    import numpy as np
    from utilities import sex2decdeg
    from field_check import romecheck
    ogle_event_list = glob(artemis+'PublishedParameters/'+year+'/OGLE/*.model')
    count = 0
    operator_name = "OGLE"
    for i in ogle_event_list:
        data = open(i).read().split()
        ev_ra = data[0]
        ev_dec = data[1]
        # Convert from sexagesimal to decimal degrees
        ev_ra_deg, ev_dec_deg = sex2decdeg(ev_ra, ev_dec)
        name = data[2].replace('OB'+year[2:],'OGLE-'+year+'-BLG-')
        #print 'Doing '+name
        #print 'Trying to add event ...'
        t = Time(datetime.now())
        tjd = t.jd - 2450000.0
        if (float(data[3]) <= 2450000.0):
            tmax = float(data[3])+2450000.0
        else:
            tmax = float(data[3])
        if abs(tjd-tmax) <= 5.0*float(data[5]):
            guess_status = 'AC'
        else:
            guess_status = 'EX'
            # Find field
            id_field, rate = romecheck(ev_ra_deg, ev_dec_deg)
        if id_field == -1:
            field_name = "Outside ROMEREA footprint"
            guess_status = 'NF'
        else:
            field_name = sorted(field_dict.keys())[id_field]
            x = add_event(field_name=field_name, operator_name=operator_name, ev_ra=ev_ra, ev_dec=ev_dec,
        status=guess_status, anomaly_rank = -1.0, year=year)
        #print 'Trying to filter for event ...'
        event = Event.objects.filter(ev_ra=x[1]).filter(ev_dec=x[2])[0]
        operator = Operator.objects.get(name='OGLE')
        #print 'Trying to add event name ...'
        y = add_event_name(event=event, operator=operator, name=name)
        count = count + 1
        print(count)


    # Populate SingleLens model database from ARTEMiS model files
    from glob import glob
    from astropy.time import Time
    ogle_event_pars = glob(artemis+'PublishedParameters/'+year+'/OGLE/*.model')
    for i in ogle_event_pars:
        data = open(i).read().split()
        ev_ra = data[0]
        ev_dec = data[1]
        name = data[2].replace('OB'+year[2:],'OGLE-'+year+'-BLG-')
        event_id = EventName.objects.get(name=name).event_id
        event = Event.objects.get(id=event_id)
        Tmax, e_Tmax = float(data[3]), float(data[4])
        tau, e_tau = float(data[5]), float(data[6])
        umin, e_umin = float(data[7]), float(data[8])
        #timestamp of most recent datapoint
        time_last_datapoint = Time(float(data[12])+2450000.0, format='jd').datetime
        last_updated = timezone.make_aware(time_last_datapoint, timezone.get_current_timezone())
        modeler = 'OGLE'
        add_single_lens(event_name=name, Tmax=Tmax, tau=tau, umin=umin,
                last_updated=last_updated, e_Tmax=e_Tmax, e_tau=e_tau,
                e_umin=e_umin, modeler=modeler, rho=None,
                e_rho=None, pi_e_n=None, e_pi_e_n=None, pi_e_e=None, e_pi_e_e=None)

    moa_event_pars = glob(artemis+'PublishedParameters/'+year+'/MOA/*.model')
    for i in moa_event_pars:
        data = open(i).read().split()
        ev_ra = data[0]
        ev_dec = data[1]
        name = data[2].replace('KB'+year[2:],'MOA-'+year+'-BLG-')
        event_id = EventName.objects.get(name=name).event_id
        event = Event.objects.get(id=event_id)
        Tmax, e_Tmax = float(data[3]), float(data[4])
        tau, e_tau = float(data[5]), float(data[6])
        umin, e_umin = float(data[7]), float(data[8])
        #timestamp of most recent datapoint
        time_last_datapoint = Time(float(data[12])+2450000.0, format='jd').datetime
        last_updated = timezone.make_aware(time_last_datapoint, timezone.get_current_timezone())
        modeler = 'MOA'
        add_single_lens(event_name=name, Tmax=Tmax, tau=tau, umin=umin, last_updated=last_updated,
                e_Tmax=e_Tmax, e_tau=e_tau, e_umin=e_umin, modeler=modeler, rho=None,
                e_rho=None, pi_e_n=None, e_pi_e_n=None, pi_e_e=None, e_pi_e_e=None)

    artemis_event_pars = glob(artemis+'model/*B'+year[2:]+'*.model')
    for i in artemis_event_pars:
        # Exclude rogue files with incorrect entries
        try:
            data = open(i).read().split()
            ev_ra = data[0]
            ev_dec = data[1]
            if data[2].startswith('KB'+year[2:]):
                name = data[2].replace('KB'+year[2:],'MOA-'+year+'-BLG-')
            if data[2].startswith('OB'+year[2:]):
                name = data[2].replace('OB'+year[2:],'OGLE-'+year+'-BLG-')
            event_id = EventName.objects.get(name=name).event_id
            event = Event.objects.get(id=event_id)
            Tmax, e_Tmax = float(data[3]), float(data[4])
            tau, e_tau = float(data[5]), float(data[6])
            umin, e_umin = float(data[7]), float(data[8])
            #timestamp of most recent datapoint
            time_last_datapoint = Time(float(data[12])+2450000.0, format='jd').datetime
            last_updated = timezone.make_aware(time_last_datapoint, timezone.get_current_timezone())
            modeler = 'ARTEMiS'
            add_single_lens(event_name=name, Tmax=Tmax, tau=tau, umin=umin, last_updated=last_updated,
                        e_Tmax=e_Tmax, e_tau=e_tau, e_umin=e_umin, modeler=modeler, rho=None,
                        e_rho=None, pi_e_n=None, e_pi_e_n=None, pi_e_e=None, e_pi_e_e=None)
        except:
            continue

    pylima_event_pars =  glob(artemis+'PYLIMA_MODELS/*B'+year[2:]+'*_model')
    for i in pylima_event_pars:
        # Exclude rogue files with incorrect entries
        try:
            data = open(i).read().split()
            if data[2].startswith('KB'+year[2:]):
                name = data[2].replace('KB'+year[2:],'MOA-'+year+'-BLG-')
            if data[2].startswith('OB'+year[2:]):
                name = data[2].replace('OB'+year[2:],'OGLE-'+year+'-BLG-')
            event_id = EventName.objects.get(name=name).event_id
            event = Event.objects.get(id=event_id)
            ev_ra = event.ev_ra
            ev_dec = event.ev_dec
            Tmax, e_Tmax = float(data[3]), float(data[4])
            tau, e_tau = float(data[5]), float(data[6])
            umin, e_umin = float(data[7]), float(data[8])
            #timestamp of most recent datapoint
            time_last_datapoint = Time(float(data[12])+2450000.0, format='jd').datetime
            last_updated = timezone.make_aware(time_last_datapoint, timezone.get_current_timezone())
            modeler = 'pyLIMA'
            add_single_lens(event_name=name, Tmax=Tmax, tau=tau, umin=umin, last_updated=last_updated,
                    e_Tmax=e_Tmax, e_tau=e_tau, e_umin=e_umin, modeler=modeler, rho=None,
                    e_rho=None, pi_e_n=None, e_pi_e_n=None, pi_e_e=None, e_pi_e_e=None)
        except:
            continue

   # Populate EventReduction by reading the event directories in
   # ProcData
   #from lxml import etree
   #def todict(xml_file):
   #   ''' Convert an xml tree into a dictionary. '''
   #   d = {}
   #   tree = etree.parse(xml_file)
   #   root = tree.getroot()
   #   for parameter in root.findall('parameter'):
   #      name = parameter.get('name')
   #	 val = parameter.find('value').text
   # 	 d[name] = val
   #   return d
   #
   #count = 0
   #events_robonet = glob('/science/robonet/rob/Operations/ProcData/'+year+'/*')
   #for i in events_robonet:
   #    try:
   #       event_name = i.split('/')[-1].split('_')[0]
   #	  lc_file = glob(i+'/lc/*/rawlc/*.t')
   #	  if lc_file:
   #	     lc_file = lc_file[0]
   #	     is_target_found = True
   #	  else:
   #	     lc_file = ''
   #	     is_target_found = False
   #	  timestamp = timezone.now()
   #	  ref_image = glob(i+'/reflist.*.txt')
   #	  if ref_image:
   #	     ref_images = open(ref_image[0],'r').readlines()
   #	     ref_image = ", ".join(["%s" % k.split('\n')[0] for k in ref_images])
   #	  else:
   #	     ref_image = ''
   #	  ccdpar = glob(i+'/ccd.par')
   #	  if ccdpar:
   #	     lines = open(ccdpar[0],'r').readlines()
   #	     ron = float(lines[0].split('#')[0])
   #	     gain = float(lines[1].split('#')[0])
   #	  else:
   #	     ron = 0.0
   #	     gain = 1.0
   #	  s3par = glob(i+'/s3.*.par')
   #	  if s3par:
   #	     lines = open(s3par[0],'r').readlines()
   #	     use_reflist = int(lines[0].split('#')[0])
   #	     max_nimages = int(lines[1].split('#')[0])
   #	     fov = float(lines[9].split('#')[0])
   #	  else:
   #	     use_reflist = 0
   #	     max_nimages = 0
   #	     fov = 0.0
   #	  redconfig = glob(i+'/*.Red.Config')
   #	  if redconfig:
   #	     d = todict(redconfig[0])
   #	     add_reduction(event_name, lc_file=lc_file, timestamp=timestamp, ref_image=ref_image,
   #			    target_found=is_target_found, ron=ron, gain=gain,
   #			    oscanx1=int(d['oscanx1']), oscanx2=int(d['oscanx2']),
   #			    oscany1=int(d['oscany1']), oscany2=int(d['oscany2']),
   #			    imagex1=int(d['imagex1']), imagex2=int(d['imagex2']),
   #			    imagey1=int(d['imagey1']), imagey2=int(d['imagey2']),
   #			    minval=float(d['minval']), maxval=float(d['maxval']),
   #			    growsatx=int(float(d['growsatx'])), growsaty=int(float(d['growsaty'])),
   #			    coeff2=float(d['coeff2']), coeff3=float(d['coeff3']),
   #			    sigclip=float(d['sigclip']), sigfrac=float(d['sigfrac']),
   #			    flim=float(d['flim']), niter=int(d['s2niter']),
   #			    use_reflist=use_reflist, max_nimages=max_nimages,
   #			    max_sky=float(d['max_sky']), min_ell=float(d['min_ell']),
   #			    trans_type=d['transtype'], trans_auto=int(d['transauto']),
   #			    replace_cr=int(d['replacecr']), min_scale=float(d['min_scale']),
   #			    max_scale=float(d['max_scale']), fov=fov, star_space=int(float(d['star_space'])),
   #			    init_mthresh=float(d['init_mthresh']), smooth_pro=float(d['smooth_pro_s3']),
   #			    smooth_fwhm=float(d['smooth_fwhm_s3']),
   #			    var_deg=int(d['var_deg']), det_thresh=float(d['det_thresh']),
   #			    psf_thresh=float(d['psf_thresh']), psf_size=float(d['psf_size']),
   #			    psf_comp_dist=float(d['psf_comp_dist']),
   #			    psf_comp_flux=float(d['psf_comp_flux']), psf_corr_thresh=float(d['psf_corr_thresh']),
   #			    ker_rad=float(d['ker_rad']), lres_ker_rad=float(d['lres_ker_rad']),
   #			    subframes_x=int(d['subframes_x']), subframes_y=int(d['subframes_y']),
   #			    grow=float(d['grow']), ps_var=int(d['ps_var']),
   #			    back_var=int(d['back_var']), diffpro=int(d['diffpro']))
   #	  else:
   #	     continue
   #   except:
   #	  continue
   #    count = count + 1
   #    print count

    #Populate ObsRequest
    from datetime import datetime, timedelta
    import random
    count = 0
    # Ignore the Outside ROMEREA field
    field_list = Field.objects.all().order_by('name')[1:]
    track_id = '0000'+str(random.randint(10000,30000))
    req_id = '0000'+str(random.randint(40000,60000))
    for i in field_list:
        field_name = i.name
        request_type = random.choice(['A','M','M','L','L','L','L','L','L'])
        if request_type == 'A':
            t_sample = 20
            exptime = random.randint(10,300)
            time_expire = timezone.now()+timedelta(hours=24)
            which_inst = random.choice(['fl03', 'fl14', 'fl11'])
            grp_id = 'REA_'+str(random.randint(1,10))+str(random.randint(1,30))+'T'+str(random.uniform(0,24))
        elif request_type == 'M':
            t_sample = 60
            exptime = random.randint(10,300)
            time_expire = timezone.now()+timedelta(hours=24)
            which_inst = random.choice(['fl03', 'fl14', 'fl11'])
            grp_id = 'REA_'+str(random.randint(1,10))+str(random.randint(1,30))+'T'+str(random.uniform(0,24))
        else:
            t_sample = 420
            exptime = 300
            time_expire = timezone.now()+timedelta(hours=24)
            which_inst = random.choice(['fl15', 'fl16', 'fl12'])
            grp_id = 'ROME_'+str(random.randint(1,10))+str(random.randint(1,30))+'T'+str(random.uniform(0,24))

    add_request(field_name=field_name, t_sample=t_sample, exptime=exptime, timestamp=timezone.now(),
            time_expire=time_expire, pfrm_on = False,
            onem_on=True, twom_on=False, request_type=request_type, which_filter='SDSS-i',
            which_inst=which_inst, grp_id=grp_id, track_id=track_id, req_id=req_id,  n_exp=1)

    count = count + 1
    print(count)

    # Populate RobonetStatus
    count = 0
    ogle_events_list = EventName.objects.filter(name__contains="OGLE")
    for i in ogle_events_list:
        event_name = i.name
        add_status(event_name, timestamp=timezone.now(), status='AC', comment='',
                updated_by='', rec_cad=0, rec_texp=0, rec_nexp=0, rec_telclass='')
        count = count + 1
        print(count)

    # Populate DataFile database
    from astropy.time import Time
    from django.utils import timezone
    dat_list = glob(artemis+'data/*B17*I.dat')
    count = 0
    for i in dat_list:
        data = open(i).readlines()
        data = data[1:]
        if (data != []):
            shorthand_name = i.split('/')[-1][1:-5]
        if 'OB' in shorthand_name:
            event_name = shorthand_name.replace('OB'+year[2:],'OGLE-'+year+'-BLG-')
        if 'KB' in shorthand_name:
            event_name = shorthand_name.replace('KB'+year[2:],'MOA-'+year+'-BLG-')
        datafile = i
        last_upd = timezone.now()
        #last_obs = Time(float('245'+data[-1].split()[2]), format='jd').datetime
        last_hjd = float('245'+data[-1].split()[2])
        #last_obs = timezone.make_aware(last_obs, timezone.get_current_timezone())
        last_mag = float(data[-1].split()[0])
        ndata = len(data)-1
        tel_id = i.split('/')[-1][0:1]
        tel = site_dict[tel_id][-1]
        try:
            align_file = open(i.split('data')[0]+'model/'+i.split('data')[1].split('.')[0][2:-1]+'.align','r').readlines()
            baseline = float(align_file[0].split()[1])
            g = float(align_file[0].split()[2])
        except:
            baseline = 22.0
            g = 0.0e-05
            inst = ''
            filt = ''
        add_datafile(event_name=event_name, datafile=datafile, last_upd=last_upd,
            last_hjd=last_hjd, last_mag=last_mag, tel=tel, ndata=ndata,
            inst=inst, filt=filt, baseline=baseline, g=g)
        count = count + 1
        print(count)

   # Populate Tap database
   #import random
   #count = 0
   #ogle_events_list = EventName.objects.filter(name__contains="OGLE")
   #for i in ogle_events_list:
   #   event_name = i.name
   #   timestamp = timezone.now()
   #   priority = random.choice(['L','L','L','L','M','M','H','A'])
   #   tsamp = random.uniform(0.1,24.0)
   #   texp = random.randint(10,300)
   #   nexp = random.randint(1,10)
   #   telclass = random.choice(['1m','2m','0.4m'])
   #   inst = 'default'
   #   filt = 'default'
   #   imag = random.uniform(14.0,20.0)
   #   omega = random.uniform(0.0,10.0)
   #   err_omega = random.uniform(0.0,6.0)
   #   peak_omega = random.uniform(1.0,25.0)
   #   blended = random.choice([True,False,False])
   #   add_tap(event_name=event_name, timestamp=timestamp, priority=priority, tsamp=tsamp,
   #           texp=texp, nexp=nexp, telclass=telclass, imag=imag, omega=omega,
   #	      err_omega=err_omega, peak_omega=peak_omega, blended=blended)
   #   count = count + 1
   #   print count

    # Populate Image database
    import random
    from datetime import datetime, timedelta
    count = 0
    fields_list = Field.objects.all()
    for i in fields_list:
        field_name = fields_list[0].name
        for cnt in range(10):
            image_name = str(field_name)+'_img_'+str(cnt)
            date_obs = timezone.now()+timedelta(hours=random.uniform(-1000,1000))
            timestamp = timezone.now()
            inst_list = Instrument.objects.filter(name__contains='fl')
            inst_object = random.choice(inst_list)
            inst = inst_object.name
            tel = inst_object.telescope.name
            filt = 'SDSS-i'
            grp_id = 'ROME017'+str(random.randint(1,10))+str(random.randint(1,30))+'T'+str(random.uniform(0,24))
            track_id = '0000'+str(random.randint(10000,30000))
            req_id = '0000'+str(random.randint(40000,60000))
            airmass = random.uniform(1,2)
            avg_fwhm_bob = random.uniform(2,9)
            avg_sky = random.uniform(1000,6000)
            avg_sigsky = random.uniform(10,200)
            moon_sep = random.uniform(15,40)
            moon_phase = random.uniform(0,99)
            moon_up = random.choice([True,False])
            elongation = random.uniform(1,2)
            nstars = random.randint(60,600)
            ztemp = None
            quality = 'Rejected: High sky background'
            add_image(field_name=field_name, image_name=image_name, date_obs=date_obs, timestamp=timestamp, tel=tel, inst=inst,
                filt=filt, grp_id=grp_id, track_id=track_id, req_id=req_id, airmass=airmass, avg_fwhm=avg_fwhm_bob,
                avg_sky=avg_sky, avg_sigsky=avg_sigsky, moon_sep=moon_sep, moon_phase=moon_phase, moon_up=moon_up,
                elongation=elongation, nstars=nstars, ztemp=ztemp, quality=quality)

            count = count + 1
            print(count)
