import glob
import operational_instruments
from astropy.io import fits
from numpy.fft import fft2, ifft2
import sewpy
from astropy import wcs
from astropy.table import Table
from astropy.io import ascii
from astropy.time import Time
import pytz
import numpy as np
import os
import time 
import log_utilities
import datetime
import rome_telescopes_dict
import rome_filters_dict

import update_db_2 as update_db
from django.utils import timezone

class QuantityLimits(object):

	def __init__(self):

		self.sky_background_median_limit = 10000.0
		self.sky_background_std_limit = 200
		self.sky_background_minimum = 100
		self.sky_background_maximum = 5000
		self.minimum_moon_sep = 10
		self.minimum_number_of_stars = {'gp': 1000, 'rp': 2000, 'ip' : 4000}
		self.maximum_ellipticity = 0.4
		self.maximum_seeing = 2.0



class Image(object):

	def __init__(self, image_directory,image_output_origin_directory, image_name, logger ):
		
		self.image_directory = image_directory
		self.image_name = image_name

		self.origin_directory = image_output_origin_directory
		self.logger = logger
		self.banzai_bpm = None
		self.banzai_catalog = None
		
		try:

			images = fits.open(self.image_directory+self.image_name)
			
			for image in images:

				try :	
				
					if image.header['EXTNAME'] == 'BPM':
				self.x_shift
						self.banzai_bpm = image

					if image.header['EXTNAME'] == 'SCI':

						science_image = image

					if image.header['EXTNAME'] == 'CAT':

						self.banzai_catalog = image

				except :
				
					pass

			logger.info('Image successfully loaded')
		except:
			logger.error('I can not load the image!')
			
		

		self.data = science_image.data
		self.header = science_image.header
                self.oldheader = science_image.header.copy()
		self.camera = None
		self.sky_level = None
		self.sky_level_std = None
		self.sky_minimum_level = None
		self.sky_maximum_level = None
		self.number_of_stars = None
		self.ellipticity = None
		self.seeing = None
		self.quality_flags = []
                self.thumbnail_box_size = 60
                self.field_name = None
		self.x_shift = None
		self.y_shift = None


		self.header_date_obs = '1986-04-04T00:00:00.00' #dummy value
		self.header_telescope_site = None
		self.header_dome_id = None
		self.header_group_id = ''
		self.header_track_id = ''
		self.header_request_id = ''
		self.header_object_name = None
		self.header_moon_distance = None
		self.header_moon_status = False
		self.header_moon_fraction = None
		self.header_airmass = None
		self.header_seeing = None
		self.header_ccd_temp = None
		self.header_ellipticity = None
		self.header_sky_level = None
		self.header_sky_temperature = None
		self.header_sky_measured_mag = None

		

		self.find_camera()
		self.find_object_and_field_name()
		self.quantity_limits =  QuantityLimits()

		
	def process_the_image(self):

		#self.extract_header_statistics()
		#self.find_wcs_template()
                #self.generate_sextractor_catalog()
                #self.
                #self.update_image_wcs()

                #self.move_frame()
		pass	

        def update_image_wcs(self):
	    
	    try:
		    hdutemplate = fits.open(os.path.join(self.template_directory,self.template_name))
		    templateheader=hdutemplate[0].header
		    hdutemplate.close()
		    imageheader=self.header
		    #STORE OLD FITSHEADER AND ADJUST BASED ON TEMPLATE
		    imageheader['DPXCORR'] = self.x_shift
		    imageheader['DPYCORR'] = self.y_shift
		    imageheader['WCSRFCAT']  =   templateheader['WCSRFCAT'] 
		    imageheader['RA']        =   templateheader['RA']       
		    imageheader['DEC']       =   templateheader['DEC']      
		    imageheader['CRPIX1']    =   templateheader['CRPIX1'] 
		    imageheader['CRPIX2']    =   templateheader['CRPIX2'] 
		    imageheader['CRVAL1']    =   templateheader['CRVAL1'] 
		    imageheader['CRVAL2']    =   templateheader['CRVAL2'] 
		    imageheader['CD1_1']     =   templateheader['CD1_1']  
		    imageheader['CD1_2']     =   templateheader['CD1_2']  
		    imageheader['CD2_1']     =   templateheader['CD2_1']  
		    imageheader['CD2_2']     =   templateheader['CD2_2']
		    imageheader['CRPIX1']    =   self.x_new_center
		    imageheader['CRPIX2']    =   self.y_new_center
		    imageheader['CDELT1']    =   templateheader['CDELT1']   
		    imageheader['CDELT2']    =   templateheader['CDELT2']   
		    imageheader['CROTA1']    =   templateheader['CROTA1']   
		    imageheader['CROTA2']    =   templateheader['CROTA2']   
		    imageheader['SECPIX1']   =   templateheader['SECPIX1']  
		    imageheader['SECPIX2']   =   templateheader['SECPIX2']   
		    imageheader['WCSSEP']    =   templateheader['WCSSEP']
		    
		    self.logger.info('WCS header successfully updated')   
	    except:

		    self.logger.error('WCS header successfully updated')

	def find_wcs_template(self):'1986-04-04T00:00:00.00'


		field_name = self.field_name.replace('ROME-','')	
		template_name = 'WCS_template_' + field_name + '.fits'
                thumbnail_name = 'WCS_template_' + field_name + '.thumbnail'
                
		origin_directory = self.origin_directory
		template_directory = origin_directory + 'wcs_templates/'

		self.template_name = template_name		
		self.template_directory = template_directory
                try:
                        coord=np.loadtxt(os.path.join(self.template_directory,thumnail_name))
                        self.x_center_thumbnail_world=coord[0]
                        self.y_center_thumbnail_world=coord[1]
                except:
                        self.x_center_thumbnail_world=self.header['CRVAL1']
                        self.y_center_thumbnail_world=self.header['CRVAL2']
                        

	def find_camera(self):

		try:
			camera_name = self.image_name[9:13]
			self.camera = operational_instruments.define_instrument(camera_name)
			self.filter = self.header[self.camera.header_dictionnary['filter']]
			self.logger.info('Successfully find the associated camera')

		except:

			self.logger.error('I do not know this camera!')

	def find_object_and_field_name(self):
		
		try:

			self.object_name = self.header[self.camera.header_dictionnary['object']]
			self.field_name = self.object_name
			self.logger.info('Object name is : '+self.object_name)
			self.logger.info('And so the assiocated field : '+self.field_name)
		except:

			self.logger.error('I can not recognize the object name or/and field name!')

	def determine_the_output_directory(self):

		try:
			origin_directory = self.origin_directory

			if len(self.quality_flags) == 0:		
		
				quality_directory = 'good/'
			else:

				quality_directory = 'bad/'	


			if 'ROME' in self.header_group_id:
			
				mode_directory = 'rome/'

			else:

				mode_directory = 'rea/'

		
			site_directory = self.header_telescope_site +'/'

			the_filter = self.camera.filter_convention[self.filter] 
			filter_directory = the_filter +'/'
	
			camera_directory = self.camera.name +'/'

			field_directory = self.field_name +'/'


			output_directory = origin_directory + quality_directory + mode_directory + site_directory + \
					   camera_directory + filter_directory +  field_directory
		

			self.output_directory = output_directory
		        self.catalog_directory = origin_directory.replace('images','catalog0')
			self.logger.info('Successfully construct the output directory : '+self.output_directory)
			self.logger.info('Successfully construct the catalog directory : '+self.catalog_directory)
	
		except:
		
			self.logger.error('I can not construct the output directory!')


	def find_or_construct_the_output_directory(self):

		try :	

			flag = os.path.isdir(self.output_directory)

			if flag == True:	
			
				self.logger.info('Successfully find the output directory : '+self.output_directory)

			else :

				os.makedirs(self.output_directory)
				self.logger.info('Successfully mkdir the output directory : '+self.output_directory)

		except:

				self.logger.error('I can not find or mkdir the output directory!')		
	
	def find_WCS_offset(self):
		
		try:

		   self.x_new_center,self.y_new_center,self.x_shift,self.y_shift = xycorr(os.path.join(self.template_directory,self.template_name), self.data, 0.4)
		   self.update_image_wcs()
           	   self.logger.info('Successfully find the WCS correction')

		except:

		   self.logger.error('I failed to find the WCS correction')	
			 	
	
	def generate_sextractor_catalog(self):
           '''
           extracting a catalog from a WCS-recalibrated (!) image
           calling it through logging to obtain an astropy
           compliant output with logging...
           '''
	   
	   try:

		   extractor_parameters=['X_IMAGE','Y_IMAGE','BACKGROUND',
		                      'ELLIPTICITY','FWHM_WORLD','X_WORLD',
		                      'Y_WORLD','MAG_APER','MAGERR_APER']
		   extractor_config={'DETECT_THRESH':2.5,
		                  'ANALYSIS_THRESH':2.5,
		                  'FILTER':'Y',
		                  'DEBLEND_NTHRESH':32,
		                  'DEBLEND_MINCOUNT':0.005,
		                  'CLEAN':'Y',
		                  'CLEAN_PARAM':1.0,
		                  'PIXEL_SCALE':self.camera.pix_scale,
		                  'SATUR_LEVEL':self.camera.ADU_high,
		                  'PHOT_APERTURES':10,
		                  'DETECT_MINAREA':7,
		                  'GAIN':self.camera.gain,
		                  'SEEING_FWHM':self.header_seeing,
		                  'BACK_FILTERSIZE':3}
		   sew = sewpy.SEW(params=extractor_parameters,config=extractor_config)
		   sewoutput = sew(os.path.join(self.image_directory,self.image_name))
		   #APPEND JD, ATTEMPTING TO CALIBRATE MAGNITUDES..
		   catalog=sewoutput['table']     
		   tobs=Time([self.header['DATE-OBS']],format='isot',scale='utc')
		   calibration_pars={'gp':[1.0281267,29.315002],'ip':[1.0198562,28.13711],'rp':[1.020762,28.854443]}
		   if self.filter!=None:
		       calmag=catalog['MAG_APER']*calibration_pars[self.filter][0]+calibration_pars[self.filter][1]
		       calmag[np.where(catalog['MAG_APER']==99.)]=99.
		   catalog['MAG_APER_CAL']=calmag
		   catalog['FILTER']=[self.filter]*len(calmag)
		   catalog['JD']=np.ones(len(catalog))*tobs.jd
		   #APPEND JD AND CALIBRATED MAGNITUDES...
		   #ROUGH CALIBRATION TO VPHAS+
		   #gmag=instmag*1.0281267+29.315002
		   #imag=instmag*1.0198562+28.13711
		   #rmag=instmag*1.020762+28.854443
	
		   self.compute_stats_from_catalog(catalog)
		   self.catalog = catalog

		   #ascii.write(catalog,os.path.join('./',catname))
		   
		   self.logger.info('Sextractor catalog successfully produce')
		
	   except:

		    self.logger.error('I can not produce the Sextractor catalog!')

		
        def create_image_control_region(self):
               	
                w = wcs.WCS(self.header)
                py,px = w.wcs_world2pix(self.x_center_thumbnail_world,self.y_center_thumbnail_world,1)
		py = int(py)
		px = int(px)                
		try:
                    self.thumbnail=self.data[px-self.thumbnail_box_size/2:px+self.thumbnail_box_size/2,py-self.thumbnail_box_size/2:py+self.thumbnail_box_size/2]
      		    self.logger.info('Thumbnail successfully produce around the good position')
                except:
                    self.thumbnail=np.zeros((self.thumbnail_box_size,self.thumbnail_box_size))
                    self.logger.info('Thumbnail successfully produce around the center of the image')

        def compute_stats_from_catalog(self,catalog):

	    try:

		    self.sky_level=np.median(catalog['BACKGROUND'])
		    self.sky_level_std=np.std(catalog['BACKGROUND'])
		    self.sky_minimum_level=np.percentile(catalog['BACKGROUND'],1)
		    self.sky_maximum_level=np.max(catalog['BACKGROUND'])
		    self.number_of_stars=len(catalog)
		    self.ellipticity=np.median(catalog['ELLIPTICITY'])
		    self.seeing=np.median(catalog['FWHM_WORLD']*3600)
		    self.logger.info('Image quality statistics well updated')

	    except:

		    self.logger.error('For some reason, I can not update the image quality statistics!')



	def extract_header_statistics(self):


		desired_quantities = [ key for key,value in self.__dict__.items() if 'header' in key]

		for quantity in desired_quantities :

			try:
				dictionnary_key = quantity.replace('header_','')
				setattr(self, quantity, self.header[self.camera.header_dictionnary[dictionnary_key]])
			except:

				pass

		self.logger.info('Image header_quality statistics well updated from the header')


	def assess_image_quality(self):
		
		try:

			self.check_background()
			self.check_Moon()
			self.check_Nstars()
			self.check_ellipticity()
			self.check_seeing()
			self.logger.info('Quality flags well produced')

		except:

			self.logger.error('I can not assess the image quality, no quality flags produced!')

	def check_background(self):
		if self.sky_level:
			if self.sky_level > self.quantity_limits.sky_background_median_limit:

				self.quality_flags.append('High sky background')
		else:
			self.quality_flags.append('No sky level measured!')	
		
		if self.sky_level_std :			
			if self.sky_level_std > self.quantity_limits.sky_background_std_limit:
			

				self.quality_flags.append('High sky background variations')
		else:

			self.quality_flags.append('No sky level variations measured!')	
		
		if self.sky_minimum_level:
			if self.sky_minimum_level < self.quantity_limits.sky_background_minimum:

				self.quality_flags.append('Low minimum background')
		else:
			self.quality_flags.append('No minimum sky level measured!')	

		if self.quality_flags.append('No sky level variations measured!'):
	
			if self.sky_maximum_level > self.quantity_limits.sky_background_maximum:

				self.quality_flags.append('High maximum background')

		else:

			self.quality_flags.append('No maximum sky level measured!')
	
	def check_Moon(self):
		if self.header_moon_distance:
			if self.header_moon_distance < self.quantity_limits.minimum_moon_sep:

				self.quality_flags.append('Moon too close')

		else:
			self.quality_flags.append('No Moon distance measured!')	
	def check_Nstars(self):
		if self.number_of_stars:
			if self.number_of_stars < self.quantity_limits.minimum_number_of_stars[self.filter]:

				self.quality_flags.append('Low number of stars')
		else:
			
			self.quality_flags.append('No stars measured!')
	def check_ellipticity(self):

		if self.ellipticity:
			if self.ellipticity > self.quantity_limits.maximum_ellipticity:

				self.quality_flags.append('High ellipticity')
		else:
			self.quality_flags.append('No ellipticity measured!')	

	def check_seeing(self):
		if self.seeing:

			if self.seeing > self.quantity_limits.maximum_seeing:

				self.quality_flags.append('Bad seeing')
		else:
			self.quality_flags.append('No seeing measured!')	

        def check_if_image_in_database(self):
                
                return None

	def ingest_the_image_in_the_database(self):

		quality_flag = ' ; '.join(self.quality_flags)

		observing_date  = datetime.datetime.strptime(self.header_date_obs,'%Y-%m-%dT%H:%M:%S.%f')
		observing_date = observing_date.replace(tzinfo=pytz.UTC)

		try:
			telescope = self.header_telescope_site + self.header_dome_id
			telescope_name = rome_telescopes_dict.telescope_dict[telescope]
		except:

			telescope_name = ''

		try:

			camera_filter = rome_filters_dict.filter_dict[self.filter]
		except:

			camera_filter = ''

		try:
		

			moon_status_dictionnary = {'UP':True,'DOWN':False}

			moon_status = moon_status_dictionnary[self.header_moon_status]
		except:

			moon_status = False

		ingest_success = update_db.add_image(self.field_name, self.image_name, observing_date, 
						     timezone.now(), telescope_name, self.camera.name, 
						     camera_filter, self.header_group_id, self.header_track_id, 
						     self.header_request_id, self.header_airmass, self.seeing, 
						     self.sky_level, self.sky_level_std, self.header_moon_distance, 
                                                     self.header_moon_fraction, moon_status, 
                                                     self.ellipticity, self.number_of_stars, self.header_ccd_temp, 
			      			     self.x_shift, self.y_shift, quality_flag)  	
		

		if ingest_success == True:

			self.logger.info('Image successfully ingest in the DB')

		else:

			self.logger.warning('Image NOT ingest in the DB, the image probably already exists')

		return ingest_success


	def class_the_image_in_the_directory(self):


		#import pdb; pdb.set_trace()
		try :
			new_hdul = fits.HDUList()
		
			calibrated_image = fits.ImageHDU(self.data, header=self.header, name='calibrated')

			thumbnail_image = fits.ImageHDU(self.thumbnail, header=self.header, name='thumbnail')

			original_header = fits.PrimaryHDU(header=self.oldheader)

			
		
			new_hdul.append(calibrated_image)

			new_hdul.append(thumbnail_image)
			new_hdul.append(original_header)

			if self.banzai_catalog:

				new_hdul.append(self.banzai_catalog)
			
			if self.banzai_bpm:			

				new_hdul.append(self.banzai_bpm)

			new_hdul.writeto(self.output_directory+self.image_name, clobber=True)
			self.logger.info('Image '+self.image_name+' successfully place in the directory '+self.output_directory)
			sorting_success = True

		except  :

			self.logger.error('Something goes wrong when move the image to the directory!')
			sorting_success = False

		return sorting_success


	def class_the_catalog_in_the_directory(self):
		try:

		   catname=self.image_name.replace('.fits','.cat')

		   ascii.write(self.catalog,os.path.join(self.catalog_directory,catname))
		   self.logger.info('Catalog successfully moved to the catalog directory')

		except:
		   self.logger.error('The catalog can not be copied in the good directory!')			
		
