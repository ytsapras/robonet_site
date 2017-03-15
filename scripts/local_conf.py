import os
from django.conf import settings
project_dir = settings.BASE_DIR
def get_conf(request):
   paths = {'artemis':os.path.join(project_dir,"artemis/ARTEMiS/"),
            'robonet_site':project_dir,
	    'artemis_cols':os.path.join(project_dir,'artemis/'),
	    'site_url':'http://einstein.science.lco.global:8989/'
	    #'site_url':'http://127.0.0.1:8000/'
	    }
   answer = paths[request] 
   return answer
