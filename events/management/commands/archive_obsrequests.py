from django.core.management.base import BaseCommand
from events.models import ObsRequest, Field
from os import path

class Command(BaseCommand):
    args = ''
    help = ''

    def add_arguments(self, parser):
        parser.add_argument('output_dir', nargs='+', type=str)

    def _log_obs(self,obs,target):
        tsubmit = obs.timestamp.strftime("%Y-%m-%dT%H:%M:%S")
        texpire = obs.time_expire.strftime("%Y-%m-%dT%H:%M:%S")
        if obs.onem_on:
            network = '1m0'
        elif obs.pfrm_on:
            network = '0m4'
        else:
            network = '2m0'

        entry = target.name+' '+target.field_ra+' '+target.field_dec+' '+tsubmit+' '+texpire+' '+\
                obs.grp_id+' '+obs.track_id+' '+obs.req_id+' '+\
                network+' '+str(obs.t_sample)+' '+str(obs.exptime)+' '+obs.request_type+' '+\
                str(obs.which_site)+' '+str(obs.which_filter)+' '+str(obs.which_inst)+' '+\
                str(obs.n_exp)+' '+obs.request_status+'\n'
        return entry

    def _summarize_observations(self,*args, **options):
        obs_list = ObsRequest.objects.all()

        logfile = open(path.join(options['output_dir'][0],'observations_summary.log'), 'w')
        logfile.write('# Fieldname    RA      Dec       T_submit  T_expire  '+\
                'Group_ID   Track_ID   Req_ID   Tel_aperture(m)  T_sample(min)  Exptime(s)   Request_type '\
                'Site   Filter   Instrument   N_exp    Request_status\n')
        for obs in obs_list:
            target = Field.objects.filter(pk=obs.field.pk)[0]
            logfile.write(self._log_obs(obs,target))
        logfile.close()

    def handle(self,*args, **options):
        self._summarize_observations(*args, **options)
