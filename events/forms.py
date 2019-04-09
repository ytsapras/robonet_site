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

class EventPositionForm(forms.Form):
   class Meta:
      fields = ('ra_min', 'ra_max', 'dec_min', 'dec_max',)
   ra_min = forms.FloatField(label='ra_min',min_value=0.0,max_value=360.0)
   ra_max = forms.FloatField(label='ra_max',min_value=0.0,max_value=360.0)
   dec_min = forms.FloatField(label='dec_min',min_value=-90.0,max_value=90.0)
   dec_max = forms.FloatField(label='dec_max',min_value=-90.0,max_value=90.0)

class EventSearchForm(forms.Form):
    class Meta:
        fields = ('field', 'operator', 'status', 'anomaly_rank', 
                   'ibase_min', 'ibase_max', 'year')
    
    possible_status = (
                      ('NF', 'Not in footprint'),
                      ('AC', 'active'),
                      ('MO', 'monitor'),
                      ('AN', 'anomaly'),
                      ('EX', 'expired'),
                      ('ANY', 'any')
                      )
    possible_operators = ( ('OGLE','OGLE'),
                         ('MOA','MOA'),
                         ('ALL','ALL')
                         )
    possible_fields = ( ('ROME-FIELD-01', 'ROME-FIELD-01'), 
                       ('ROME-FIELD-02', 'ROME-FIELD-02'),
                       ('ROME-FIELD-03', 'ROME-FIELD-03'),
                       ('ROME-FIELD-04', 'ROME-FIELD-04'),
                       ('ROME-FIELD-05', 'ROME-FIELD-05'),
                       ('ROME-FIELD-06', 'ROME-FIELD-06'),
                       ('ROME-FIELD-07', 'ROME-FIELD-07'),
                       ('ROME-FIELD-08', 'ROME-FIELD-08'),
                       ('ROME-FIELD-09', 'ROME-FIELD-09'),
                       ('ROME-FIELD-10', 'ROME-FIELD-10'),
                       ('ROME-FIELD-11', 'ROME-FIELD-11'),
                       ('ROME-FIELD-12', 'ROME-FIELD-12'),
                       ('ROME-FIELD-13', 'ROME-FIELD-13'),
                       ('ROME-FIELD-14', 'ROME-FIELD-14'),
                       ('ROME-FIELD-15', 'ROME-FIELD-15'),
                       ('ROME-FIELD-16', 'ROME-FIELD-16'),
                       ('ROME-FIELD-17', 'ROME-FIELD-17'),
                       ('ROME-FIELD-18', 'ROME-FIELD-18'),
                       ('ROME-FIELD-19', 'ROME-FIELD-19'),
                       ('ROME-FIELD-20', 'ROME-FIELD-20'),
                       ('All ROME fields', 'All ROME fields'),
                       ('Outside ROME footprint', 'Outside ROME footprint'),
                      )
                      
    field = forms.ChoiceField(label='field', choices=possible_fields)
    operator = forms.ChoiceField(label='operator', choices=possible_operators)
    status = forms.ChoiceField(label='status', choices=possible_status)
    anomaly_rank = forms.FloatField(label='Anomaly Rank', min_value=-1.0, max_value=100.0,required=False)
    ibase_min = forms.FloatField(label='ibase_min',min_value=0.0,max_value=24.0,required=False)
    ibase_max = forms.FloatField(label='ibase_max',min_value=0.0,max_value=24.0,required=False)
    year = forms.IntegerField(label='year',min_value=2017, max_value=2019,required=False)

class EventAnomalyStatusForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('status','override',)
    override = forms.BooleanField(label='override', required=False)


class EventOverrideForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('override',)
    override = forms.BooleanField(label='override', required=False)
    
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

class TapStatusForm(forms.ModelForm):
   class Meta:
      model = Tap
      fields = ('event', 'priority',)
   
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

class ImageNameForm(forms.ModelForm):
   class Meta:
      model = Image
      fields = ('image_name',)

class ObsExposureForm(forms.ModelForm):
    class Meta:
        model = ObsRequest
        fields = ('exptime', 'which_filter', 'n_exp')
    
    possible_filters = ( ('SDSS-i', 'SDSS-i'),
                         ('SDSS-r', 'SDSS-r'),
                         ('SDSS-g', 'SDSS-g') )
                         
    exptime = forms.IntegerField()
    t_sample = forms.DecimalField(max_digits=6,decimal_places=2)
    which_filter = forms.ChoiceField(label='field', choices=possible_filters)
    
class ObsRequestForm(forms.ModelForm):
    class Meta:
        model = ObsRequest
        fields = ('field', 'pfrm_on', 'onem_on', 'twom_on', 't_sample', 
                  'exptime', 'timestamp', 'time_expire', 'n_exp',
                  'jitter', 'airmass_limit', 'lunar_distance_limit', 
                  'ipp', 'simulate')
    jitter = forms.FloatField(label='jitter',min_value=0.1,max_value=24.0)
    airmass_limit = forms.FloatField(label='airmass_limit',min_value=1.0,max_value=2.2)
    lunar_distance_limit = forms.FloatField(label='lunar_distance_limit',min_value=1.0,max_value=180.0)
    ipp = forms.FloatField(label='ipp',min_value=0.1,max_value=2.0)
    simulate = forms.ChoiceField([(False,False),(True,True)])
    
class FieldNameForm(forms.ModelForm):
    class Meta:
        model = Field
        fields = ('name',)
    name = forms.CharField(max_length=50)
    
class QueryObsRequestForm(forms.ModelForm):
    class Meta:
        model = ObsRequest
        fields = ('field',)
   
class QueryObsRequestDateForm(forms.ModelForm):
    class Meta:
        model = ObsRequest
        fields = ('timestamp','time_expire','request_status')
    timestamp = forms.DateTimeField(label='timestamp',input_formats=["%Y-%m-%dT%H:%M:%S"])
    time_expire = forms.DateTimeField(label='time_expire',input_formats=["%Y-%m-%dT%H:%M:%S"])
    
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
