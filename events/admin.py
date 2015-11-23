from django.contrib import admin
#from .models import Event, Data_File, Ogle_Detail, Moa_Detail, Kmt_Detail, Single_Model, Binary_Model, Data_File, Robonet_Log, Robonet_Reduction, Robonet_Request, Robonet_Status 
from .models import Operator, Telescope, Instrument, Filter, Event, EventName, SingleModel, BinaryModel, RobonetReduction, RobonetRequest, RobonetStatus, DataFile, Tap, Image
 
# Register your models here.
admin.site.register(Operator)
admin.site.register(Telescope)
admin.site.register(Instrument)
admin.site.register(Filter)
admin.site.register(Event)
admin.site.register(EventName)
admin.site.register(SingleModel)
admin.site.register(BinaryModel)
admin.site.register(RobonetReduction)
admin.site.register(RobonetRequest)
admin.site.register(RobonetStatus)
admin.site.register(DataFile)
admin.site.register(Tap)
admin.site.register(Image)

#admin.site.register(Event)
#admin.site.register(Data_File)
#admin.site.register(Ogle_Detail)
#admin.site.register(Moa_Detail)
#admin.site.register(Kmt_Detail)
#admin.site.register(Single_Model)
#admin.site.register(Binary_Model)
#admin.site.register(Robonet_Log)
#admin.site.register(Robonet_Request)
#admin.site.register(Robonet_Status)
#admin.site.register(Robonet_Reduction)
