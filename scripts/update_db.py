################################################################################################################
# Collection of routines to update the RoboNet database tables
# Keywords match the class model fields in ../robonet_site/events/models.py
#
# Written by Yiannis Tsapras Sep 2015
# Last update: 
################################################################################################################

# Import dependencies
import os
import sys
sys.path.append('/home/Tux/ytsapras/robonet_site/')
#os.environ['DJANGO_SETTINGS_MODULE'] = 'robonet_site.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'robonet_site.settings')
from django.core import management
from django.conf import settings
from django.utils import timezone
from django import setup
setup()

from events.models import Event, Single_Model, Binary_Model, Data_File, Robonet_Log, Robonet_Reduction, Robonet_Request, Robonet_Status, Ogle_Detail, Moa_Detail, Kmt_Detail

################################################################################################################
def check_exists(event_name):
   """
   Check if event exists in database.
   
   Keyword arguments:
   event_name -- The event name (string, required)
   """
   if event_name.startswith("OGLE"): 
      successful = Event.objects.filter(ev_name_ogle=event_name).exists()
   elif event_name.startswith("MOA"):
      successful = Event.objects.filter(ev_name_moa=event_name).exists()
   elif event_name.startswith("KMT"):
      successful = Event.objects.filter(ev_name_kmt=event_name).exists()
   else:
      successful = False
   return successful

################################################################################################################
def check_coords(event_name, check_ra, check_dec):
   """
   Cross-survey identification check.
   Check if an event at these coordinates already exists in the database.
   
   Keyword arguments:
   event_name -- The event name (string, required)
   check_ra -- event RA. (string, required)
        	   e.g. "17:54:33.58"
   check_dec -- event DEC. (string, required)
        	   e.g. "-30:31:02.02"
   """

################################################################################################################
def add_new_event(event_name, event_ra, event_dec, bright_neighbour = False):
   """
   Add a new event to the database.
   
   Keyword arguments:
   ev_name_ogle -- OGLE name of event. (string, optional, default='...')
        	   e.g. "OGLE-2015-BLG-1234"
   ev_name_moa --  MOA name of event. (string, optional, default='...')
        	   e.g. "MOA-2015-BLG-123"
   ev_name_kmt -- KMT name of event. (string, optional, default='...')
        	   e.g. "KMT-2015-BLG-1234"
   ev_ra -- event RA. (string, required)
        	   e.g. "17:54:33.58"
   ev_dec -- event DEC. (string, required)
        	   e.g. "-30:31:02.02"
   bright_neighbour -- Is there a bright neighbour? (boolean, optional, 
                                                     default=False)
   """
   # Check if the event already exists in the database. If not, add it.
   if event_name.startswith("OGLE") and check_exists(event_name)==False:
      ev = Event(ev_name_ogle=event_name, ev_ra=event_ra, ev_dec=event_dec,
                 bright_neighbour = bright_neighbour)
      ev.save()
      successful = True
   elif event_name.startswith("MOA") and check_exists(event_name)==False:
      ev = Event(ev_name_moa=event_name, ev_ra=event_ra, ev_dec=event_dec,
                 bright_neighbour = bright_neighbour)
      ev.save()
      successful = True
   elif event_name.startswith("KMT") and check_exists(event_name)==False:
      ev = Event(ev_name_kmt=event_name, ev_ra=event_ra, ev_dec=event_dec,
                 bright_neighbour = bright_neighbour)
      ev.save()
      successful = True
   else:
      successful = False
   return successful

