# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 10:52:17 2017

@author: rstreet
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from events.models import Event, EventName, DataFile
from sys import exit
from os import path
from scripts import update_db_2, query_db

class Command(BaseCommand):
    help = ''
    
    def add_arguments(self, parser):
        parser.add_argument('eventname', nargs='+', type=str)
        
    def _check_datafiles_for_event(self,*args, **options):
        event_name = options['eventname'][0]
        print event_name
        
        par_list = ['datafile', 'last_upd', 'last_hjd','last_mag',\
                                'tel', 'inst', 'filt', 'baseline', 'g']
        
        if str(event_name).upper() == 'ALL':
            print('Checking datafiles for all events...')
            events = Event.objects.all()
            n_start_events = len(events)
            datafiles = DataFile.objects.all()
            n_start_files = len(datafiles)
            n_rm = 0
            for e in events:
                datafiles = DataFile.objects.filter(event=e)
                if len(datafiles) > 1:
                    ename_list = query_db.get_event_names(e)
                    ename = query_db.combine_event_names(ename_list)
                    print(str(len(datafiles))+' datafiles for event '+ename)
                    
                    file_names = []
                    for f1 in datafiles:
                        file_names.append(f1.datafile)
                    if len(file_names) > len(set(file_names)):
                        print(' -> Matching datafiles found')
                        for d1 in datafiles:
                            print(d1.pk, d1.datafile, d1.last_upd, \
                                        d1.ndata, d1.last_hjd, d1.last_mag, \
                                        d1.tel, d1.inst, d1.filt, d1.baseline, \
                                        d1.g)
                        checked = []
                        for i,f1 in enumerate(file_names):
                            print(' --> Looking for matches for '+path.basename(f1))
                            try:
                                for j,f2 in enumerate(file_names):
                                    if f2 not in checked:
                                        if f1 == f2 and i != j:
                                            d1 = datafiles[i]
                                            d2 = datafiles[j]
                                            print(' --> Matched '+str(i)+', '+str(d1.pk)+' '\
                                                    +path.basename(d1.datafile)+\
                                                    ' with '+str(j)+', '+str(d2.pk)+' '+\
                                                    path.basename(d2.datafile))
                                                    
                                            identical = True
                                            for par in par_list:
                                                if getattr(d1,par) != getattr(d2,par):
                                                    identical = False
                                            
                                            if identical == True and d1.pk != d2.pk:
                                                print('REMOVING ONE OF IDENTICAL ENTRIES:')
                                                n_rm += 1
                                                print(d1.pk, d1.datafile, d1.last_upd, \
                                                    d1.ndata, d1.last_hjd, d1.last_mag, \
                                                    d1.tel, d1.inst, d1.filt, d1.baseline, \
                                                    d1.g)
                                                print(d2.pk, d2.datafile, d2.last_upd, \
                                                    d2.ndata, d2.last_hjd, d2.last_mag, \
                                                    d2.tel, d2.inst, d2.filt, d2.baseline, \
                                                    d2.g)
                                                if d1.pk == None or d2.pk == None:
                                                    print(' --> SKIPPING DELETION: incomplete DB entry suggests DB write in progress')
                                                elif d1.pk > d2.pk and d1.pk != None and d2.pk != None:
                                                    print(' --> Removing '+str(d1.pk))
                                                    d1.delete()
                                                elif d1.pk < d2.pk and d1.pk != None and d2.pk != None:
                                                    print(' --> Removing '+str(d2.pk))
                                                    d2.delete()
                                            
                            except ValueError:
                                pass
                            checked.append(f1)
                    else:
                        print (' -> All files are distinct')
                
            events = Event.objects.all()
            n_end_events = len(events)
            datafiles = DataFile.objects.all()
            n_end_files = len(datafiles)
            print('Completed clean-up:')
            print('Started with '+str(n_start_events)+' events with '+str(n_start_files))
            print('Finished with '+str(n_end_events)+' events with '+str(n_end_files))
            print('Removed '+str(n_rm)+' datafile entries')
            
        elif update_db_2.check_exists(event_name)==True:
            event_id = EventName.objects.get(name=event_name).event_id
            event = Event.objects.get(id=event_id)
            datafiles = DataFile.objects.filter(event=event)
            for d in datafiles:
                
                print d.pk, d.datafile, d.last_upd, d.ndata, d.last_hjd, \
                    d.last_mag, d.tel, d.inst, d.filt, d.baseline, d.g
        else:
            print 'Event name not recognized by DB'
            
            
    def handle(self,*args, **options):
        self._check_datafiles_for_event(*args,**options)
