import os, sys
lib_path = os.path.abspath(os.path.join('/home/etienne/Work/Microlensing/ROME/robonet_site/robonet_site/scripts'))
sys.path.append(lib_path)

from scripts import reception_data



def test_image_creation():

	test_image = reception_data.Image('./','lsc1m009-fl03-20161005-0041-e00.fits.fz','./')
	
	assert test_image.camera.name == 'fl03'

def test_check_background():

	test_image = reception_data.Image('./','lsc1m009-fl03-20161005-0041-e00.fits.fz','./')
	
	test_image.sky_level = 6000
        test_image.sky_level_std = 5000
	test_image.sky_minimum_level = 1
	test_image.sky_maximum_level = 10000
	
	test_image.check_background()
	
	assert test_image.quality_flags == ['High sky background', 'High sky background variations', 'Low minimum background', 'High maximum background']


def test_check_Moon():

	test_image = reception_data.Image('./','lsc1m009-fl03-20161005-0041-e00.fits.fz','./')
	
	test_image.header_moon_distance = 1.6
      
	
	test_image.check_Moon()
	
	assert test_image.quality_flags == ['Moon too close']

def test_check_Nstars():

	test_image = reception_data.Image('./','lsc1m009-fl03-20161005-0041-e00.fits.fz','./')
	
	test_image.number_of_stars = 12
      
	
	test_image.check_Nstars()
	
	assert test_image.quality_flags == ['Low number of stars']

def test_check_ellipticity():

	test_image = reception_data.Image('./','lsc1m009-fl03-20161005-0041-e00.fits.fz','./')
	
	test_image.ellipticity = 0.8
      
	
	test_image.check_ellipticity()
	
	assert test_image.quality_flags == ['High ellipticity']

def test_check_seeing():

	test_image = reception_data.Image('./','lsc1m009-fl03-20161005-0041-e00.fits.fz','./')
	
	test_image.seeing = 5.8
      
	
	test_image.check_seeing()
	
	assert test_image.quality_flags == ['Bad seeing']


