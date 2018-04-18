import requests
import matplotlib.pyplot as plt
import datetime
import numpy as np
from matplotlib.ticker import MaxNLocator, MultipleLocator

API_ROOT = 'https://observe.lco.global/api/'
api_token = raw_input('Please enter your LCO API token: ')
headers = {'Authorization': 'Token ' + api_token}


response = requests.get(API_ROOT + 'telescope_states/?start=2017-04-01 02:00:00&end=2017-07-17 02:00:00', headers=headers,timeout=300).json()
colors = ['b','r','g','y','m','c','orange','k','gray']

chili_reason = []
chili_status = []
chili_date = []


sa_reason = []
sa_status = []
sa_date = []

au_reason = []
au_status = []
au_date = []

elp_reason = []
elp_status = []
elp_date = []

for key in response.keys():

	if '1m' in key :
		
		to_treat = response[key]

		for event in xrange(len(to_treat)) :

			date = to_treat[event]['start']
			day = datetime.datetime(int(date[:4]),int(date[5:7]),int(date[8:10]),int(date[11:13]),int(date[14:16]),int(date[17:19]))


			if 'Available for' in to_treat[event]['event_reason']:
				reason = 'available'

			if 'Humidity' in to_treat[event]['event_reason']:
				reason = 'humidity'
			
			if 'No update' in to_treat[event]['event_reason']:
				reason = 'no update'

			if 'Raining' in to_treat[event]['event_reason']:
				reason = 'raining'

			if 'Risk of' in to_treat[event]['event_reason']:
				reason = 'risk of dewing'

			if 'DISABLED' in to_treat[event]['event_reason']:

				reason = 'sequencer DISABLED'
			
			if 'MANUAL' in to_treat[event]['event_reason']:
				reason = 'sequencer MANUAL'
			if 'unavalaible for for' in to_treat[event]['event_reason']:
				reason = 'sequencer unavailable'
			
			if 'transparency' in to_treat[event]['event_reason']:
				reason = 'cloudy'	

			if 'Unknown' in to_treat[event]['event_reason']:
				reason = 'unknown'		

			if 'coj' in to_treat[event]['telescope']:
				DATE = au_date
				REASON = au_reason
				STATUS = au_status

			if 'cpt' in to_treat[event]['telescope']:
				DATE = sa_date
				REASON = sa_reason
				STATUS = sa_status

			if 'lsc' in to_treat[event]['telescope']:
				DATE = chili_date
				REASON = chili_reason
				STATUS = chili_status

			if 'elp' in to_treat[event]['telescope']:
				DATE = elp_date
				REASON = elp_reason
				STATUS = elp_status

			status = to_treat[event]['event_type']
			#import pdb; pdb.set_trace()
			DATE.append(day)
			REASON.append(reason)
			STATUS.append(status)


chili_pie = np.unique(chili_reason,return_counts=True)
sa_pie = np.unique(sa_reason,return_counts=True)
au_pie = np.unique(au_reason,return_counts=True)
			

fig,axes = plt.subplots(3,2)



rat_chili = []
for i in xrange(len(chili_status)):
	status = 1
	if chili_status[i] != 'AVAILABLE':
		status=0
	rat_chili.append(status)
	axes[0,0].scatter(chili_date[i],status,edgecolor = 'None',facecolor='orange')

axes[0,1].pie(chili_pie[1],labels=chili_pie[0],colors=colors,autopct='%1.1f%%',shadow=True)
axes[0,0].set_xlim(chili_date[0],chili_date[-1])
axes[0,0].set_title('CTIO : '+str(sum(rat_chili)/float(len(rat_chili))))

rat_au = []
for i in xrange(len(au_status)):
	status = 1
	if au_status[i] != 'AVAILABLE':
		status=0
	rat_au.append(status)	
	axes[1,0].scatter(au_date[i],status,edgecolor = 'None',facecolor='y')

axes[1,1].pie(au_pie[1],labels=au_pie[0],colors=colors,autopct='%1.1f%%',shadow=True)
axes[1,0].set_title(' SSO : '+str(sum(rat_au)/float(len(rat_au))))
axes[1,0].set_xlim(au_date[0],au_date[-1])
rat_sa = []
for i in xrange(len(sa_status)):
	status = 1
	if sa_status[i] != 'AVAILABLE':
		status=0
	rat_sa.append(status)
	axes[2,0].scatter(sa_date[i],status,edgecolor = 'None',facecolor='r')

axes[2,1].pie(sa_pie[1],labels=sa_pie[0],colors=colors,autopct='%1.1f%%',shadow=True)

axes[2,0].set_title('SAAO : '+str(sum(rat_sa)/float(len(rat_sa))))
axes[2,0].set_xlim(sa_date[0],sa_date[-1])
plt.show()
import pdb; pdb.set_trace()
