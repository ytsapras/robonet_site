def get_conf(request):
   paths = {'artemis':'/science/robonet/rob/Operations/Signalmen_output/',
            'robonet_site':'/home/robouser/Software/robonet_site/',
	    'artemis_cols':'/data/robonet/rob/ytsapras/',
	    'site_url':'http://127.0.0.1:8000/'
	    }
   answer = paths[request] 
   return answer
