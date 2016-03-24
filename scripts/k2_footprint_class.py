from sys import exit, argv
from os import path
import json
import numpy as np
from astropy.time import Time, TimeDelta
import matplotlib.pyplot as plt
from commands import getstatusoutput
import logging
import K2fov
from K2fov import c9
import event_classes
import utilities
import lcogt_imagers

class K2Footprint():
    """Class to parse the JSON file description of the K2 footprint"""

    def __init__( self, config, campaign, year, debug=False, log=None ):
        
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
        self.xsuperstamp_targets = {}
 
        # Read and parse the outline of the K2 footprint on sky:
        k2_footprint_file = config['k2_footprint_data']
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
            self.campaign_dates = [ [ str(year) + json_data['start'][4:], \
                                str(year) + json_data['stop'][4:] ] ]
	    
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
        if log != None:
            log.info('Loaded K2 footprint for Campaign ' + str(campaign))
            
    def targets_in_footprint( self, config, targets, verbose=False ):
        """Method to determine whether a given target lies within the
        K2 footprint or not.
        Required parameters:
            target_locations   dict   object_id: Event object
        Depends:
            Requires K2onSilicon installed (from K2FOV package)
        Returns:
            target_locations   
        """
	
        if verbose == True:
            print ' -> Checking whether events are in the K2 campaign footprint'
            
        # Write the CSV file in the format required by K2onSilicon. 
        # This uses a default magnitude for the target, which we don't know.
        target_file = path.join(config['tmp_location'],'target.csv')
        output_file = path.join(config['tmp_location'],'targets_siliconFlag.csv')
        fileobj = open( target_file, 'w' )
        for target_id, target in targets.items():
            ( ra, dec ) = target.get_location()
            fileobj.write( str(ra) + ', ' + str(dec) + ', 11.0\n' )
        fileobj.close()
	
        # Call K2onSilicon and harvest the output:
        K2fov.K2onSilicon( target_file, int(self.campaign) )
        #( iexec, coutput ) = getstatusoutput( 'K2onSilicon target.csv ' + \
        #            str(self.campaign) )
	
        # Parse the output file, called targets_siliconFlag.csv'
        # The last column entry for each object indicates whether or not the object lies on silicon.
        # 0 = no, 2 = yes
        file_lines = open( output_file, 'r').readlines()
        for i,target_id in enumerate( targets.keys() ):
            target = targets[ target_id ]
            flag = None
            if float( file_lines[i].split(',')[-1] ) == 0.0: 
                target.in_footprint = False
            if float( file_lines[i].split(',')[-1] ) == 2.0: 
                target.in_footprint = True
            targets[ target_id ] = target
	
        # Remove the temporary files:
 
        return targets

    def targets_in_superstamp( self, targets, log=None, verbose=False, debug=False ):
        """Method to check whether the targets are within the K2C9 superstamp.
        Requires targets_in_footprint to have been run already.
        Depends:
            Requires K2inMicrolensRegion installed (from K2FOV package)
        """
        
        def check_in_superstamp( target ):
            (ra, dec) = target.get_location()
            if ra == None or dec == None:
                print target.summary([])
                exit()
            result = c9.inMicrolensRegion(ra, dec)
            return result
