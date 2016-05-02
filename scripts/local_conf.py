def get_conf(request):
   paths = {'artemis':'/work/Tux8/ytsapras/Data/RoboNet/ARTEMiS/',
            'robonet_site':'/home/Tux/ytsapras/robonet_site/',
	    'artemis_cols':'/work/Tux8/ytsapras/Data/RoboNet/ARTEMiS/'
	    }
   answer = paths[request] 
   return answer