def find_frames_to_process(new_frames_directory, logger):

	IncomingList = [i for i in os.listdir(new_frames_directory) if ('.fits' in i) and ('.fz' not in i)]

	
	if len(IncomingList) == 0 :

		
		return

	else :
		logger.info('I found '+str(len(IncomingList))+' frames to treat')
		return IncomingList




def process_new_images(new_frames_directory, image_output_origin_directory, logs_directory):
	


	config = {'log_directory':logs_directory, 'log_root_name':'reception_data'}
	logger = log_utilities. start_day_log( config, 'reception', console=False )
	NewFrames = find_frames_to_process(new_frames_directory, logger)
	
	if NewFrames :

		for newframe in NewFrames :

			start = time.time()
			newframe = newframe.replace(new_frames_directory, '')
			logger.info('')
			logger.info('Start to work on frame: '+newframe)
			image = Image(new_frames_directory, image_output_origin_directory, newframe, logger)
			image.extract_header_statistics()
			image.find_wcs_template()
			image.create_image_control_region()
			image.find_WCS_offset()
			image.generate_sextractor_catalog()
			image.assess_image_quality()
			image.determine_the_output_directory()
			image.find_or_construct_the_output_directory()
			success = image.ingest_the_image_in_the_database()

			if success == True:

				image.class_the_catalog_in_the_directory()
				sorting_success = image.class_the_image_in_the_directory()
				
				if sorting_success == True:

					os.remove(new_frames_directory+newframe)

				else:

					pass	
			
			
		log_utilities.end_day_log(logger)
	else :

		logger.info('')
		logger.info('No frames to treat, aboard!')
		log_utilities.end_day_log(logger)









