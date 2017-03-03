import os
def get_conf(request):
   paths = {'artemis':os.getcwd()+'/artemis/',
            'robonet_site':os.getcwd()+'../robonet_site/',
	    'artemis_cols':os.getcwd()+'artemis/',
	    'site_url':'http://127.0.0.1:8000/'
	    }
   answer = paths[request] 
   return answer
