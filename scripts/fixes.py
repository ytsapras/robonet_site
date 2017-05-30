from update_db_2 import *
# Fix events that have non-NF status but are ourside footprint 
def notnf():
    events = Event.objects.all()
    for ev in events.values():
        evstatus = ev['status']
	evfldid = ev['field_id']
	evid = ev['id']
	# Set status to NF if outside footprint
	if evfldid==21:
	    p = Event.objects.get(id=evid)
	    p.status = 'NF'
	    p.save()
