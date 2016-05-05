def get_conf(request):
   paths = {'artemis':'/work/Tux8/ytsapras/Data/RoboNet/ARTEMiS/',
            'robonet_site':'/home/Tux/ytsapras/robonet_site/',
	    'artemis_cols':'/work/Tux8/ytsapras/Data/RoboNet/ARTEMiS/',
	    'site_url':'http://127.0.0.1:8000/'
	    }
   answer = paths[request] 
   return answer
