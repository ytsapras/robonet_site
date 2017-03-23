# -*- coding: utf-8 -*-
import os
import sys
from time import gmtime, strftime
from math import pi
import numpy as np
import ephem
import matplotlib
from matplotlib import pyplot as plt
from jdcal import gcal2jd


def generate_visibility_plot():
    ut_current = gmtime()
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

    worldmap = np.loadtxt('wrld.txt')
    fig, ax = plt.subplots()
    plt.xticks(np.arange(-180,180, 30.))
    plt.yticks(np.arange(-90,90, 15.))
    plt.plot(worldmap[:, 0], worldmap[:, 1], '.',color='k', markersize=1)
    plt.scatter(lon_plot, lat_plot, c=alt_plot, cmap='nipy_spectral')
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    plt.grid(alpha=0.3)
    plt.show()

if __name__ == '__main__':
    generate_visibility_plot()
    
