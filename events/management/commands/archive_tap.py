from django.core.management.base import BaseCommand
from events.models import Event, Tap, EventName, Field, Operator, SingleModel
from django.core.exceptions import ObjectDoesNotExist
from os import path
from astropy.time import Time

class Command(BaseCommand):
    args = ''
    help = ''

    def add_arguments(self, parser):
        parser.add_argument('output_dir', nargs='+', type=str)

    def _extract_eventname(self, event):
        qs = EventName.objects.filter(event_id=event.pk)
        if len(qs) > 0:
            name = qs[0].name
            for entry in qs[1:]:
                name += '/' + entry.name
        else:
            return 'None'

        return name

    def _record_event(self,event, event_name, model):
        target = Field.objects.filter(pk=event.field.pk)[0]
        survey = Operator.objects.filter(pk=event.operator.pk)[0]
        if model == None:
            entry = event_name+' '+event.ev_ra+' '+event.ev_dec+' '+\
                survey.name+' '+target.name+' '+str(event.ibase)+' '+event.status+' '+\
                str(event.anomaly_rank)+' '+event.year+' '+repr(event.override)+' '+\
                '0.0'+' '+'0.0'+' '+'0.0'+' '+'0.0'+' '+\
                '0.0'+' '+'0.0'+' '+'0.0'+' '+'0.0'+' '+\
                '0.0'+' '+'0.0'+' '+'0.0'+' '+'0.0'+' '+\
                'None'+' '+'None'+' '+'0.0'+' '+'0.0'+'\n'
        else:
            last_update = model.last_updated.strftime("%Y-%m-%dT%H:%M:%S")
            entry = event_name+' '+event.ev_ra+' '+event.ev_dec+' '+\
                survey.name+' '+target.name+' '+str(event.ibase)+' '+event.status+' '+\
                str(event.anomaly_rank)+' '+event.year+' '+repr(event.override)+' '+\
                str(model.Tmax)+' '+str(model.e_Tmax)+' '+str(model.tau)+' '+str(model.e_tau)+' '+\
                str(model.umin)+' '+str(model.e_umin)+' '+str(model.rho)+' '+str(model.e_rho)+' '+\
                str(model.pi_e_n)+' '+str(model.e_pi_e_n)+' '+str(model.pi_e_e)+' '+str(model.e_pi_e_e)+' '+\
                model.modeler+' '+last_update+' '+str(model.tap_omega)+' '+str(model.chi_sq)+'\n'
        return entry

    def _cStr(self,datum):
        try:
            strDatum = str(datum)
        except TypeError:
            strDatum = repr(datum)
        return strDatum

    def _record_tap_entry(self,tap_record):
        date_gen = tap_record.timestamp.strftime("%Y-%m-%dT%H:%M:%S")
        ts = Time(date_gen,format='isot',scale='utc')
        mjd = str(ts.mjd)
        try:
            entry = date_gen + ' ' + mjd + ' ' + tap_record.priority + ' ' + \
                    self._cStr(tap_record.tsamp) + ' ' + self._cStr(tap_record.texp) + ' ' + \
                    self._cStr(tap_record.nexp) + ' ' + tap_record.telclass + ' ' + \
                    self._cStr(tap_record.imag) + ' ' + self._cStr(tap_record.omega) + ' ' + \
                    self._cStr(tap_record.err_omega) + ' ' + self._cStr(tap_record.peak_omega) + ' ' + \
                    self._cStr(tap_record.blended) + ' ' + self._cStr(tap_record.visibility) + ' ' + \
                    self._cStr(tap_record.cost1m) + ' ' + self._cStr(tap_record.passband) + ' ' + \
                    self._cStr(tap_record.ipp) + '\n'
        except TypeError:
            print(date_gen, mjd)
            for par in [tsamp, texp, nexp, telclass,imag, omega,err_omega, peak_omega, cost1m, visibility, passband, ipp]:
                print(par, getattr(tap_record, par))

        return entry

    def _summarize_tap(self,*args, **options):
        event_list = Event.objects.all()

        eventfile = open(path.join(options['output_dir'][0],'events','event_summary.log'), 'w')
        eventfile.write('# Entry records last SingleModel parameters for each event\n')
        eventfile.write('# Eventname    RA      Dec       I_base(mag)  Event_status   Anomaly_rank   Discovery_year   Tmax  err_Tmax   tau   err_tau   umin   err_umin  rho   err_rho  pi_e_n  err_pi_e_n  pi_e_e   err_pi_e_e  modeler  last_updated  tap_omega   chisq\n')

        for i,event in enumerate(event_list):
            if (i%100) == 0:
                print('-> Recording event '+str(i))

            event_name = self._extract_eventname(event)
            try:
                model = SingleModel.objects.filter(event=event.pk).latest('last_updated')
            except ObjectDoesNotExist:
                model = None
            eventfile.write(self._record_event(event, event_name, model))

            logfile = open(path.join(options['output_dir'][0],'events',event_name.replace('/','_')+'_tap_summary.log'), 'w')
            logfile.write('# Date_generated   Date_gen_MJD   Priority   Tsamp(hrs)   Texp(s)   Nexp   Telclass   Imag   Omega '+\
                'Err_omega   Peak_omega   Blended   Visibility    Cost1m   Passband   IPP\n')

            qs = Tap.objects.filter(event=event.pk)
            try:
                for entry in qs:
                    item = self._record_tap_entry(entry)
                    logfile.write(item)
            except TypeError:
                print('Cannot output TAP data for '+event_name)

            logfile.close()

        eventfile.close()

    def handle(self,*args, **options):
        self._summarize_tap(*args, **options)