#            comm = 'K2inMicrolensRegion ' + str(ra) + ' ' + str(dec) 
#            ( iexec, coutput ) = getstatusoutput( comm )
#            if 'coordinate is NOT inside' in coutput:
#                return False
#            elif 'coordinate is inside' in coutput:
#                return True
#            elif 'command not found' in coutput:
#                print """ERROR: K2fov tools not available.  
#                        Cannot check target location within the footprint"""
#                exit()
#            else:
#                print comm
#                print coutput
#                exit()
                
        if debug==True: 
            print ' -> Checking whether events are in the K2C9 superstamp'
        ntargets = float( len(targets) )
        for i,target_id in enumerate( targets ):
            target = targets[ target_id ]
            
            if debug==True: 
                (ra, dec) = target.get_location()
                print 'SCHK start: ',ra, dec,\
                targets[ target_id ].summary( ['master_index','in_superstamp', 'in_footprint', 'during_campaign'] )
            if target.in_superstamp == True:
                if debug==True: print 'Target already known to be in superstamp'
            
            elif target.in_footprint == 'Unknown' and \
                    target.in_superstamp == 'Unknown':
                if debug==True: 
                    print 'Target location relative to footprint unknown, checking location with superstamp'
                target.in_superstamp = check_in_superstamp( target )
                if debug==True: 
                    print '-> check result ',check_in_superstamp( target )
            elif target.in_footprint == True and \
                    target.in_superstamp == 'Unknown':
                if debug==True: 
                    print 'Target within footprint, checking location with superstamp'
                target.in_superstamp = check_in_superstamp( target )
                if debug==True: 
                    print '-> check result ',check_in_superstamp( target )

            elif target.in_footprint == False:
                target.in_superstamp = False
                if debug==True: print 'Target outside footprint'
                
            else:
                if debug==True: print 'Target in footprint unknown?'
                
                if target.in_superstamp == 'Unknown' \
                    and target.in_footprint == False:
                    if debug == True: print 'MISSED CHECK!'
                target.in_superstamp = False
                
            targets[ target_id ] = target
            if debug==True: 
                print 'SCHK: ',targets[ target_id ].summary( ['in_superstamp', 'in_footprint', 'during_campaign'] )
            
            if verbose==True and (i%50) == 0:
                print '  - completed ' + str(i) + ' out of ' + str( ntargets )
	    
        return targets

    def targets_in_campaign( self, targets, verbose=False ):
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
        
        if verbose == True:
            print '  -> Checking whether events occur within campaign duration'
        
        # Thresholds for determining whether an event has ended before a 
        # campaign or starts too late:
        n_min_te = 2.0
        n_max_te = 2.0
        
        for target_id in targets.keys():
            target = targets[ target_id ]
            
            origin = target.get_event_origin()
            
            # Check whether the event is detectable during the Campaign, 
            # accounting for the possibility that there may be a mid-Campaign break, and so
            # multiple start and end dates. 
            campaign_start = self.campaign_dates[0][0]
            campaign_end = self.campaign_dates[-1][-1]
            t0 = target.get_par( 't0' )
            tE = target.get_par( 'te' )
            tnow = Time( '2016-02-01T00:00:00', format='isot', scale='utc')
            try:
                if t0 > tnow.jd:
                    target.during_campaign = True
                else:
                    if ( t0 - n_min_te*tE ) < campaign_end and \
                        ( t0 + n_max_te*tE ) > campaign_start:
                        target.during_campaign = True
                    else:
                        target.during_campaign = False
                    
                # To be alertable, a target must:
                # - Be within tE of the peak before the alert upload date
                # - Have a predicted end date greater than the campaign start
                for date in self.last_alert_dates:
                    if ( t0 - tE ) < date and \
                        ( t0 + n_max_te*tE ) > campaign_start:
                            target.alertable = True
                    else:
                        target.alertable = False
                    
                    
            except TypeError:
                print 'Missing params: ',t0,tE,\
                        target.summary( ['ogle_te','ogle_t0'] ), target_id
                target.during_campaign = False

            targets[ target_id ] = target
            
	return targets

    def load_isolated_stars( self ):
        """Method to load the list of isolated stars in the K2C9 field, 
        compiled by Matthew Penny"""
        
        self.isolated_stars = np.array( [ [ 270.40804, -27.046134 ], \
                        [ 270.49576, -25.536695 ], \
                        [ 270.73213, -27.874719 ],\
                        [ 270.74435, -27.865961],\
                        [ 272.57049, -28.294317], \
                        [ 268.93794, -28.630169],\
                        [ 269.31554, -27.714637], \
                        [ 268.733, -27.826375],\
                        [ 268.8716, -28.082166],\
                        [267.57216	, -27.320698],\
                        [268.2913528, -27.2967556],\
                        [268.4794417, -27.4386056], \
                        [268.2337144, -27.1964411]\
                    ] )
    
    def load_dark_patches( self ):
        """Method to load the list of dark patches in the K2C9 field, 
        compiled by Matthew Penny"""
        
        self.dark_patches = np.array( [ [ 270.84623, -26.762669 ],\
                                        [ 270.41595, -27.049313 ],\
                                        [ 270.48975, -25.519039 ],\
                                        [ 270.75529, -27.858001 ],\
                                        [ 270.41672, -27.04942 ],\
                                        [ 270.39375, -27.053268 ],\
                                        [ 270.38166, -27.041276 ],\
                                        [ 272.57065, -28.300362 ],\
                                        [ 268.93974, -28.627501 ],\
                                        [ 269.38561, -27.652358 ],\
                                        [ 269.34559, -27.652964 ],\
                                        [ 269.32428, -27.744229 ],\
                                        [ 268.72758, -27.817351 ],\
                                        [ 268.68949, -27.846192 ],\
                                        [ 268.66007, -27.835367 ],\
                                        [ 268.87573, -28.08303 ],\
                                        [ 267.90683, -27.527327 ],\
                                        [ 267.58464, -27.322087 ]\
                                    ] )
    
    def load_ddt_targets( self, config ):
        """Method to load the locations of DDT targets"""
        
        file_name = config['ddt_target_data']
        file_lines = open(file_name, 'r').readlines()
        ddt_targets = []
        for line in file_lines:
            if line.lstrip()[0:1] != '#':
                entries = line.replace('\n','').split(',')
                ddt_targets.append( [float(entries[1]), float(entries[2]) ] )
        
        ddt_targets = np.array( ddt_targets )
        return ddt_targets
    
    def load_xsuperstamp_targets( self, config ):
        """Method to load the data for targets selected outside the 
        superstamp"""
        
        file_data = open( config['xsuperstamp_target_data'], 'r' ).read()
        json_data = json.loads( file_data )
        for target, target_data in json_data['targets'].items():
            event = event_classes.K2C9Event()
            (ra_deg, dec_deg) = utilities.sex2decdeg( target_data['RA'], \
                                                        target_data['Dec'] )
            event.ogle_ra = ra_deg
            event.ogle_dec = dec_deg
            event.ogle_i0 = float( target_data['Io'] )
            event.in_superstamp = False
            event.in_footprint= True
            event.during_campaign = True
            self.xsuperstamp_targets[ target ] = event
    
    def plot_footprint( self, plot_file=None, targets=None, year = None, \
                       plot_isolated_stars=False, plot_dark_patches=False, \
                       plot_ddt_targets=False, overlays={}):
        """Method to plot the footprint"""
        
        
        def get_label_loc( corners ):
            lx = corners[:,0].min() + \
                (corners[:,0].max() - corners[:,0].min()) / 2.0
            ly = corners[:,1].min() + \
                (corners[:,1].max() - corners[:,1].min()) / 2.0
            return lx,ly
            
        def store_position( target_list, ra, dec ):
            ( ra_list, dec_list ) = target_list
            ra_list.append(ra)
            dec_list.append(dec)
            target_list = [ ra_list, dec_list ]
            return target_list
        
        if plot_ddt_targets == True:        
            ddt_targets = self.load_ddt_targets()        
        
        # Establish which targets should be plotted in which colours, 
        # according to whether they occur in or outside the footprint, 
        # superstamp and campaign:
        if targets != None:
            targets_no_k2_data = [ [], [] ]
            targets_in_superstamp = [ [], [] ]
            targets_outside_superstamp = [ [], [] ]
            targets_outside_campaign = [ [], [] ]
            for target_id, target in targets.items():
                (ra, dec) = target.get_location()
                if target.in_footprint == False:
                    targets_no_k2_data = store_position(targets_no_k2_data, ra, dec)
                elif target.in_superstamp == True and target.during_campaign == True: 
                    targets_in_superstamp = store_position(targets_in_superstamp, ra, dec)
                elif target.in_footprint == True and \
                    target.in_superstamp == False and \
                    target.during_campaign == True: 
                    targets_outside_superstamp = store_position(targets_outside_superstamp, ra, dec)
                elif target.in_footprint == True and target.during_campaign == False: 
                    targets_outside_campaign = store_position(targets_outside_campaign, ra, dec)
        
        fig = plt.figure(1,(12,12))
        font_pt = 18
        for channel, corners in self.k2_footprint.items():
            a = np.array( corners )
            plt.plot( a[:,0], a[:,1], 'k-' )
            (lx, ly) = get_label_loc(a)
            plt.text( lx, ly, str(channel) )
        
        if targets != None:
            ( ra, dec ) = targets_no_k2_data
            plt.plot( ra, dec, 'k.', markersize=2 )
            ( ra, dec ) = targets_in_superstamp
            plt.plot( ra, dec, 'g.' )
            ( ra, dec ) = targets_outside_superstamp
            plt.plot( ra, dec, 'c.' )
            ( ra, dec ) = targets_outside_campaign
            plt.plot( ra, dec, 'm.', markersize=2 )
            
        if plot_ddt_targets == True:
            plt.plot( ddt_targets[:,0], ddt_targets[:,1], 'k+', markersize=3 )            
            
        if plot_dark_patches == True:
            self.load_dark_patches()
            plt.plot( self.dark_patches[:,0], \
                        self.dark_patches[:,1], markersize=8, \
                            marker='s', mec='#cdc9c9', mfc='#cdc9c9', ls='None')
        
        if plot_isolated_stars == True:
            self.load_isolated_stars()
            plt.plot( self.isolated_stars[:,0], \
                        self.isolated_stars[:,1],  'rd' )
        
        if len(overlays) != 0:
            for name, field in overlays.items():
                plt.plot( field[:,0], field[:,1], 'r-.' )
                (lx, ly) = get_label_loc(field)
                plt.text( lx, ly, str(name), fontsize=8, color='red' )
                            
        plt.xlabel( 'RA [deg]', fontsize=font_pt )
        plt.ylabel( 'Dec [deg]', fontsize=font_pt  )
        if year == None: 
            title = 'Events within K2 Campaign ' + \
                    str(self.campaign) + ' footprint'
        else: 
            title = 'Events within K2 Campaign ' + \
                    str(self.campaign) + ' footprint from ' + str(year) 
        plt.title( title, fontsize=font_pt )
        if plot_file == None: plot_file = 'k2-footprint.png'
        (xmin,xmax,ymin,ymax) = plt.axis()
        plt.axis( [xmax,xmin,ymin,ymax] )
        plt.axis('equal')
        plt.tick_params( labelsize=font_pt )
        plt.grid(True)
        plt.savefig( plot_file )
        plt.close(fig)

#####################################################
if __name__ == '__main__':
    config = { 'k2_footprint_data': \
                '/home/robouser/Software/robonet_site/scripts/k2-footprint.json',
               'xsuperstamp_target_data': \
               '/home/robouser/Software/robonet_site/scripts/xsuperstamp_targets.json', 
               'ddt_target_data': \
               '/home/robouser/Software/robonet_site/scripts/c9-ddt-targets-preliminary.csv',
               'tmp_location': \
               '/home/robouser/Software/robonet_site/scripts/'
              }
    k2_campaign = K2Footprint( config, 9, 2016 )
    k2_campaign.load_xsuperstamp_targets( config )
    plot_file = path.join( config['tmp_location'], 'test_k2_footprint.png' )
    k2_campaign.plot_footprint(plot_file=plot_file, targets=\
                k2_campaign.xsuperstamp_targets)
                
