import glob
import operational_instruments
from astropy.io import fits
from numpy.fft import fft2, ifft2
import sewpy
from astropy import wcs
from astropy.table import Table
from astropy.io import ascii
from astropy.time import Time

class QuantityLimits(object):

	def __init__(self):

		self.sky_background_median_limit = 5000.0
		self.sky_background_std_limit = 200
		self.sky_background_minimum = 100
		self.sky_background_maximum = 5000
		self.minimum_moon_sep = 10
		self.minimum_number_of_stars = {'gp': 1000, 'rp': 2000, 'ip' : 4000}
		self.maximum_ellipticity = 0.4
		self.maximum_seeing = 2.0



class Image(object):

	def __init__(self, image_directory, image_name, image_output_origin_directory):
	
		self.image_directory = image_directory
		self.image_name = image_name
		self.origin_directory = image_output_origin_directory
		
		import pdb; pdb.set_trace()
		image = fits.open(self.image_directory+self.image_name)
		image = image[0]

		self.data = image.data
		self.header = image.header
                self.oldheader = image.header.copy()
		self.camera = None
		self.sky_level = None
		self.sky_level_std = None
		self.sky_minimum_level = None
		self.sky_maximum_level = None
		self.number_of_stars = None
		self.ellipticity = None
		self.seeing = None
		self.quality_flags = []
                self.thumbnail_box_size = 30
                

		self.header_telescope_site = None
		self.header_group_id = None
		self.header_track_id = None
		self.header_request_id = None
		self.header_object_name = None
		self.field_name = None
		self.header_moon_distance = None
		self.header_moon_status = None
		self.header_moon_fraction = None
		self.header_airmass = None
		self.header_seeing = None
		self.header_ccd_temp = None
		self.header_ellipticity = None
		self.header_sky_level = None
		self.header_sky_temperature = None
		self.header_sky_measured_mag = None
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

	def find_wcs_template(self):

		object_name = self.object_name.split('-')
		field_name = object_name[1] + '-' + object_name[2]
		template_name = 'WCS_template_' + field_name + '.fits'
                thumbnail_name = 'WCS_template_' + field_name + '.thumbnail'
                
		origin_directory = self.origin_directory
		template_directory = origin_directory + 'WCStemplates/'

		self.template_name = tenplate_name		
		self.template_directory = tenplate_directory
                try:
                        coord=np.loadtxt(os.path.join(self.template_directory,thumnail_name))
                        self.x_center_thumbnail_world=coord[0]
                        self.y_center_thumbnail_world=coord[1]
                except:
                        self.x_center_thumbnail_world=self.header['CRVAL1']
                        self.y_center_thumbnail_world=self.header['CRVAL2']
                        

	def find_camera(self):

		camera_name = self.image_name[9:13]
		self.camera = operational_instruments.define_instrument(camera_name)
		self.filter = self.header[self.camera.header_dictionnary['filter']]
	
	def find_object_and_field_name(self):
		
		self.object_name = self.header[self.camera.header_dictionnary['object']]
		self.field_name = self.object_name.replace('ROME-','')	

	def determine_the_output_directory(self):

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
				   camera_directory + filter_directory +  + field_directory
		

		self.output_directory = output_directory
                self.catalog_directory = output_directory.replace('images','catalog0')
	

	def find_WCS_offset(self):
           
           self.x_new_center,self.y_new_center,self.x_shift,self.y_shift = xycorr(os.path.join(self.template_directory,self.template_name), self.data, 0.3)
           self.update_image_wcs()
           

	def generate_sextractor_catalog(self):
           '''
           extracting a catalog from a WCS-recalibrated (!) image
           calling it through logging to obtain an astropy
           compliant output with logging...
           '''
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
                          'SEEING_FWHM':2.5,
                          'BACK_FILTERSIZE':3}
           sew = sewpy.SEW(params=extractor_parameters,config=extractor_config,sexpath='/usr/bin/sextractor')
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
           catname=self.name.replace('.fits','.cat')
           ascii.write(catalog,os.path.join(self.catalog_directory,catname))

        def create_image_control_region(self):
                
                w = wcs.WCS(self.header)
                pxcrd = w.wcs_world2pix([self.x_center_thumbnail_world,self.y_center_thumbnail_world])
                try:
                    self.thumbnail=self.data[pxcrd[1]-self.thumbnail_box_size/2:pxcrd[0]+self.thumbnail_box_size/2,pxcrd[0]-self.thumbnail_box_size/2:pxcrd[0]+self.thumbnail_box_size/2]
                except:
                    self.thumbnail=np.zeros((self.thumbnail_box_size,self.thumnail_box_size))
                    

        def compute_stats_from_catalog(self,catalog):

            self.sky_level=np.median(catalog['BACKGROUND'])
            self.sky_level_std=np.std(catalog['BACKGROUND'])
            self.sky_minimum_level=np.min(catalog['BACKGROUND'])
            self.sky_maximum_level=np.max(catalog['BACKGROUND'])
            self.number_of_stars=len(catalog)
            self.ellipticity=np.median(catalog['ELLIPTICITY'])
            self.seeing=np.median(catalog['FWHM_WORLD'])

	def extract_header_statistics(self):

		desired_quantities = [ key for key,value in self.__dict__.items() if 'header' in key]

		for quantity in desired_quantities :

			try:
				dictionnary_key = quantity.replace('header_','')
				setattr(self, quantity, self.header[self.camera.header_dictionnary[dictionnary_key]])
			except:

				pass
		

	def assess_image_quality(self):
		
		self.check_background()
		self.check_Moon()
		self.check_Nstars()
		self.check_ellipticity()
		self.check_seeing()

		

	def check_background(self):
	
		if self.sky_level > self.quantity_limits.sky_background_median_limit:

			self.quality_flags.append('High sky background')
					
		if self.sky_level_std > self.quantity_limits.sky_background_std_limit:
			

			self.quality_flags.append('High sky background variations')

		if self.sky_minimum_level < self.quantity_limits.sky_background_minimum:

			self.quality_flags.append('Low minimum background')

		if self.sky_maximum_level > self.quantity_limits.sky_background_maximum:

			self.quality_flags.append('High maximum background')

	def check_Moon(self):
	
		if self.header_moon_distance < self.quantity_limits.minimum_moon_sep:

			self.quality_flags.append('Moon too close')

		
	def check_Nstars(self):
	
		if self.number_of_stars < self.quantity_limits.minimum_number_of_stars[self.filter]:

			self.quality_flags.append('Low number of stars')

	
	def check_ellipticity(self):
	
		if self.ellipticity > self.quantity_limits.maximum_ellipticity:

			self.quality_flags.append('High ellipticity')

	def check_seeing(self):
	
		if self.seeing > self.quantity_limits.maximum_seeing:

			self.quality_flags.append('Bad seeing')

        def check_if_image_in_database(self):
                
                return None

	def ingest_the_image_in_the_database(self):

		return None


	def class_the_image_in_the_directory(self):
		
		try :
			return 'copy it'

		except RaiseError :

			return 'mkdir it'