def update_data(event_name, datafile, last_upd, last_mag, tel, ver, ndat):
   """
   Add or Update a data file to the database.
   Uses the .dat files rsynced from ARTEMiS.
   
   Keyword arguments:
   event_name -- The event name (string, required)
   datafile -- Full path to the data file (string, required)
   last_upd -- datetime of last update. (datetime, required, 
                                         default=timezone.now())
   last_mag -- last recorded magnitude (float, required)
   tel -- telescope identifier (string, required)
   ver -- reduction version identifier (integer, required)
   ndat -- number of data points (integer, required)
   """
   # Check if the event already exists in the database.
   if event_name.startswith("OGLE") and check_exists(event_name)==True:
      # Get event identifier.
      ev = Event.objects.get(ev_name_ogle=event_name)
      ev.data_file_set.update_or_create(datafile=datafile,
                                        last_updated=last_upd,
                                        last_magnitude=last_mag,
					telescope=tel,
					version=ver,
					ndata=ndat)
      ev.save()
      successful = True
   elif event_name.startswith("MOA") and check_exists(event_name)==True:
      # Get event identifier.
      ev = Event.objects.get(ev_name_moa=event_name)
      ev.data_file_set.update_or_create(datafile=datafile,
                                        last_updated=last_upd,
					last_magnitude=last_mag,
					telescope=tel,
					version=ver,
					ndata=ndat)
      ev.save()
      successful = True
   elif event_name.startswith("KMT") and check_exists(event_name)==True:
      # Get event identifier.
      ev = Event.objects.get(ev_name_kmt=event_name)
      ev.data_file_set.update_or_create(datafile=datafile,
                                        last_updated=last_upd,
					last_magnitude=last_mag,
					telescope=tel,
					version=ver,
					ndata=ndat)
      ev.save()
      successful = True
   else:
      successful = False
   return successful

################################################################################################################
def ogle_details(event_name, Tmax, tau, umin, 
		 url_link, last_updated=timezone.now()):
   """
   Update or Add OGLE event details to the database. These are the survey event
   parameters as displayed on the survey website.
   
   Keyword arguments:
   event_name -- OGLE name of event. (string, required)
        	 e.g. "OGLE-2015-BLG-1234"
   Tmax -- time of maximum magnification.(float, required)
        	 e.g. 2457135.422
   tau -- event timescale (in days). (float, required)
   umin -- minimum impact parameter (in units of R_E). (float, required)
   last_updated -- datetime of last update. (datetime, required, 
                                             default=timezone.now())
        	 e.g. datetime(2015, 9, 23, 15, 26, 13, 104683, tzinfo=<UTC>)
   url_link -- URL link to OGLE survey event page (string, required)
   """
   # Check if the event already exists in the database.
   if check_exists(event_name)==True:
      # Get event identifier
      ev = Event.objects.get(ev_name_ogle=event_name)
      ev.ogle_detail_set.update_or_create(Tmax=Tmax, tau=tau, umin=umin,
                           last_updated=last_updated, url_link=url_link)
      ev.save()
      successful = True
   else:
      successful = False
   return successful

################################################################################################################
def moa_details(event_name, Tmax, tau, umin, 
                url_link, last_updated=timezone.now()):
   """
   Update or Add MOA event details to the database. These are the survey event
   parameters as displayed on the survey website.
   
   Keyword arguments:
   event_name -- MOA name of event. (string, required)
        	 e.g. "MOA-2015-BLG-123"
   Tmax -- time of maximum magnification.(float, required)
        	 e.g. 2457135.422
   tau -- event timescale (in days). (float, required)
   umin -- minimum impact parameter (in units of R_E). (float, required)
   last_updated -- datetime of last update. (datetime, required, 
                                             default=timezone.now())
        	 e.g. datetime(2015, 9, 23, 15, 26, 13, 104683, tzinfo=<UTC>)
   url_link -- URL link to MOA survey event page (string, required)
   """
   # Check if the event already exists in the database.
   if check_exists(event_name)==True:
      # Get event identifier
      ev = Event.objects.get(ev_name_moa=event_name)
      ev.moa_detail_set.update_or_create(Tmax=Tmax, tau=tau, umin=umin,
                           last_updated=last_updated, url_link=url_link)
      ev.save()
      successful = True
   else:
      successful = False
   return successful