def convolve(image, psf, ft_psf=None, ft_image=None, no_ft=None, correlate=None, auto_correlation=None):
   """
    NAME:
          CONVOLVE
    PURPOSE:
          Convolution of an image with a Point Spread Function (PSF)
    EXPLANATION:
          The default is to compute the convolution using a product of
          Fourier transforms (for speed).
   
    CALLING SEQUENCE:
   
          imconv = convolve( image1, psf, FT_PSF = psf_FT )
     or:
          correl = convolve( image1, image2, /CORREL )
     or:
          correl = convolve( image, /AUTO )
   
    INPUTS:
          image = 2-D np.array (matrix) to be convolved with psf
          psf = the Point Spread Function, (size < or = to size of image).
   
    OPTIONAL INPUT KEYWORDS:
   
          FT_PSF = passes out/in the Fourier transform of the PSF,
                  (so that it can be re-used the next time function is called).
          FT_IMAGE = passes out/in the Fourier transform of image.
   
          /CORRELATE uses the np.conjugate of the Fourier transform of PSF,
                  to compute the cross-correlation of image and PSF,
                  (equivalent to IDL function convol() with NO rotation of PSF)
   
          /AUTO_CORR computes the auto-correlation function of image using FFT.
   
          /NO_FT overrides the use of FFT, using IDL function convol() instead.
                  (then PSF is rotated by 180 degrees to give same result)
    METHOD:
          When using FFT, PSF is centered & expanded to size of image.
    HISTORY:
          written, Frank Varosi, NASA/GSFC 1992.
          Appropriate precision type for result depending on input image
                                  Markus Hundertmark February 2006
          Fix the bug causing the recomputation of FFT(psf) and/or FFT(image)
                                  Sergey Koposov     December 2006
   """

   n_params = 2
   psf_ft = ft_psf
   imft = ft_image
   noft = no_ft
   auto = auto_correlation
   
   sp = np.array(np.shape(psf_ft)) 
   sif = np.array(np.shape(imft))
   sim = np.array(np.shape(image))
   sc = sim / 2
   npix = np.array(image, copy=0).size
   
   if image.ndim!=2 or noft!=None:   
      if (auto is not None):   
         message("auto-correlation only for images with FFT", inf=True)
         return image
      else:   
         if (correlate is not None):   
            return convol(image, psf)
         else:
            return convol(image, rotate(psf, 2))
   
   if imft==None or (imft.ndim!=2) or imft.shape!=im.shape: #add the type check
      imft = ifft2(image)
   
   if (auto is not None):   
      return np.roll(np.roll(npix * np.real(fft2(imft * np.conjugate(imft))), sc[0], 0),sc[1],1)

   if (ft_psf==None or ft_psf.ndim!=2 or ft_psf.shape!=image.shape or 
            ft_psf.dtype!=image.dtype):
      sp = np.array(np.shape(psf))
      
      loc = np.maximum((sc - sp / 2), 0)         #center PSF in new np.array,
      s = np.maximum((sp / 2 - sc), 0)        #handle all cases: smaller or bigger
      l = np.minimum((s + sim - 1), (sp - 1))
      psf_ft = np.conjugate(image) * 0 #initialise with correct size+type according 
      #to logic of conj and set values to 0 (type of ft_psf is conserved)
      psf_ft[loc[1]:loc[1]+l[1]-s[1]+1,loc[0]:loc[0]+l[0]-s[0]+1] = \
                     psf[s[1]:(l[1])+1,s[0]:(l[0])+1]
      psf_ft = ifft2(psf_ft)
   
   if (correlate is not None):   
      conv = npix * np.real(fft2(imft * np.conjugate(psf_ft)))
   else:   
      conv = npix * np.real(fft2(imft * psf_ft))
   
   sc = sc + (sim % 2)   #shift correction for odd size images.
   
   return np.roll(np.roll(conv, sc[0],0), sc[1],1)