def find_frames_to_process(new_frames_directory):

	IncomingList = glob.glob('*.fits') 
	
	if len(IncomingList) == 0 :

		print 'NoNewData here'
		return

	else :

		return IncomingList





def process_new_images(new_frames_directory, image_output_origin_directory):


	NewFrames = find_frames_to_process(new_frames_directory)

	if NewFrames :

		for newframe in NewFrames :
	
			image = open(newframe)
			image = Image(image_directory, image_name, data_structure_origin_directory)
			image.process_the_image(self)

	else :


		return 'Done'









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

def correl_shift(refdata, imgdata):
    ''' This function calculates the revised
    central pixel coordinate for imgdata based
    on a cross correlation with refdata
    '''
    xcen = np.shape(refdata[0].data)[0] / 2
    ycen = np.shape(refdata[0].data)[1] / 2
    correl = convolve.convolve(np.matrix(refdata[0].data),
                               np.matrix(imgdata[0].data), correlate=1)
    xshift, yshift = np.unravel_index(np.argmax(correl), np.shape(correl))
    half = np.shape(correl)[0] / 2
    return yshift-ycen,xshift-xcen

def xycorr(pathref, pathimg, edgefraction):
    '''
    For a given reference image path pathref
    and a given image path pathimg
    the central part with an edge length of
    edgefraction times full edge length is used
    to correlate a revised central pixel position
    '''
    hduref = fits.open(pathref)
    hdulist = fits.open(pathimg)
    noff = np.shape(hduref[0].data)
    if noff != np.shape(hdulist[0].data):
        hduref.close()
        hdulist.close()
        return 0, 0, 0
    xcen = np.shape(hduref[0].data)[0] / 2
    ycen = np.shape(hduref[0].data)[1] / 2
    halfx = int(edgefraction * float(noff[0]))
    halfy = int(edgefraction * float(noff[1]))

    hduref[0].data = hduref[0].data[
        xcen - halfx:xcen + halfx, ycen - halfy:ycen + halfy]
    hdulist[0].data = hdulist[0].data[
        xcen - halfx:xcen + halfx, ycen - halfy:ycen + halfy]
    xc, yc = correl_shift(hduref, hdulist)
    hdulist.close()
    hduref.close()
    return -xc + xcen ,-yc + ycen,xc,yc