################################################################################################################
def kmt_details(event_name, Tmax, tau, umin, 
                url_link, last_updated=timezone.now()):
   """
   Update or Add KMT event details to the database. These are the survey event
   parameters as displayed on the survey website.
   
   Keyword arguments:
   event_name -- KMT name of event. (string, required)
        	 e.g. "KMT-2015-BLG-1234"
   Tmax -- time of maximum magnification.(float, required)
        	 e.g. 2457135.422
   tau -- event timescale (in days). (float, required)
   umin -- minimum impact parameter (in units of R_E). (float, required)
   last_updated -- datetime of last update. (datetime, required, 
                                             default=timezone.now())
        	 e.g. datetime(2015, 9, 23, 15, 26, 13, 104683, tzinfo=<UTC>)
   url_link -- URL link to KMT survey event page (string, required)
   """
   # Check if the event already exists in the database.
   if check_exists(event_name)==True:
      # Get event identifier
      ev = Event.objects.get(ev_name_kmt=event_name)
      ev.kmt_detail_set.update_or_create(Tmax=Tmax, tau=tau, umin=umin,
                          last_updated=last_updated, url_link=url_link)
      ev.save()
      successful = True
   else:
      successful = False
   return successful

################################################################################################################
def single_lens_par(event_name, Tmax, e_Tmax, tau, e_tau, umin, e_umin, last_updated):
   """
   Update or Add Single Lens model parameters as estimated by ARTEMiS
   to the database.
   
   Keyword arguments:
   event_name -- KMT name of event. (string, required)
        	 e.g. "KMT-2015-BLG-1234"
   Tmax -- time of maximum magnification.(float, required)
        	 e.g. 2457135.422
   e_Tmax -- error in Tmax (float, required)
   tau -- event timescale (in days). (float, required)
   e_tau -- error in tau (float, required)
   umin -- minimum impact parameter (in units of R_E). (float, required)
   e_umin -- error in umin (float, required)
   last_updated -- datetime of last update. (datetime, required)
        	 e.g. datetime(2015, 9, 23, 15, 26, 13, 104683, tzinfo=<UTC>)
   """
   # Check if the event already exists in the database.
   if event_name.startswith("OGLE") and check_exists(event_name)==True:
      # Get event identifier
      ev = Event.objects.get(ev_name_ogle=event_name)
      ev.single_model_set.update_or_create(Tmax=Tmax, e_Tmax=e_Tmax, tau=tau,
                                           e_tau=e_tau, umin=umin, e_umin=e_umin,
					   last_updated=last_updated)
      ev.save()
      successful = True
   elif event_name.startswith("MOA") and check_exists(event_name)==True:
      # Get event identifier
      ev = Event.objects.get(ev_name_moa=event_name)
      ev.single_model_set.update_or_create(Tmax=Tmax, e_Tmax=e_Tmax, tau=tau,
                                           e_tau=e_tau, umin=umin, e_umin=e_umin,
					   last_updated=last_updated)
      ev.save()
      successful = True
   elif event_name.startswith("KMT") and check_exists(event_name)==True:
      # Get event identifier
      ev = Event.objects.get(ev_name_kmt=event_name)
      ev.single_model_set.update_or_create(Tmax=Tmax, e_Tmax=e_Tmax, tau=tau,
                                           e_tau=e_tau, umin=umin, e_umin=e_umin,
					   last_updated=last_updated)
      ev.save()
      successful = True
   else:
      successful = False
   return successful

