from django.shortcuts import render
from .models import Event, Single_Model, Binary_Model, Data_File, Robonet_Log, Robonet_Reduction, Robonet_Request, Robonet_Status, Ogle_Detail, Moa_Detail, Kmt_Detail

def index(request):
    return HttpResponse("Hello, world. You're at the Events index.")

def list_all(request):
    event_names = Event.objects.filter(ev_name_ogle__contains="OGLE")
    ordered_ogle = Event.objects.order_by('ev_name_ogle')
    context = {'event_names': ordered_ogle}
    return render(request, 'events/list_events.html', context)
