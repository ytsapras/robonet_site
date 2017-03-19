#################################################################################
# Collection of routines to update the RoboNet database tables
# Keywords match the class model fields in ../robonet_site/events/models.py
#
# Written by Yiannis Tsapras Oct 2016
# Last update: TAP function by Markus Hundertmark March 2017
#################################################################################

# Import dependencies
from update_db_2 import *
import warnings
warnings.filterwarnings('ignore',module='astropy.coordinates')

def romerea_visibility_3sites_40deg(jdi):
    '''
    The ROME REA visibility function calculates the available
    time for the ROME field center for 3 sites (CTIO, SAAO, SSO)
    and an altitude limit of 40 degrees. 
    The input requires the requested time in JD-2450000
    The output provides the visibility in hours;
    '''
    yearoffset=round((7925.-jdi)/365.25)
    jd=jdi+yearoffset*365.25
    par=[7.90148098e+03,7.94700334e+03,9.38610177e-03,-7.31977214e+01,
         9.74954459e-01,-9.32858229e-03,7.51131184e+01]
    
    if jd<par[0]:
        return min((jd*par[2]+par[3])*24.,par[4]*24.)
    if jd>par[1]:
        return min((jd*par[5]+par[6])*24.,par[4]*24.)
    if jd>=par[0] and jd<=par[1]:
        return par[4]*24.
    return 0.

def calculate_exptime_romerea(magin):
   '''
   This function calculates the required exposure time
   for a given iband magnitude (e.g. OGLE I which also 
   roughly matches SDSS i) based on a fit to the empiric
   RMS diagram of DANDIA light curves from 2016. The
   output is in seconds.
   '''
    if magin<14.7:
        mag=14.7
    else:
        mag=magin
    lrms = 0.14075464 *mag*mag-4.00137342*mag+24.17513298
    snr= 1.0/np.exp(lrms)
    #target 4% -> snr 25
    return round((25./snr)**2*300.,1)

#at peak psi:
def omegarea(t,u0,te,t0,fs,fb):
   '''
   This function calculates the priority for ranking
   microlensing events based on the planet probability psi
   as defined by Dominik 2009 and estimates the cost of 
   observations based on an empiric RMS estimate 
   obtained from a DANDIA reduction of K2C9 Sinistro
   observations from 2016. It expects the overhead to be
   60 seconds and also return the current Paczynski 
   light curve magnification.
   '''
    usqr=u0**2+((t-t0)/te)**2
    pspl_deno=(usqr*(usqr+4.))**0.5
    psip=4.0/(pspl_deno)-2.0/(usqr+2.0+pspl_deno)
    a=(usqr+2.)/pspl_deno
    mag=-2.5*np.log10(fs*a+fb)
    #60s overhead
    return psip/(calculate_exptime(mag)+60.),a

 
def run_tap():
   '''
   This function runs TAP and updates entries in the database. 
   It only calculates the priority for active events if the reported Einstein time
   stays below 210 days assuming that ROME observations will 
   characterise the event sufficiently.
   '''
   import time
   from jdcal import gcal2jd
   from math import log10
   ut_current=time.gmtime()
   t_current=gcal2jd(ut_current[0],ut_current[1],ut_current[2])[1]-49999.5+ut_current[3]/24.0+ut_current[4]/(1440.)
   active_events_list=Event.objects.select_related().filter(status='AC') 
   #MISSING: FILTER FOR ROME-REA-EVENTS!!!
   for event in active_events_list:
      event_id=event.pk
      event_name=EventName.objects.select_related().filter(event=event)[0].name      
      t0=float(SingleModel.objects.select_related().filter(event=event).values().latest('last_updated')['Tmax'])
      timestamp = timezone.now()
      telclass='1m'
      inst= 'default'
      filt= 'default'      
      if DataFile.objects.filter(event=event).exists():
         single_model_pars=SingleModel.objects.select_related().filter(event=event).values().latest('last_updated')
         u0=float(single_model_pars['umin'])
         te=float(single_model_pars['tau'])
         t0=float(single_model_pars['Tmax'])
         #NB: blending and baseline magnitude are in a different file
         data_blending_pars=DataFile.objects.select_related().filter(event=event).values().latest('last_upd')
         ibase=float(data_blending_pars['baseline'])
         g=float(data_blending_pars['g'])
         ftot=10.0**(-0.4*ibase)
         fs=ftot/(1.0+g)                           
         fb=g*fs
         omega_now,amp_npw=omegarea(t_current,u0,te,t0,fs,fb)
         err_omega=0.
         omega_peak,amp_peak=omegarea(t0,u0,te,t0,fs,fb)
         dailyvisibility=1.4*romerea_visibility_3sites_40deg(t_current)*300./3185.
         #1.4 is a fudge factor trying to compensate bad weather
         #300./3185. is the time-allocation fraction which can and should
         #be updated based on the requested amount of time.
         cost1m=0.
         #SAMPLING TIME FOR REA IS 1h
         tsamp=1.
         #EXPOSURE TIME DEPENDS ON THE CURRENT MAGNIFICATION
         texp=calculate_exptime_romerea(-2.5*log10(fs*amp_now+fb)
         #REA IS REQUESTING A SINGLE OBSERVATION
         nexp = 1.
         cost1m=dailyvisibility/tsamp*((60.+nexp*texp)/60.)
         err_omega = 0.
	 #DEFINE A BLENDED EVENT AS g>0.5
         blended = g>0.5
     	 add_tap(event_name=event_name, timestamp=timestamp, priority=priority, tsamp=tsamp, 
              texp=texp, nexp=nexp, telclass=telclass, imag=imag, omega=omega, 
   	         err_omega=err_omega, peak_omega=peak_omega, blended=blended, visibility=dailyvisibility, cost1m=cost1m)

 
  
