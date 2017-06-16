# -*- coding: utf-8 -*-
"""RoboTAP for REA

 Collection of routines to update the RoboNet database tables
 Keywords match the class model fields in ../robonet_site/events/models.py

 Last update: Correct Docker paths - Markus Hundertmark Apr 18
"""

# Import dependencies
import warnings
import time
import log_utilities
from update_db_2 import *
import numpy as np
from jdcal import gcal2jd
from django.db.models import Max
import log_utilities
from get_errors import update_err
from os import listdir

warnings.filterwarnings('ignore', module='astropy.coordinates')

def romerea_visibility_3sites_40deg(julian_date):
    """
    The ROME REA visibility function calculates the available
    time for the ROME field center for 3 sites (CTIO, SAAO, SSO)
    and an altitude limit of 40 degrees.
    The input requires the requested time in JD-2450000
    The output provides the visibility in hours;
    """
    yearoffset = round((7925. - julian_date) / 365.25)
    julian_date_reference_year = julian_date + yearoffset * 365.25
    par = [7.90148098e+03, 7.94700334e+03, 9.38610177e-03, -7.31977214e+01,
           9.74954459e-01, -9.32858229e-03, 7.51131184e+01]

    if julian_date_reference_year < par[0]:
        return min((julian_date_reference_year * par[2] + par[3]) * 24., par[4] * 24.)
    if julian_date_reference_year > par[1]:
        return min((julian_date_reference_year * par[5] + par[6]) * 24., par[4] * 24.)
    if julian_date_reference_year >= par[0] and julian_date_reference_year <= par[1]:
        return par[4] * 24.
    return 0.


def calculate_exptime_romerea(magin):
    """
    This function calculates the required exposure time
    for a given iband magnitude (e.g. OGLE I which also
    roughly matches SDSS i) based on a fit to the empiric
    RMS diagram of DANDIA light curves from 2016. The
    output is in seconds.
    """
    if magin < 14.7:
        mag = 14.7
    else:
        mag = magin
    lrms = 0.14075464 * mag * mag - 4.00137342 * mag + 24.17513298
    snr = 1.0 / np.exp(lrms)
    # target 4% -> snr 25
    return round((25. / snr)**2 * 300., 1)


def omegarea(time_requested, u0_pspl, te_pspl, t0_pspl, fs_pspl, fb_pspl):
    """
    This function calculates the priority for ranking
    microlensing events based on the planet probability psi
    as defined by Dominik 2009 and estimates the cost of
    observations based on an empiric RMS estimate
    obtained from a DANDIA reduction of K2C9 Sinistro
    observations from 2016. It expects the overhead to be
    60 seconds and also return the current Paczynski
    light curve magnification.
    """
    usqr = u0_pspl**2 + ((time_requested - t0_pspl) / te_pspl)**2
    pspl_deno = (usqr * (usqr + 4.))**0.5
    psip = 4.0 / (pspl_deno) - 2.0 / (usqr + 2.0 + pspl_deno)
    amp = (usqr + 2.) / pspl_deno
    mag = -2.5 * np.log10(fs_pspl * amp + fb_pspl)
    # 60s overhead
    return psip / (calculate_exptime_romerea(mag) + 60.), amp


def event_in_season(t0):
    """
    Checks if t0 is in the ROME/REA season
    """
    if t0>7844.5 and t0<8026.5:
        return True
    elif t0>8209.5 and t0<8391.5:
        return True
    elif t0>8574.5 and t0<8756.5:
        return True
    else:
        return False


def psplrea(u):
    """
    Calculates the magnification for a given source-lens
    separation u (PSPL)
    """
    usqr = float(u)**2
    pspl_deno = (usqr * (usqr + 4.))**0.5
    amp = (usqr + 2.) / pspl_deno
    return amp


