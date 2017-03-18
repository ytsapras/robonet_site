#################################################################################
# Collection of routines to update the RoboNet database tables
# Keywords match the class model fields in ../robonet_site/events/models.py
#
# Written by Yiannis Tsapras Oct 2016
# Last update: 
#################################################################################

# Import dependencies
from update_db_2 import *
import warnings
warnings.filterwarnings('ignore',module='astropy.coordinates')
 
def visibility(event,mlsites=['CPT','COJ','LSC']):
   vis=0.
   for site in mlsites:
      lonrobo=float(Telescope.objects.filter(site=site).values('longitude')[0]['longitude'])*u.deg
      latrobo=float(Telescope.objects.filter(site=site).values('latitude')[0]['latitude'])*u.deg
      ###WARNING IF ASTROPY FIXES THAT BUG, LON AND LAT NEED TO BE CHANGED AT SOME POINT!!!!
      RoboSite=EarthLocation(lat=lonrobo,lon=latrobo,height=float(Telescope.objects.filter(site=site).values('altitude')[0]['altitude'])*u.m)
      mlcrd=SkyCoord(str(event.ev_ra)+' '+str(event.ev_dec),unit=(u.hourangle, u.deg))
      time=Time(datetime.utcnow(),scale='utc')
      mlalt=mlcrd.transform_to(AltAz(obstime=time,location=RoboSite))
      delta_midnight=linspace(-12, 12, 24)*u.hour
      mlaltazs=mlalt.transform_to(AltAz(obstime=time+delta_midnight,location=RoboSite))
      times=time+delta_midnight
      altazframe=AltAz(obstime=times,location=RoboSite)
      sunaltazs=get_sun(times).transform_to(altazframe)
      altsun = interp1d(times.jd2,sunaltazs.alt*u.deg,kind='linear',fill_value=0.,bounds_error=False)
      altml = interp1d(times.jd2,mlaltazs.alt*u.deg,kind='linear',fill_value=0.,bounds_error=False)
      deltat=1.0/200.
      for timetest in arange(-0.5,+0.5,deltat):
         if altsun(timetest)<-18. and altml(timetest)>30.:
            vis+=deltat
      print vis
   return vis
#RUN TAP
def omegas(t,u0,te,t0,fs,fb,k2):
   k1=0.4
   g=fb/fs
   usqr=u0**2+((t-t0)/te)**2
   pspl_deno=(usqr*(usqr+4.))**0.5
   psip=4.0/(pspl_deno)-2.0/(usqr+2.0+pspl_deno)
   a=(usqr+2.)/pspl_deno
   return psip/(a**0.5*((a+g)*(1.0+g)*k2/(a*a)+k1))

def pspl(t,u0,te,t0):
   usqr=u0**2+((t-t0)/te)**2
   return (usqr+2.0)/(usqr*(usqr+4.0))**0.5

def run_tap():
   from jdcal import gcal2jd
   from math import log10
   ut_current=time.gmtime()
   t_current=gcal2jd(ut_current[0],ut_current[1],ut_current[2])[1]-49999.5+ut_current[3]/24.0+ut_current[4]/(1440.)
         
   active_events_list=Event.objects.select_related().filter(status='AC') 
   for event in active_events_list:
      event_id=event.pk
      event_name=EventName.objects.select_related().filter(event=event)[0].name
      
      t0=float(SingleModel.objects.select_related().filter(event=event).values().latest('last_updated')['Tmax'])
      #print event_name,e,e.pk,t0#,DataFile.objects.filter(event=e.pk).values()

      timestamp = timezone.now()
      telclass='1m'
      inst= 'default'
      filt= 'default'
      
      if DataFile.objects.filter(event=event).exists():

         u0=float(SingleModel.objects.select_related().filter(event=event).values().latest('last_updated')['umin'])
         te=float(SingleModel.objects.select_related().filter(event=event).values().latest('last_updated')['tau'])
         t0=float(SingleModel.objects.select_related().filter(event=event).values().latest('last_updated')['Tmax'])
         ibase=float(DataFile.objects.select_related().filter(event=event).values().latest('last_upd')['baseline'])
         g=float(DataFile.objects.select_related().filter(event=event).values().latest('last_upd')['g'])

#         print u0,te,t0,ibase,g,e.pk,event_name,e
         k2=10.0**(0.4*(ibase-18.))
         ftot=10.0**(-0.4*ibase)
         fs_ref=ftot/(1.0+g)                           
         fb_ref=g*fs_ref
         omega=omegas(t_current,u0,te,t0,fs_ref,fb_ref,k2)
         err_omega=0.
         peak_omega=omegas(t0,u0,te,t0,fs_ref,fb_ref,k2)
       
         munow=pspl(t_current,u0,te,t0)
         dailyvisibility=0.
         cost1m=0.
         if omega<6.0:
            priority='L'
         else:
            ##CALCULATE VISIBILITY FOR MEDIUM AND HIGH PRIORITY EVENTS
            dailyvisibility=24.0*visibility(event)
            print dailyvisibility,event

         if omega<10. and omega>6.:
            priority='M'
         if omega>10.:
            priority='H'
         sig_te=float(SingleModel.objects.filter(event=event).values().latest('last_updated')['e_tau'])
         winit=1./900
         if sig_te==0.:
            sig_te=0.001
   	    wte=1./sig_te**2
	
	    if munow==0.:
	       tsamp=-1.
	    else:
	       #USE MODIFIED SAMPLING INTERVAL FROM DOMINIK (FULLY DETERMINISTIC...)
               tsamp=(te*wte/26.+winit)/(winit+wte)*1.7374382779324/(munow)**0.5
         else:
  	    wte=1./sig_te**2
	    if munow==0.:
               tsamp=-1.
            else:
               tsamp=(te*wte/26.+winit)/(winit+wte)*1.7374382779324/(munow)**0.5
	 if munow==0.:
	    imag=99.
	 else:         
            #EMPIRICAL EXPTIME CALCULATOR BASED ON IMAG -> NEEDS TO BE REVISITED FOR 2016
            imag=-2.5*log10(fs_ref*munow+fb_ref)
         texp=10.**(0.43214*imag-4.79556)
         if texp>300.:
            texp=300.
         else:
            if texp<60.:
               texp=6.
	 #ALWAYS TAKE 2 EXPOSURES
         nexp = 2.
         overhead=2.
         cost1m=dailyvisibility/tsamp*(overhead+nexp*texp/60.)
         err_omega = 0.
	 #DEFINE A BLENDED EVENT AS g>0.5
         blended = g>0.5
     	 add_tap(event_name=event_name, timestamp=timestamp, priority=priority, tsamp=tsamp, 
              texp=texp, nexp=nexp, telclass=telclass, imag=imag, omega=omega, 
   	         err_omega=err_omega, peak_omega=peak_omega, blended=blended, visibility=dailyvisibility, cost1m=cost1m)

 
  