def correl_shift(reference, image):
    ''' This function calculates the revised
    central pixel coordinate for imgdata based
    on a cross correlation with refdata
    '''
    xcen = np.shape(reference)[0] / 2
    ycen = np.shape(reference)[1] / 2
    correl = convolve(np.matrix(reference),
                               np.matrix(image), correlate=1)
    xshift, yshift = np.unravel_index(np.argmax(correl), np.shape(correl))
    half = np.shape(correl)[0] / 2
    return yshift-ycen,xshift-xcen

def xycorr(pathref, image, edgefraction):
    '''
    For a given reference image path pathref
    and a given image path pathimg
    the central part with an edge length of
    edgefraction times full edge length is used
    to correlate a revised central pixel position
    '''

    hduref = fits.open(pathref)
    template_data = hduref[0].data
    noff = np.shape(template_data)
    if noff != np.shape(image):
        hduref.close()

        return 0, 0, 0, 0
    xcen = np.shape(template_data)[0] / 2
    ycen = np.shape(template_data)[1] / 2
    halfx = int(edgefraction * float(noff[0]))/2
    halfy = int(edgefraction * float(noff[1]))/2

    reduce_template = template_data[
        xcen - halfx:xcen + halfx, ycen - halfy:ycen + halfy]
    reduce_image = image[
        xcen - halfx:xcen + halfx, ycen - halfy:ycen + halfy]
    xc, yc = correl_shift(reduce_template, reduce_image)
    hduref.close()
    return -xc + xcen , -yc + ycen, xc, yc