def assign_tap_priorities(logger):
    """
    This function runs TAP and updates entries in the database.
    It only calculates the priority for active events if the reported Einstein time
    stays below 210 days assuming that ROME observations will
    characterise the event sufficiently. For the start events with A>50 are triggered
    as anomalies. TAP itself does not request observations, but sets flags
    pointing to relevant events. Blending and baseline parameters live with the
    datafile and need to be present for a succesful run. Currently, MOA parameters
    are not provided by ARTEMiS and require another processing step.
    """

    ut_current = time.gmtime()
    t_current = gcal2jd(ut_current[0], ut_current[1], ut_current[2])[
        1] - 49999.5 + ut_current[3] / 24.0 + ut_current[4] / (1440.)
    full_visibility = romerea_visibility_3sites_40deg(t_current)
    daily_visibility = 1.4 * full_visibility * 300. / 3198.

    # FILTER FOR ACTIVE EVENTS (BY DEFINITION WITHIN ROME FOOTPRINT0
    active_events_list = Event.objects.select_related().filter(status__in=['AC','MO'])
    logger.info('RoboTAP: Processing ' +
                str(len(active_events_list)) + ' active events.')
    
    nmissing = 0
    for event in active_events_list:
        event_id = event.pk
        event_name = EventName.objects.select_related().filter(event=event)[
            0].name
        timestamp = timezone.now()

	modelpath = '/somewhere/artemis/model/'
        if 'MOA' in event_name:
            eventname_short = 'KB' + event_name[6:8] + event_name[13:17]
        else:
            eventname_short = 'OB' + event_name[7:9] + event_name[14:18]

        if os.path.exists(os.path.join(modelpath, eventname_short + '.align')):
            filein = open(os.path.join(modelpath, eventname_short + '.align'))
            for fentry in filein:
                if 'OI' in fentry and 'O' in eventname_short:
                    alignpars = str.split(fentry)
                if 'KI' in fentry and 'K' in eventname_short:
                    alignpars = str.split(fentry)
            filein.close()

        if os.path.exists(os.path.join(modelpath, eventname_short + '.model')):
            filein = open(os.path.join(modelpath, eventname_short + '.model'))
            psplpars = str.split(filein.readline())
            filein.close()
            gfac = abs(float(alignpars[2]))
            ibase_pspl = float(alignpars[1])
            ftot_pspl = 10.0**(-0.4 * ibase_pspl)
            fs_pspl = ftot_pspl / (1.0 + gfac)
            fb_pspl = gfac * fs_pspl
            t0_pspl = float(psplpars[3])
            te_pspl = float(psplpars[5])
            u0_pspl = float(psplpars[7])
            g_pspl = gfac
            omega_now, amp_now = omegarea(
                t_current, u0_pspl, te_pspl, t0_pspl, fs_pspl, fb_pspl)
            err_omega = 0.
            omega_peak, amp_peak = omegarea(
                t0_pspl, u0_pspl, te_pspl, t0_pspl, fs_pspl, fb_pspl)
            # 1.4 is a fudge factor trying to compensate bad weather
            # 300./3185. is the time-allocation fraction which can and should
            # be updated based on the requested amount of time -> tb moved config.
            # SAMPLING TIME FOR REA IS 1h
            tsamp = 1.
            imag = -2.5 * np.log10(fs_pspl * amp_now + fb_pspl)
            texp = calculate_exptime_romerea(imag)
            cost1m = daily_visibility / tsamp * ((60. + texp) / 60.)

            err_omega = 0.

	    if ibase_pspl>0. and g_pspl<300.:
                add_tap(event_name=event_name, timestamp=timestamp, tsamp=tsamp,
                        texp=texp, nexp=1., imag=imag, omega=omega_now,
                        err_omega=err_omega, peak_omega=omega_peak,
                        visibility=full_visibility, cost1m=cost1m)
            else:
                add_tap(event_name=event_name, timestamp=timestamp, tsamp=tsamp,
                        texp=texp, nexp=1., imag=imag, omega=0.0,
                        err_omega=err_omega, peak_omega=omega_peak,
                       	visibility=full_visibility, cost1m=cost1m)

            #expire events -> deactivated
            #if t_current > te_pspl+t0_pspl:
            #    Event.objects.filter(event_id=event_id).update(status="EX")
        else:
            nmissing += 1
    if nmissing>0:
        update_err('run_rea_tap', 'Missing DataFile: '+str(nmissing)+' events')


