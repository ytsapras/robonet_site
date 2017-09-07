import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import collections
from datetime import timedelta
from django.utils import timezone

from bokeh.plotting import figure, show, output_file,gridplot,vplot
from bokeh.models import ColumnDataSource, HoverTool, LinearColorMapper, Legend,CheckboxGroup
from bokeh.models import FixedTicker,PrintfTickFormatter
from bokeh.embed import components
from bokeh.resources import CDN



import update_db_2 as updb
import rome_fields_dict as fields_radec
import matplotlib
import datetime

limit = 14*3

list_of_images = updb.Image.objects.filter(date_obs__range=[timezone.now()-timedelta(days=limit),timezone.now()], grp_id__contains='ROME')
fig,ax = plt.subplots(2,1)

COORDS = []
COUNTS = []
for i in np.arange(1,21):

	number = str(i).zfill(2)
	
	sub_list = [j for j in list_of_images if j.field.name == 'ROME-FIELD-'+number]

	ra = float(fields_radec.field_dict['ROME-FIELD-'+number][0])
	dec = float(fields_radec.field_dict['ROME-FIELD-'+number][1])
	ax[0].text(ra,dec,'ROME-FIELD-'+number)
	COORDS.append((ra,dec))
	COUNTS.append(len(sub_list))
	

COORDS = np.array(COORDS)

aa = ax[0].scatter(COORDS[:,0],COORDS[:,1],c=COUNTS,marker = 's',s=500)

ax[1].bar(np.arange(1,21),COUNTS)
fig.colorbar(aa,ax = ax[0])
ax[0].invert_xaxis()

list_of_images_i = updb.Image.objects.filter(date_obs__range=[timezone.now()-timedelta(days=limit),timezone.now()], grp_id__contains='ROME',filt__contains = 'i')
list_of_images_r = updb.Image.objects.filter(date_obs__range=[timezone.now()-timedelta(days=limit),timezone.now()], grp_id__contains='ROME',filt__contains = 'r')
list_of_images_g = updb.Image.objects.filter(date_obs__range=[timezone.now()-timedelta(days=limit),timezone.now()], grp_id__contains='ROME',filt__contains = 'g')
plt.suptitle('TOTAL = '+str(len(list_of_images))+' ; SDSS-i='+str(len(list_of_images_i))+' ; SDSS_r='+str(len(list_of_images_r))+' ; SDSS_g='+str(len(list_of_images_g)))
plt.show()


aaa = timezone.now()-timedelta(days=limit)
bbb = timezone.now()
date_start = datetime.datetime(aaa.year,aaa.month,aaa.day)
date_end = datetime.datetime(bbb.year,bbb.month,bbb.day)

days = (date_end-date_start).days

delta = 0

while days>0:

	plt.bar(date_start+timedelta(days=delta),22,width = 0.3,color ='red',alpha=0.3,align='center')
	plt.bar(date_start+timedelta(days=delta)+timedelta(hours=8),22,width = 0.3,color = 'orange',alpha=0.3,align='center')
	plt.bar(date_start+timedelta(days=delta)+timedelta(hours=16),22,width = 0.3,color ='yellow',alpha=0.3,align='center')

	delta += 1 
	days += -1



date_telescopes = [(a.date_obs,a.tel,a.field.name,a.filt) for a in list_of_images]

colors = []
symbols = []
site_dico = {'*':'SSO','o':'SAAO','s':'CTIO'}
offset = []
for observations  in date_telescopes :

	if 'SSO' in observations[1]:
		

		symbols.append('*')
		
	if 'CTIO' in observations[1]:	


		symbols.append('s')

	if 'SAAO' in observations[1]:


		symbols.append('o')

	if '-i' in observations[3]:
		colors.append(0.0)
		offset.append(0.5)
	if '-g' in observations[3]:
		colors.append(0.5)
		offset.append(0)
	if '-r' in observations[3]:
		colors.append(1.0)
		offset.append(0.25)

plot_telescopes = [(list_of_images[i].date_obs,list_of_images[i].tel,list_of_images[i].field.name,list_of_images[i].filt,colors[i],symbols[i]) for i in xrange(len(list_of_images))]

fields_number = np.array([float(plot_telescopes[i][2][-2:])+offset[i] for i in xrange(len(plot_telescopes))])
plot_telescopes = np.array(plot_telescopes)

for mark in ['*','s','o']:

	good = np.where(plot_telescopes[:,5] == mark)[0]
	plt.scatter(plot_telescopes[good,0], fields_number[good],c=plot_telescopes[good,4],marker = mark,s=100,label = site_dico[mark])

plt.legend(scatterpoints=1)
plt.xlabel('TIME',fontsize = 50)
plt.ylabel('FIELD', fontsize=50)


plt.show()

