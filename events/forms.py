from events.models import *
from django import forms

class OperatorForm(forms.ModelForm):
   class Meta:
      model = Operator
      fields = '__all__'

class TelescopeForm(forms.ModelForm):
   class Meta:
      model = Telescope
      fields = '__all__'

class InstrumentForm(forms.ModelForm):
   class Meta:
      model = Instrument
      fields = '__all__'

class FilterForm(forms.ModelForm):
   class Meta:
      model = Filter
      fields = '__all__'

class EventForm(forms.ModelForm):
   class Meta:
      model = Event
      fields = '__all__'

class EventNameForm(forms.ModelForm):
   class Meta:
      model = EventName
      fields = ('name',)

class SingleModelForm(forms.ModelForm):
   class Meta:
      model = SingleModel
      fields = ('event','Tmax','e_Tmax', 'tau', 'e_tau', 'umin', 'e_umin',
                'rho', 'e_rho', 'pi_e_n', 'e_pi_e_n', 'pi_e_e', 'e_pi_e_e',
		'modeler', 'tap_omega', 'chi_sq', 'last_updated') 
   last_updated = forms.DateTimeField(label='last_updated',input_formats=["%Y-%m-%dT%H:%M:%S"])
   
class BinaryModelForm(forms.ModelForm):
   class Meta:
      model = BinaryModel
      fields = '__all__'
   last_updated = forms.DateTimeField(label='last_updated',input_formats=["%Y-%m-%dT%H:%M:%S"])

class EventReductionForm(forms.ModelForm):
   class Meta:
      model = EventReduction
      fields = '__all__'
   timestamp = forms.DateTimeField(label='timestamp',input_formats=["%Y-%m-%dT%H:%M:%S"])
    
class DataFileForm(forms.ModelForm):
   class Meta:
      model = DataFile
      fields = '__all__'
   last_upd = forms.DateTimeField(label='last_upd',input_formats=["%Y-%m-%dT%H:%M:%S"])
   
class TapForm(forms.ModelForm):
   class Meta:
      model = Tap
      fields = '__all__'
   timestamp = forms.DateTimeField(label='timestamp',input_formats=["%Y-%m-%dT%H:%M:%S"])

class TapLimaForm(forms.ModelForm):
   class Meta:
      model = TapLima
      fields = '__all__'
   timestamp = forms.DateTimeField(label='timestamp',input_formats=["%Y-%m-%dT%H:%M:%S"])
   
class ImageForm(forms.ModelForm):
   class Meta:
      model = Image
      fields = '__all__'
   timestamp = forms.DateTimeField(label='timestamp',input_formats=["%Y-%m-%dT%H:%M:%S"])
   date_obs = forms.DateTimeField(label='date_obs',input_formats=["%Y-%m-%dT%H:%M:%S"])
   
class QueryObsRequestForm(forms.ModelForm):
    class Meta:
        model = ObsRequest
        fields = ('field',)
        
class RecordObsRequestForm(forms.ModelForm):
    class Meta:
        model = ObsRequest
        fields = ('field','t_sample','exptime','timestamp','time_expire')
    timestamp = forms.DateTimeField(label='timestamp',input_formats=["%Y-%m-%dT%H:%M:%S"])
    time_expire = forms.DateTimeField(label='time_expire',input_formats=["%Y-%m-%dT%H:%M:%S"])
    
class RecordSubObsRequestForm(forms.ModelForm):
    class Meta:
        model = SubObsRequest
        fields = ('sr_id', 'grp_id', 'track_id', 'window_start', 'window_end', 'status', 'time_executed')
    window_start = forms.DateTimeField(label='window_start',input_formats=["%Y-%m-%dT%H:%M:%S"])
    window_end = forms.DateTimeField(label='window_end',input_formats=["%Y-%m-%dT%H:%M:%S"])
    time_executed = forms.DateTimeField(label='time_executed',input_formats=["%Y-%m-%dT%H:%M:%S"],required=False)
    
class RecordDataFileForm(forms.ModelForm):
    class Meta:
        model = DataFile
        fields = ('datafile','last_mag', 'tel', 'filt',
                  'baseline','g','ndata','last_obs','last_upd')
    last_obs = forms.DateTimeField(label='last_obs',input_formats=["%Y-%m-%dT%H:%M:%S"])
    last_upd = forms.DateTimeField(label='last_upd',input_formats=["%Y-%m-%dT%H:%M:%S"])
    timestamp = forms.DateField(label='timestamp',input_formats=["%Y-%m-%dT%H:%M:%S"])
    time_expire = forms.DateField(label='time_expire',input_formats=["%Y-%m-%dT%H:%M:%S"])
