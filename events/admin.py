from django.contrib import admin
from .models import Event, Data_File, Ogle_Detail, Moa_Detail, Kmt_Detail, Single_Model, Binary_Model, Data_File, Robonet_Log, Robonet_Reduction, Robonet_Request, Robonet_Status 
admin.site.register(Event)
admin.site.register(Data_File)
admin.site.register(Ogle_Detail)
admin.site.register(Moa_Detail)
admin.site.register(Kmt_Detail)
admin.site.register(Single_Model)
admin.site.register(Binary_Model)
admin.site.register(Robonet_Log)
admin.site.register(Robonet_Request)
admin.site.register(Robonet_Status)
admin.site.register(Robonet_Reduction)

#
#class EventAdmin(admin.ModelAdmin):
#   list_display = ('ev_name', 'ev_ra', 'ev_dec')
   
# Register your models here.
