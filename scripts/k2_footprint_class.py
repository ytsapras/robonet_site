from sys import exit, argv
from os import path
import json
import numpy as np
from astropy.time import Time, TimeDelta
import matplotlib.pyplot as plt
from commands import getstatusoutput

class K2Footprint():
    """Class to parse the JSON file description of the K2 footprint"""
    
    def __init__( self, campaign, year, debug=False ):
        
	def date_list_to_jd( date_list ):
	    """Establish the dates of the campaign in JD"""
	    jd_list = []
	    for date in date_list:
	        timeobj = Time( (date + 'T00:00:00'), format='isot', scale='utc')
	        jd_list.append( timeobj.jd )
            return jd_list
	
	def calc_alert_date( year, date ):
	    """Function to calculate the last-alert date based on the Campaign-start date 
	    given as a string, adjusting the date to the year requested for the 
	    simulation, to effectively compare the times of the events from the catalogue."""
	    
	    date = str(year) + '-' + date[5:]
	    campaign_start = Time( (date + 'T00:00:00'), format='isot', scale='utc')
	    alert_time = TimeDelta( (30.0*24.0*60.0*60.0), format='sec' )
	    alert_date = campaign_start - alert_time
	    return alert_date.jd
	    
	# Declare campaign number:
	self.campaign = campaign
	
	# Read and parse the outline of the K2 footprint on sky:
        k2_footprint_file = 'k2-footprint.json'
        if path.isfile( k2_footprint_file ) == False:
            print 'Error: Cannot find JSON file of the K2 footprint'
            exit()
	
        file_data = open( k2_footprint_file, 'r').read()
        json_data = json.loads( file_data )
        json_data = json_data['c'+str(self.campaign)]
        self.k2_footprint = {}
        self.channel_limits = {}
	for channel in json_data['channels'].keys():
	    corners = []
	    for i in range(0,4,1):
	        corners.append( [ json_data['channels'][channel]['corners_ra'][i], \
		                  json_data['channels'][channel]['corners_dec'][i] ] )
	    corners.append( [ json_data['channels'][channel]['corners_ra'][0], \
	                      json_data['channels'][channel]['corners_dec'][0] ] )
	    a = np.array( corners )
	    ra_min = a[:,0].min()
	    ra_max = a[:,0].max()
	    dec_min = a[:,1].min()
	    dec_max = a[:,1].max()
	    self.k2_footprint[channel] = corners
	    self.channel_limits[channel] = [ ra_min, ra_max ,dec_min, dec_max ]
	    
	# Campaign and last alert dates reset to YEAR to simulate as if the events happened in 2016
	self.last_alert_dates = []
        if campaign == 9: 
	    self.campaign_dates = [ [ str(year) + '-04-07', str(year) + '-05-19' ], \
	                            [ str(year) + '-05-22', str(year) + '-07-02' ] ]
	else:
            self.campaign_dates = [ [ str(year) + json_data['start'][4:], str(year) + json_data['stop'][4:] ] ]
	    
	if debug == True: print 'Campaign dates: ',self.campaign_dates
	for date_range in self.campaign_dates:
	    self.last_alert_dates.append( calc_alert_date( year, date_range[0] ) )
	if debug == True: print 'Last alert dates: ',self.last_alert_dates
	
	date_list = []
	for sub_campaign in self.campaign_dates:
	    date_list.append( date_list_to_jd( sub_campaign ) )
	self.campaign_dates = date_list
	if debug == True: print 'Campaign dates, JD: ',self.campaign_dates
	
	if debug == True:
            for channel, corners in self.k2_footprint.items():
                print channel, ': ', corners

    def targets_in_footprint( self, targets ):
        """Method to determine whether a given target lies within the
        K2 footprint or not.
        Required parameters:
            target_locations   dict   object_id: Event object
        Depends:
            Requires K2onSilicon installed (from K2FOV package)
        Returns:
            target_locations   
        """
	
        # Write the CSV file in the format required by K2onSilicon. 
        # This uses a default magnitude for the target, which we don't know.
        fileobj = open( 'target.csv', 'w')
        for target_id, target in targets.items():
            ( ra, dec ) = target.get_location()
            fileobj.write( str(ra) + ', ' + str(dec) + ', 11.0\n' )
        fileobj.close()
	
        # Call K2onSilicon and harvest the output:
        ( iexec, coutput ) = getstatusoutput( 'K2onSilicon target.csv ' + \
                    str(self.campaign) )
        print coutput
	
        # Parse the output file, called targets_siliconFlag.csv'
        # The last column entry for each object indicates whether or not the object lies on silicon.
        # 0 = no, 2 = yes
        file_lines = open( 'targets_siliconFlag.csv', 'r').readlines()
        for i,target_id in enumerate( targets.keys() ):
            target = targets[ target_id ]
            flag = None
            if float( file_lines[i].split(',')[-1] ) == 0.0: target.in_footprint = False
            if float( file_lines[i].split(',')[-1] ) == 2.0: target.in_footprint = True
            targets[ target_id ] = target
	
        # Remove the temporary files:
	
        return targets

    def targets_in_superstamp( self, targets ):
        """Method to check whether the targets are within the K2C9 superstamp.
	Requires targets_in_footprint to have been run already.
	Depends:
	    Requires K2inMicrolensRegion installed (from K2FOV package)
	"""
	
	for target_id in targets:
	    target = targets[ target_id ]
	    if target.in_footprint == True:
	        ( iexec, coutput ) = getstatusoutput( 'K2inMicrolensRegion ' + str(target.ra) + ' ' + str(target.dec) )
	    
	        if 'coordinate is NOT inside' in coutput:
	            target.in_superstamp = False
	        elif 'coordinate is inside' in coutput:
	            target.in_superstamp = True
	        targets[ target_id ] = target
	    
	return targets

    def targets_in_campaign( self, targets ):
        """Method to check whether an event would be alerted in time to be included 
        in a K2 Campaign.  For this to happen the following criteria must be met:
            For events in footprint but outside superstamp:
            - ( t0 - tE ) < last_alert_date        Event detected in time to alert
            - ( t0 + 2*tE ) < last_alert_date   Event likely to be over before Campaign, even from space
            => target.alertable = True
	
        	For events in the superstamp (Campaign 9 only):
             - ( t0 - 2*tE ) < Campaign end        Event starts before the end of Campaign
             - ( t0 + 2*tE ) > Campaign start      Event ends after the start of the Campaign
             => target.during_campaign = True
	
        	where
             last_alert_date = date of target upload
             Inputs:
                 targets   dict   object_id: Event object
        """
	
        for target_id in targets.keys():
            target = targets[ target_id ]
	    
            # Check whether the event is detectable during the Campaign, 
            # accounting for the possibility that there may be a mid-Campaign break, and so
            # multiple start and end dates. 
            campaign_start = self.campaign_dates[0][0]
            campaign_end = self.campaign_dates[-1][-1]
            t0 = target.get_par('t0')
            tE = target.get_par('te')
            if ( t0 - 2.0*tE ) < campaign_end and \
                    ( t0 + 2.0*tE ) > campaign_start:
                target.during_campaign = True
		
            # To be alertable, a target must:
            # - Be within tE of the peak before the alert upload date
            # - Have a predicted end date greater than the campaign start
            for date in self.last_alert_dates:
                if ( t0 - tE ) < date and \
                    ( t0 + 2.0*tE ) > campaign_start:
                        target.alertable = True
            targets[ target_id ] = target
	
	return targets


    def plot_footprint( self, plot_file=None, targets=None, year = None ):
        """Method to plot the footprint"""
	
        fig = plt.figure(1)
        for channel, corners in self.k2_footprint.items():
            a = np.array( corners )
            plt.plot( a[:,0], a[:,1], 'r-' )
            if targets != None:
                for target_id, target in targets.items():
                    (ra, dec) = target.get_location()
                    if target.in_footprint == False:
                        plt.plot( ra, dec, 'k.', markersize=2 )
                    elif target.in_superstamp == True and target.during_campaign == True: 
                        plt.plot( ra, dec, 'y.' )
                    elif target.in_footprint == True and \
                        target.in_superstamp == False and \
                        target.during_campaign == True: 
                        plt.plot( ra, dec, 'c.' )
                    elif target.in_footprint == True and target.during_campaign == False: 
                        plt.plot( ra, dec, 'm.' )
        plt.xlabel( 'RA [deg]' )
        plt.ylabel( 'Dec [deg]' )
        if year == None: 
            plt.title( 'Microlensing events within K2 Campaign ' + str(self.campaign) + ' footprint' )
        else: 
            plt.title( 'Microlensing events within K2 Campaign ' + str(self.campaign) + ' footprint from ' + str(year) )
        if plot_file == None: plot_file = 'k2-footprint.png'
        (xmin,xmax,ymin,ymax) = plt.axis()
        plt.axis( [xmax,xmin,ymin,ymax] )
        plt.grid(True)
        plt.savefig( plot_file )