################################################################################################################
def double_lens_par(event_name, Tmax, e_Tmax, tau, e_tau, umin, e_umin, 
                    q, e_q, s, e_s, rho, alpha, last_updated):
   """
   Update or Add Binary Lens model parameters as estimated by ARTEMiS
   to the database.
   
   Keyword arguments:
   event_name -- KMT name of event. (string, required)
        	 e.g. "KMT-2015-BLG-1234"
   Tmax -- time of maximum magnification.(float, required)
        	 e.g. 2457135.422
   e_Tmax -- error in Tmax (float, required)
   tau -- event timescale (in days). (float, required)
   e_tau -- error in tau (float, required)
   umin -- minimum impact parameter (in units of R_E). (float, required)
   e_umin -- error in umin (float, required)
   q -- mass ratio between the lensing components. (float, required)
   e_q -- error in q (float, required)
   s -- projected separation between the two lensing components
        (in units of R_E). (float, required)
   e_s -- error in s (float, required)
   rho -- finite source size (in units of R_E). (float, required)
   alpha -- trajectory angle w.r.t. binary axis (float, required)
   last_updated -- datetime of last update. (datetime, required)
        	 e.g. datetime(2015, 9, 23, 15, 26, 13, 104683, tzinfo=<UTC>)
   """
   # Check if the event already exists in the database.
   if event_name.startswith("OGLE") and check_exists(event_name)==True:
      # Get event identifier
      ev = Event.objects.get(ev_name_ogle=event_name)
      ev.binary_model_set.update_or_create(Tmax=Tmax, e_Tmax=e_Tmax, tau=tau,
                          e_tau=e_tau, umin=umin, e_umin=e_umin, mass_ratio=q,
			  e_mass_ratio=e_q, separation=s, e_separation=e_s,
			  rho_finite=rho, angle_a = alpha,
			  last_updated=last_updated)
      ev.save()
      successful = True
   elif event_name.startswith("MOA") and check_exists(event_name)==True:
      # Get event identifier
      ev = Event.objects.get(ev_name_moa=event_name)
      ev.binary_model_set.update_or_create(Tmax=Tmax, e_Tmax=e_Tmax, tau=tau,
                          e_tau=e_tau, umin=umin, e_umin=e_umin, mass_ratio=q,
			  e_mass_ratio=e_q, separation=s, e_separation=e_s,
			  rho_finite=rho, angle_a = alpha,
			  last_updated=last_updated)
      ev.save()
      successful = True
   elif event_name.startswith("KMT") and check_exists(event_name)==True:
      # Get event identifier
      ev = Event.objects.get(ev_name_kmt=event_name)
      ev.binary_model_set.update_or_create(Tmax=Tmax, e_Tmax=e_Tmax, tau=tau,
                          e_tau=e_tau, umin=umin, e_umin=e_umin, mass_ratio=q,
			  e_mass_ratio=e_q, separation=s, e_separation=e_s,
			  rho_finite=rho, angle_a = alpha,
			  last_updated=last_updated)
      ev.save()
      successful = True
   else:
      successful = False
   return successful

