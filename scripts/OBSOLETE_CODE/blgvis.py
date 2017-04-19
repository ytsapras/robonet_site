from update_db_2 import *
import warnings
warnings.filterwarnings('ignore',module='astropy.coordinates')

# Estimate the total visibility of the bulge for all three sites (in hours)
def blg_visibility(mlsites=['CPT','COJ','LSC']):
   vis=0.
   for site in mlsites:
      lonrobo=float(Telescope.objects.filter(site=site).values('longitude')[0]['longitude'])*u.deg
      latrobo=float(Telescope.objects.filter(site=site).values('latitude')[0]['latitude'])*u.deg
      ###WARNING IF ASTROPY FIXES THAT BUG, LON AND LAT NEED TO BE CHANGED AT SOME POINT!!!!
      RoboSite=EarthLocation(lat=lonrobo,lon=latrobo,height=float(Telescope.objects.filter(site=site).values('altitude')[0]['altitude'])*u.m)
      mlcrd=SkyCoord('18:50:00 -26:17:00',unit=(u.hourangle, u.deg))
      time=Time(datetime.utcnow(),scale='utc')
      mlalt=mlcrd.transform_to(AltAz(obstime=time,location=RoboSite))
      delta_midnight=linspace(-12, 12, 48)*u.hour
      mlaltazs=mlalt.transform_to(AltAz(obstime=time+delta_midnight,location=RoboSite))
      times=time+delta_midnight
      altazframe=AltAz(obstime=times,location=RoboSite)
      sunaltazs=get_sun(times).transform_to(altazframe)
      for idx in range(len(sunaltazs)):
         altsun= sunaltazs[idx].alt*u.deg
         altml=mlaltazs[idx].alt*u.deg
         if altsun<-18.*u.deg*u.deg and altml>30.*u.deg*u.deg:
            vis+=0.5
   return vis

