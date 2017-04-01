import os
import sys
import socket
# Get hostname and set paths
host_name = socket.gethostname()
if 'cursa' in host_name:
   sys.path.append("/home/Tux/ytsapras/robonet_site/")
   site_url = 'http://127.0.0.1:8000/'
elif 'Rachel' in host_name:
   sys.path.append("/Users/rstreet/software/robonet_site/")
   site_url = 'http://127.0.0.1:8000/'
elif 'einstein' in host_name:
   sys.path.append("/var/www/robonetsite/")
   site_url = 'http://romerea.lco.global/'
else:
   sys.path.append("/var/www/robonetsite/")
   site_url = 'http://romerea.lco.global/'

from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'robonet_site.settings')
project_dir = settings.BASE_DIR
def get_conf(request):
   paths = {'artemis':os.path.join(project_dir,"artemis/ARTEMiS/"),
            'robonet_site':project_dir,
	    'artemis_cols':os.path.join(project_dir,'artemis/'),
	    #'site_url':'http://einstein.science.lco.global:8989/'
	    'site_url':site_url
	    }
   answer = paths[request] 
   return answer
