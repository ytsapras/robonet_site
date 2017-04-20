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
      fields = '__all__'

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

class ObsRequestForm(forms.ModelForm):
    class Meta:
        model = ObsRequest
        fields = ('field',)
        