### Define Instruments for the LCO project


import sys
thismodule = sys.modules[__name__]


def define_instrument(name):
""" Construct the correct instrument class according to the input name.
:param str name: a string which should match a class name.

:return: instrument
:rtype: instrument object like
"""

    try:

        instrument = getattr(thismodule, '{}'.format(name))

    except AttributeError:

        raise InstrumentException('Unknown instrument "{}"'.format(name))

    return instrument()


class InstrumentException(Exception):
     
	pass
					

class LCOSinistro(object):
""" Master class that defines common quantities for the LCO Sinistro cameras.      
"""
	def __init__(self):

		self.name = None
		self.type = 'Imager'	
		self.camera_model = 'Sinistro'
		self.pix_scale = 0.389
		self.gain = 1.0
		self.fov = 26.5*60
		self.ADU_low = 100
		self.ADU_high = 50000
		self.ron = 12
		self.ccd_temp = -100 # Celsius
		self.define_header_conventions()
		self.filter_convention = {'ip' : 'sdss-i', 'gp' : 'sdss-g', 'rp' : 'sdds-r'}

	def define_header_conventions(self):
		
		self.header_dictionnary = {}
		self.header_dictionnary['date_obs'] = 'DATE-OBS'
		self.header_dictionnary['time_start'] = 'UT_START'
		self.header_dictionnary['obs_type'] = 'OBSTYPE'
		self.header_dictionnary['exp_time'] = 'EXPTIME'
		self.header_dictionnary['filter'] = 'FILTER'
		self.header_dictionnary['ra'] = 'RA'
		self.header_dictionnary['dec'] = 'DEC'
		self.header_dictionnary['reference_epoch'] = 'CAT-EPOC'
		self.header_dictionnary['airmass'] = 'AIRMASS'	
		self.header_dictionnary['sky_level'] = 'L1MEDIAN'
		self.header_dictionnary['ron'] = 'RDNOISE' 	
		self.header_dictionnary['ro_speed'] = 'RDSPEED'
 		self.header_dictionnary['telescope_site'] = 'SITEID'
		self.header_dictionnary['dome_id'] = 'ENCID'
		self.header_dictionnary['track_id'] = 'TRACKNUM'
		self.header_dictionnary['request_id'] = 'REQNUM'
		self.header_dictionnary['group_id'] = 'GROUP'												
		self.header_dictionnary['instrument'] = 'INSTRUME'
		self.header_dictionnary['binning'] = 'CCDSUM'
		self.header_dictionnary['ccd_temp'] = 'CCDATEMP'
		self.header_dictionnary['object'] = 'OBJECT'
		self.header_dictionnary['moon_distance'] = 'MOONDIST'
		self.header_dictionnary['moon_status'] = 'MOONSTAT'
		self.header_dictionnary['moon_frac'] = 'MOONFRAC'
		self.header_dictionnary['seeing'] = 'AGFWHM'
		self.header_dictionnary['ellipticity'] = 'L1ELLIP'
		self.header_dictionnary['sky_temperature'] = 'WMSCLOUD'
		self.header_dictionnary['sky_measured_mag'] = 'WMSSKYBR'
		self.header_dictionnary['sky_expected_mag'] = 'SKYMAG'





	def update_values_from_header(self, image):
		
		from astropy.io import fits	
		data = fits.open(image)
		header = data[1].header

		self.ron = header[self.header_dictionnary['ron']]
	
		binning = header[self.header_dictionnary['binning']]
		self.x_binning = float(binning[0])
		self.y_binning = float(binning[2])

class fl03(LCOSinistro):
	
	def __init__(self) :

		
		super(fl03, self).__init__()
		self.name = 'fl03'

class fl04(LCOSinistro):
	
	def __init__(self) :

		
		super(fl04, self).__init__()
		self.name = 'fl04'

class fl05(LCOSinistro):
	
	def __init__(self) :

		
		super(fl05, self).__init__()
		self.name = 'fl05'

class fl06(LCOSinistro):
	
	def __init__(self) :

		
		super(fl06, self).__init__()
		self.name = 'fl06'


class fl08(LCOSinistro):
	
	def __init__(self) :

		
		super(fl08, self).__init__()
		self.name = 'fl08'
	
class fl11(LCOSinistro):
	
	def __init__(self) :

		
		super(fl11, self).__init__()
		self.name = 'fl11'
		
class fl12(LCOSinistro):
	
	def __init__(self) :

		
		super(fl12, self).__init__()
		self.name = 'fl12'

class fl14(LCOSinistro):
	
	def __init__(self) :

		
		super(fl14, self).__init__()
		self.name = 'fl14'

class fl15(LCOSinistro):
	
	def __init__(self) :

		
		super(fl15, self).__init__()
		self.name = 'fl15'

class fl16(LCOSinistro):
	
	def __init__(self) :

		
		super(fl16, self).__init__()
		self.name = 'fl16'
