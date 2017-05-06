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
      fields = '__all__'

class BinaryModelForm(forms.ModelForm):
   class Meta:
      model = BinaryModel
      fields = '__all__'

class DataFileForm(forms.ModelForm):
   class Meta:
      model = DataFile
      fields = '__all__'

class TapForm(forms.ModelForm):
   class Meta:
      model = Tap
      fields = '__all__'

class ImageForm(forms.ModelForm):
   class Meta:
      model = Image
      fields = '__all__'

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
    
class RecordDataFileForm(forms.ModelForm):
    class Meta:
        model = DataFile
        fields = ('datafile','last_mag', 'tel', 'filt',
                  'baseline','g','ndata','last_obs','last_upd')
    last_obs = forms.DateTimeField(label='last_obs',input_formats=["%Y-%m-%dT%H:%M:%S"])
    last_upd = forms.DateTimeField(label='last_upd',input_formats=["%Y-%m-%dT%H:%M:%S"])
    