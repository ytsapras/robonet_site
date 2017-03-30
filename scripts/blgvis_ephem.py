# -*- coding: utf-8 -*-
import os
import sys
from time import gmtime, strftime
from datetime import datetime
from math import pi
import numpy as np
import ephem
import matplotlib
from matplotlib import pyplot as plt
from jdcal import gcal2jd
from matplotlib.cm import coolwarm

def generate_visibility_plot():
    ut_current = gmtime()
    t_current_string = datetime.utcnow().strftime('%B %d %Y - %H:%M')
    t_current = gcal2jd(ut_current[0], ut_current[1], ut_current[2])[
        1] - 49999.5 + ut_current[3] / 24.0 + ut_current[4] / (1440.)
    obj = ephem.readdb("ENTRY,f|M|F7," + "17:57:07.0" +
                       "," + "-29:04:45.00" + ",0.0,2000")
    global_sites = ephem.Observer()
    global_sites.epoch = 2000
    #initialise coordinates and assume an altitude of 2500m
    global_sites.long, global_sites.lat, global_sites.elev = '-70.6926', '-29.0146', 2500.0
    lon_plot = []
    lat_plot = []
    alt_plot = []
    for lon in np.arange(-180.0, 180., 3.):
        for lat in np.arange(-90, 90., 3.):
            global_sites.long, global_sites.lat, global_sites.elev = str(lon), str(lat), 2000.
            djd = 50000.0 + t_current - 15020.000000
            dt = ephem.Date(djd)
            global_sites.date = dt
            sol = ephem.Sun()
            sol.compute(global_sites)
            glob_sun_alt = float(ephem.degrees((sol.alt))) * 180 / pi
            if glob_sun_alt < -15.:
                obj.compute(global_sites)
                lun = ephem.Moon()
                lun.compute(global_sites)
                ph = lun.moon_phase
                sep = ephem.separation(obj, lun)
                sepdeg = abs(float(ephem.degrees((sep)))) * 180. / pi
                glob_alt = float(ephem.degrees(obj.alt)) * 180 / pi
                if glob_alt > 15:
                    lon_plot.append(lon)
                    lat_plot.append(lat)
                    alt_plot.append(glob_alt)

    # downloading one of the examples on http://www.gnuplotting.org/plotting-the-world-revisited/ or any other world map contour can be used
    worldmap = np.loadtxt('world_50m.txt')
    fig, ax = plt.subplots()
    plt.xticks(np.arange(-180.001,180.001, 60.))
    plt.yticks(np.arange(-90.001,90.001, 30.))
    plt.title(str(round(t_current,2))+' '+t_current_string)
    plt.plot(worldmap[:, 0], worldmap[:, 1], '.',color='k', markersize=1)
    tmp=plt.scatter(lon_plot, lat_plot, c=alt_plot, cmap=coolwarm)
    #ax.set_xticklabels([])
    #ax.set_yticklabels([])
    plt.grid(alpha=0.3)
    cbar = plt.colorbar(tmp,cmap=coolwarm,orientation='vertical')
    plt.clim(0.,90.)
    plt.savefig('blgvis_now.png')
#    plt.show()

if __name__ == '__main__':
    generate_visibility_plot()
    
