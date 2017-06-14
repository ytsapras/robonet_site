# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 11:09:40 2017

@author: rstreet
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import datetime
from scripts import artemis_subscriber, query_db

class Command(BaseCommand):
    args = ''
    help = ''
    
    def add_arguments(self, parser):
        parser.add_argument('data_path', nargs='+', type=str)
        
    def _check_event_cross_matching(self,*args,**options):
        data_path = options['data_path'][0]
        year = str(datetime.utcnow().year)[2:]
        model_files = path.join(data_path,'??'+year+'*.model')
        for model_path in model_files:
            (event, last_modified) = artemis_subscriber.read_artemis_model_file(model_path)
            
            (dbevent,message) = query_db.get_event_by_name(event.name)
            
            if dbevent == None:
                dbevent = query_db.get_event_by_position(ra_str,dec_str)
                print event.name+' not recognized by DB, checcking by sky position...'
                
                # If the event name is not recognised but the position is, 
                # the event name needs to be added to the DB:
                if dbevent != None:
                    operator = Operator.objects.filter(name=self.origin)[0]
                    (status, response) = update_db_2.add_event_name(event=dbevent,\
                                                            operator=operator,\
                                                            name=event.name)
                    print '-> Added event name: ',status, response
                else:
                    print '-> New event, will be added by subscriber'
                    
    def handle(self,*args, **options):
        self._check_event_cross_matching(*args,**options)