def run_tap_prioritization(logger):

    """
    Sort events on RoboTAP and check a request can be made with 
    an assumed REA-LOW time allocation of 300 hours.
    For very high priority events A_now>500, the anomaly status
    can be set (not implemented yet).
    """

    ut_current = time.gmtime()
    t_current = gcal2jd(ut_current[0], ut_current[1], ut_current[2])[
        1] - 49999.5 + ut_current[3] / 24.0 + ut_current[4] / (1440.)
    full_visibility = romerea_visibility_3sites_40deg(t_current)
    daily_visibility = 1.4 * full_visibility * 300. / 3198.

    list_evnt = Event.objects.filter(status__in=['AC', 'MO'])
    output = []
    nmissing=0
    for ev in list_evnt:
        try:
            latest_ev_tap_val = Tap.objects.filter(
                event=ev).values().latest('timestamp')
            #print 'done', ev.id, ev.status
            output.append(latest_ev_tap_val)
        except Exception as errmsg:
            serrmsg = str(errmsg)
            logger.info('skipping '+str(ev.id)+' '+str(ev.status)+' '+str(EventName.objects.select_related().filter(event=ev.id)[0].name))
	    logger.info(serrmsg)
            nmissing=nmissing+1
    sorted_list = sorted(output, key=lambda k: k['omega'], reverse=True)

    # FIRST RESET ALL MONITORING EVENTS TO ACTIVE
    Event.objects.filter(status='MO').update(status="AC")
    # RESET ANOMALIES (PERMITS RE-CHECK)
    #logger.info('revert anomalies to active - no anomaly trigger active!')
    #Event.objects.filter(status='AN').update(status="AC")
    
    toverhead = 60.
    trun = 0.

    # CHECK ALLOCATED TIME AND SET MONITOR
    for idx in range(len(sorted_list)):
        # CHECK CURRENT MAGNIFICATION IF >500 SET IT TO ANOMALOUS 
        #IF IT NEVER WAS ANOMALOUS BEFORE
        if psplrea(SingleModel.objects.select_related().filter(event=sorted_list[idx]['event_id']).values().latest('last_updated')['umin'])>5000.:
            #Event.objects.filter(event_id=sorted_list[idx]['event_id']).update(status="AN")
            pass
        #Filter events with te>210, t0 in the season and Anow>1.34 (within Einstein radius)
        #ROME provides baseline data beyond that
        elif SingleModel.objects.select_related().filter(event=sorted_list[idx]['event_id']).values().latest('last_updated')['tau'] < 210. and psplrea(SingleModel.objects.select_related().filter(event=sorted_list[idx]['event_id']).values().latest('last_updated')['umin'])>1.34 and event_in_season(float(SingleModel.objects.select_related().filter(event=sorted_list[idx]['event_id']).values().latest('last_updated')['Tmax'])-2450000.):
            tsys = 24. * (float(sorted_list[idx]['texp']) + toverhead) / 3600.
            if trun + tsys < daily_visibility:
                logger.info('RoboTAP requests: Amax '+str(round(psplrea(SingleModel.objects.select_related().filter(event=sorted_list[idx]['event_id']).values().latest('last_updated')['umin']),2))+' '+EventName.objects.select_related().filter(event=sorted_list[idx]['event_id'])[0].name)
                #The model requires here to use id
                Event.objects.filter(id=sorted_list[idx]['event_id']).update(status="MO")
                #The model requires here to use event_id (consistency?)
                Tap.objects.filter(event_id=sorted_list[idx]['event_id']).values().update(priority='L')
                trun = trun + tsys
        
            

if __name__ == '__main__':
    #DIRECTORY TO BE OBTAINED FROM XML...
    logs_directory='/var/www/robonetsite/data/logs/2017/'
    #logs_directory='/home/Tux/ytsapras/Data/ROMEREA/logs/2017'
    script_config = {'log_directory':logs_directory, 
                     'log_root_name':'robotap_rea','lock_file':'robotap.lock'}
    logger = log_utilities.start_day_log( script_config, 'robotap', console=False )
    lock_status = log_utilities.lock(script_config, 'check', logger)
    if lock_status == 'clashing_lock':
        log_utilities.end_day_log(logger)
        update_err('run_rea_tap', 'Lock file found') 
        exit()
    else:
        #reset errors.txt to ok
        update_err('run_rea_tap', 'Status OK') 
    lock_status = log_utilities.lock( script_config, 'lock', logger)
    assign_tap_priorities(logger)
    run_tap_prioritization(logger)
    log_utilities.end_day_log(logger)
    lock_status = log_utilities.lock(script_config, 'unlock', logger)
