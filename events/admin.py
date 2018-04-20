from django.contrib import admin
from events.models import Field, Operator, Telescope, Instrument, Filter, Event
from events.models import EventName, SingleModel, BinaryModel
from events.models import EventReduction, ObsRequest, DataFile
#from events.models import SubObsRequest
from events.models import Tap, TapLima, Image, EventStatus
 
# Register your models here.
admin.site.register(Field)
admin.site.register(Operator)
admin.site.register(Telescope)
admin.site.register(Instrument)
admin.site.register(Filter)
admin.site.register(Event)
admin.site.register(EventName)
admin.site.register(SingleModel)
admin.site.register(BinaryModel)
admin.site.register(EventReduction)
admin.site.register(ObsRequest)
#admin.site.register(SubObsRequest)
admin.site.register(EventStatus)
admin.site.register(DataFile)
admin.site.register(Tap)
admin.site.register(TapLima)
admin.site.register(Image)