################################################################################################################
def update_log(event_name, image_name, timestamp, exptime,
               filter1, filter2, filter3, telescope, instrument, group_id,
	       track_id, req_id, airmass, fwhm, sky_bg, sd_bg, moon_sep,
	       elongation, nstars, quality):
   """
   Update Log with new image details in the database.
   
   Keyword arguments:
   event_name -- The event name. (string, required)
        	 e.g. "OGLE-2015-BLG-1234"
   image_name -- The image name. (string, required)
                 e.g. lsc1m005-kb78-20150922-0089-e10.fits
   timestamp -- Time of observation. (datetime, required)
                 e.g. datetime(2015, 9, 23, 15, 26, 13, 104683, tzinfo=<UTC>)
   exptime -- Exposure time. (float, required)
   filter1 -- Filter1 wheel identifier. (string, required)
   filter2 -- Filter2 wheel identifier. (string, required)
   filter3 -- Filter3 wheel identifier. (string, required)
   telescope -- Telescope identifier. (string, required)
                e.g. "1m0-05"
   instrument -- Instrument identifier.(string, required)
                e.g. "kb78"
   group_id -- Group identifier. (string, required)
                e.g. "RBN20150922T15.42112818"
   track_id -- Track identifier. (string, required)
                e.g. "0000110965"
   req_id -- Request identifier. (string, required)
                e.g. "0000427795"
   airmass -- Airmass. (float, required)
   fwhm -- average fwhm of stars. (in pixels) (float, required)
   sky_bg -- sky background value. (in ADU) (float, required)
   sd_bg -- error in sky_bg (float, required)
   moon_sep -- angular distance of centre of moon from target. (float, required)
   elongation -- estimated elongation of stars. (float, required)
   nstars -- number of stars found in image. (integer, required)
   quality -- image quality assessment. (string, required)
   """
   if event_name.startswith("OGLE") and check_exists(event_name)==True:
      # Get event identifier
      ev = Event.objects.get(ev_name_ogle=event_name)
      ev.robonet_log_set.update_or_create(event=event_name, image_name=image_name,
                           timestamp=timestamp, exptime=exptime, filter1=filter1,
			   filter2=filter2, filter3=filter3, telescope=telescope,
			   instrument=instrument, group_id=group_id, track_id=track_id,
			   req_id=req_id, airmass=airmass, fwhm=fwhm, sky_bg=sky_bg,
			   sd_bg=sd_bg, moon_sep=moon_sep, elongation=elongation,
			   nstars=nstars, quality=quality)
      ev.save()
      successful = True
   elif event_name.startswith("MOA") and check_exists(event_name)==True:
      ev = Event.objects.get(ev_name_moa=event_name)
      ev.robonet_log_set.update_or_create(event=event_name, image_name=image_name,
                           timestamp=timestamp, exptime=exptime, filter1=filter1,
			   filter2=filter2, filter3=filter3, telescope=telescope,
			   instrument=instrument, group_id=group_id, track_id=track_id,
			   req_id=req_id, airmass=airmass, fwhm=fwhm, sky_bg=sky_bg,
			   sd_bg=sd_bg, moon_sep=moon_sep, elongation=elongation,
			   nstars=nstars, quality=quality)
      ev.save()
      successful = True
   elif event_name.startswith("KMT") and check_exists(event_name)==True:
      ev = Event.objects.get(ev_name_kmt=event_name)
      ev.robonet_log_set.update_or_create(event=event_name, image_name=image_name,
                           timestamp=timestamp, exptime=exptime, filter1=filter1,
			   filter2=filter2, filter3=filter3, telescope=telescope,
			   instrument=instrument, group_id=group_id, track_id=track_id,
			   req_id=req_id, airmass=airmass, fwhm=fwhm, sky_bg=sky_bg,
			   sd_bg=sd_bg, moon_sep=moon_sep, elongation=elongation,
			   nstars=nstars, quality=quality)
      ev.save()
      successful = True
   else:
      successful = False
   return successful


