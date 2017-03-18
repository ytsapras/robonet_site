Last updated 18 Mar 2017

DB uses 	django v1.10.5
		python v2.7.12
		anaconda v4.3.1
		bokeh v0.12.4
		
			LIST OF DJANGO MODULES (models.py)
---------------------------------------------------------------------------------
NAME			DESCRIPTION				ASSOCIATED FUNCTION(/scripts/update_db_2.py)
Field			known ROME/REA field			add_field
Operator		known survey/follow-up			add_operator
Telescope		known telescopes			add_telescope
Instrument		known instruments			add_instrument
Filter			known filters				add_filter
Event			RA,Dec,status,field			add_event
EventName		names associated with Event		add_event_name
SingleModel		single lens models for Event		add_single_lens
BinaryModel		binary lens models for Event		add_binary_lens
EventReduction  	light curve & related info		add_reduction
ObsRequest		observing requests submitted		add_request
EventStatus		update event status			add_status
DataFile		ARTEMiS compatible .dat files		add_datafile
Tap			tap entries and details			add_tap
Image			image identifier & related info		add_image
---------------------------------------------------------------------------------
