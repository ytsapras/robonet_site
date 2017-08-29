# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 02:49:13 2017

@author: ytsapras

Example call from command line:
./manage.py  set_event_status OGLE-2017-BLG-1527 EX
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from events.models import Event, EventName
from sys import exit
from scripts import update_db_2, query_db

class Command(BaseCommand):
    help = 'Sets the status of a specific event'
        
    def add_arguments(self, parser):
        parser.add_argument('eventname', nargs='+', type=str)
        parser.add_argument('new_status', nargs='+', type=str)

    def handle(self,*args, **options):
        #print options
        try:
            event_id = EventName.objects.all().filter(name=options['eventname'][0])[0].event_id
	    event = Event.objects.get(id=event_id)
	except:
	    raise CommandError("Event %s does not exist" % str(options['eventname'][0]))
	ev_old_status = event.status
        print ' -> Resetting status of event '+str(options['eventname'][0])+', currently: '+str(ev_old_status)
        event.status=options['new_status'][0]
        event.save()
        event = Event.objects.get(id=event_id)
        print ' -> New status set to: '+str(event.status)