################################################################################################################
def update_reduction(event_name, lc_file, timestamp, version, ref_image, ron=0.0, gain=1.0,
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
   event_name  -- The event name. (string, required)
        	 e.g. "OGLE-2015-BLG-1234"
   lc_file -- The lightcurve file. (string, required)
   timestamp -- The date the lightcurve file was created. (datetime, required)
                 e.g. datetime(2015, 9, 23, 15, 26, 13, 104683, tzinfo=<UTC>)
   version -- Reduction identifier (integer, required)
   ref_image -- Reference image used. (string, required)
   -+-+- DanDIA parameters -+-+-
   ron -- CCD readout noise (in ADU) (float, optional, default=0.0)
   gain -- CCD gain. (e-/ADU) (float, optional, default=1.0)
   oscanx1 -- Overscan strip coordinate x1 (integer, optional, default=1)
   oscanx2 -- Overscan strip coordinate x2 (integer, optional, default=50)
   oscany1 -- Overscan strip coordinate y1 (integer, optional, default=1)
   oscany2 -- Overscan strip coordinate y2 (integer, optional, default=500)
   imagex1 -- Image region coordinate x1 (integer, optional, default=51)
   imagex2 -- Image region coordinate x2 (integer, optional, default=1000)
   imagey1 -- Image region coordinate y1 (integer, optional, default=1)
   imagey2 -- Image region coordinate y2 (integer, optional, default=1000)
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
   if event_name.startswith("OGLE") and check_exists(event_name)==True:
      # Get event identifier
      ev = Event.objects.get(ev_name_ogle=event_name)
      ev.robonet_reduction_set.update_or_create(event=event_name, lc_file=lc_file,
                           timestamp=timestamp, version=version, ref_image=ref_image,
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
      ev.save()
      successful = True
   elif event_name.startswith("MOA") and check_exists(event_name)==True:
      ev = Event.objects.get(ev_name_moa=event_name)
      ev.robonet_reduction_set.update_or_create(event=event_name, lc_file=lc_file,
                           timestamp=timestamp, version=version, ref_image=ref_image,
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
      ev.save()
      successful = True
   elif event_name.startswith("KMT") and check_exists(event_name)==True:
      ev = Event.objects.get(ev_name_kmt=event_name)
      ev.robonet_reduction_set.update_or_create(event=event_name, lc_file=lc_file,
                           timestamp=timestamp, version=version, ref_image=ref_image,
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
      ev.save()
      successful = True
   else:
      successful = False
   return successful

################################################################################################################
def update_request(event_name, t_sample, exptime, timestamp=timezone.now(), onem_on=False,
                   twom_on=False, request_type='M', which_filter='ip'):
   """
   Update or Add robonet observing request to the database.
   
   Keyword arguments:
   event_name -- The event name. (string, required)
        	 e.g. "OGLE-2015-BLG-1234"
   t_sample -- Sampling interval to use. (in minutes) (float, required)
   exptime -- Exposure time to use. (in seconds) (integer, required) 
   timestamp -- The request submission time.
                (datetime, optional, default=timezone.now())
        	e.g. datetime(2015, 9, 23, 15, 26, 13, 104683, tzinfo=<UTC>)
   onem_on -- Observe on 1m network? (boolean, optional, default=False)
   twom_on -- Observe on 2m network? (boolean, optional, default=False)
   request_type -- Observation request class (string, optional, default='M')
                   ('T':'ToO','M':'Monitor', 'S':'Single')
   which_filter -- Filter identifier string. (string, optional, default='ip')
   """
   if event_name.startswith("OGLE") and check_exists(event_name)==True:
      # Get event identifier
      ev = Event.objects.get(ev_name_ogle=event_name)
      ev.robonet_request_set.update_or_create(event=event_name, timestamp=timestamp,
                   onem_on=onem_on, twom_on=twom_on, t_sample=t_sample, exptime=exptime,
		   request_type=request_type, which_filter=which_filter)
      ev.save()
      successful = True
   elif event_name.startswith("MOA") and check_exists(event_name)==True:
      ev = Event.objects.get(ev_name_moa=event_name)
      ev.robonet_request_set.update_or_create(event=event_name, timestamp=timestamp,
                   onem_on=onem_on, twom_on=twom_on, t_sample=t_sample, exptime=exptime,
		   request_type=request_type, which_filter=which_filter)
      ev.save()
      successful = True
   elif event_name.startswith("KMT") and check_exists(event_name)==True:
      ev = Event.objects.get(ev_name_kmt=event_name)
      ev.robonet_request_set.update_or_create(event=event_name, timestamp=timestamp,
                   onem_on=onem_on, twom_on=twom_on, t_sample=t_sample, exptime=exptime,
		   request_type=request_type, which_filter=which_filter)
      ev.save()
      successful = True
   else:
      successful = False
   return successful

################################################################################################################
def update_status(event_name, timestamp=timezone.now(), priority='L', status='AC',
                  comment='--', updated_by='--'):
   """
   Update or Add robonet status to the database.
   
   Keyword arguments:
   event_name -- The event name. (string, required)
        	 e.g. "OGLE-2015-BLG-1234"
   timestamp -- The request submission time.
                (datetime, optional, default=timezone.now())
        	e.g. datetime(2015, 9, 23, 15, 26, 13, 104683, tzinfo=<UTC>)
   priority -- Priority flag for human observers.
               (A:anomaly, H:high, M:medium, L:low)
               (string, optional, default='L')
   status -- Event status.
             (CH:check, AC:active, AN:anomaly, RE:rejected, EX:expired)
             (string, optional, default='AC')
   comment -- Comment field. (string, optional, default='--')
   updated_by -- Updated by which user? (string, optional, default='--')
   """
   if event_name.startswith("OGLE") and check_exists(event_name)==True:
      # Get event identifier
      ev = Event.objects.get(ev_name_ogle=event_name)
      ev.robonet_status_set.update_or_create(event=event_name, timestamp=timestamp,
                                 priority=priority, status=status, comment=comment,
		                 updated_by=updated_by)
      ev.save()
      successful = True
   elif event_name.startswith("MOA") and check_exists(event_name)==True:
      ev = Event.objects.get(ev_name_moa=event_name)
      ev.robonet_status_set.update_or_create(event=event_name, timestamp=timestamp,
                                 priority=priority, status=status, comment=comment,
		                 updated_by=updated_by)
      ev.save()
      successful = True
   elif event_name.startswith("KMT") and check_exists(event_name)==True:
      ev = Event.objects.get(ev_name_kmt=event_name)
      ev.robonet_status_set.update_or_create(event=event_name, timestamp=timestamp,
                                 priority=priority, status=status, comment=comment,
		                 updated_by=updated_by)
      ev.save()
      successful = True
   else:
      successful = False
   return successful

################################################################################################################
##TEST
def run_test():
   # Populate Event database
   from glob import glob
   ogle_event_list = glob('/work/Tux8/ytsapras/Data/RoboNet/ARTEMiS/PublishedParameters/2015/OGLE/*.model')
   count = 0
   for i in ogle_event_list:
      data = open(i).read().split()
      ev_ra = data[0]
      ev_dec = data[1]
      event_name = data[2].replace('OB15','OGLE-2015-BLG-')
      add_new_event(event_name, ev_ra, ev_dec)
      count = count + 1
      print count
   
   # Populate Ogle_Detail database
   from glob import glob
   ogle_event_list = glob('/work/Tux8/ytsapras/Data/RoboNet/ARTEMiS/PublishedParameters/2015/OGLE/*.model')
   count = 0
   for i in ogle_event_list:
      data = open(i).read().split()
      event_name = data[2].replace('OB15','OGLE-2015-BLG-')
      Tmax = 2450000.0+float(data[3])
      tau = float(data[5])
      umin = float(data[7])
      year, og_id = '20'+data[2][2:4], data[2].replace('OB15','blg-')
      url_link = 'http://ogle.astrouw.edu.pl/ogle4/ews/%s/%s.html' % (year, og_id)
      last_updated=timezone.now()
      ogle_details(event_name=event_name, Tmax=Tmax, tau=tau, umin=umin,
   		   url_link=url_link, last_updated=last_updated)
      count = count + 1
      print count
   
   # Populate Data_File database
   from astropy.time import Time
   ogle_dat_list = glob('/work/Tux8/ytsapras/Data/RoboNet/ARTEMiS/data/*OB15*I.dat')
   count = 0
   for i in ogle_dat_list:
      data = open(i).readlines()
      data = data[1:]
      if (data != []):
         event_name = i.split('/')[-1][1:-5].replace('OB15','OGLE-2015-BLG-')
         datafile = i
         last_upd = Time(float('245'+data[-1].split()[2]), format='jd').datetime
         last_upd = timezone.make_aware(last_upd, timezone.get_current_timezone())
         last_mag = float(data[-1].split()[0])
         ndat = len(data)-1
         tel = i.split('/')[-1][0:1]
         ver = 1
         update_data(event_name, datafile, last_upd, last_mag, tel, ver, ndat)
         count = count + 1
         print count
   
   # Populate Robonet_Status database
   count = 0
   ogle_events_list = Event.objects.filter(ev_name_ogle__contains="OGLE")
   for event_id in ogle_events_list:
      event_name = event_id.ev_name_ogle
      update_status(event_name, timestamp=timezone.now(), priority='L', status='AC',
                  comment='--', updated_by='--')
      count = count + 1
      print count
      
   # Populate Robonet_Request database
   import random
   count = 0
   ogle_events_list = Event.objects.filter(ev_name_ogle__contains="OGLE")
   for event_id in ogle_events_list:
      event_name = event_id.ev_name_ogle
      t_sample = random.uniform(0.1,24.0)
      exptime = random.randint(10,300)
      update_request(event_name, t_sample, exptime, timestamp=timezone.now(), onem_on=False,
                   twom_on=False, request_type='M', which_filter='ip')
      count = count + 1
      print count
   
   # Populate Robonet_Log database
   import random
   count = 0
   ogle_events_list = Event.objects.filter(ev_name_ogle__contains="OGLE")
   for event_id in ogle_events_list:
      event_name = event_id.ev_name_ogle
      image_name = "image_name.fits"
      timestamp = timezone.now()
      exptime = random.randint(10,300)
      filter1 = 'air'
      filter2 = 'ip'
      filter3 = 'air'
      telescope = '1m0-02'
      instrument = 'kb70'
      group_id = "RBN20150922T15.42112818"
      track_id = "0000110965"
      req_id = "0000427795"
      airmass = 1.33
      fwhm = 6.45
      sky_bg = 2143.5435347
      sd_bg = 80.543
      moon_sep = 18.43
      elongation = 1.2345234
      nstars = 120
      quality = "Rejected: High FWHM of stars "
      update_log(event_name, image_name, timestamp, exptime,
               filter1, filter2, filter3, telescope, instrument, group_id,
	       track_id, req_id, airmass, fwhm, sky_bg, sd_bg, moon_sep,
	       elongation, nstars, quality)
      count = count + 1
      print count
   
   # Populate Robonet_Reduction database
   count = 0
   ogle_events_list = Event.objects.filter(ev_name_ogle__contains="OGLE")
   for event_id in ogle_events_list:
      event_name = event_id.ev_name_ogle
      lc_file = 'lc_'+event_name+'_ip.t'
      timestamp = timezone.now()
      version = 1
      ref_image = 'reference.fits'
      update_reduction(event_name, lc_file, timestamp, version, ref_image, ron=0.0, gain=1.0,
                     oscanx1=1, oscanx2=50, oscany1=1, oscany2=500, imagex1=51, imagex2=1000,
		     imagey1=1, imagey2=1000, minval=1.0, maxval=55000.0, growsatx=0,
		     growsaty=0, coeff2=1.0e-06, coeff3=1.0e-12,
		     sigclip=4.5, sigfrac=0.5, flim=2.0, niter=4, use_reflist=0, max_nimages=1,
		     max_sky=5000.0, min_ell=0.8, trans_type='polynomial', trans_auto=0, replace_cr=0,
		     min_scale=0.99, max_scale=1.01,
		     fov=0.1, star_space=30, init_mthresh=1.0, smooth_pro=2, smooth_fwhm=3.0,
		     var_deg=1, det_thresh=2.0, psf_thresh=8.0, psf_size=8.0, psf_comp_dist=0.7,
		     psf_comp_flux=0.1, psf_corr_thresh=0.9, ker_rad=2.0, lres_ker_rad=2.0,
		     subframes_x=1, subframes_y=1, grow=0.0, ps_var=0, back_var=1, diffpro=0)
      count = count + 1
      print count
   
   # Populate Single_Model database
   from glob import glob
   from astropy.time import Time
   ogle_event_list = glob('/work/Tux8/ytsapras/Data/RoboNet/ARTEMiS/model/OB15*.model')
   count = 0
   for i in ogle_event_list:
      data = open(i).read().split()
      event_name = data[2].replace('OB15','OGLE-2015-BLG-')
      Tmax = 2450000.0+float(data[3])
      e_Tmax = float(data[4])
      tau = float(data[5])
      e_tau = float(data[6])
      umin = float(data[7])
      e_umin = float(data[8])
      if (data[12] != '0.0'):
         last_updated = Time(float('245'+data[12]), format='jd').datetime
         last_updated = timezone.make_aware(last_updated, timezone.get_current_timezone())
      else:
         last_updated = timezone.now()
      single_lens_par(event_name, Tmax, e_Tmax, tau, e_tau, umin, e_umin, last_updated)
      count = count + 1
      print count
   
   # Populate Robonet_Reduction database
   
   len(Event.objects.all())
