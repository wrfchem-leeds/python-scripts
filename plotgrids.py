#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 16 14:11:51 2018

@author: eebjs
"""

from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt
import re
import os
import argparse

shp_path = '/nfs/see-fs-02_users/eebjs/OneDrive/AIA_project/scripts/shapefiles/'

# setup optional arguments for script
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--tissot", help="display tissot's indicatrix",
                    action="store_true")
parser.add_argument("-e", "--etopo", help="display etopo map background",
                    action="store_true")
parser.add_argument("-s", "--suggest", help="suggest truelat 1 & 2",
                    action="store_true")
args = parser.parse_args()

def firstint(string):
    if len(string.split(',')) > 1:
        return(float(string.split(',')[0]))
    else:
        return(float(string))
    

### READ FILE
nl  = open(os.getcwd()+'/namelist.wps.blueprint', 'r')

lines = nl.read().split(',\n')

# lines to use:
use = ['e_we', 'e_sn', 'dx', 'dy', 'ref_lat','ref_lat', 'ref_lon', 'truelat1',
       'truelat2']

d = {}
for line in lines:
    slines = line.split('=')
    slines = [re.sub(' +',' ', x) for x in slines]

    
    if any(x in slines[0] for x in use):
        d[slines[0].strip()] = firstint(slines[1].strip())


### PLOT MAP

# setup lambert conformal basemap.
# lat_1 is first standard parallel.
# lat_2 is second standard parallel (defaults to lat_1).
# lon_0,lat_0 is central point.
# rsphere=(6378137.00,6356752.3142) specifies WGS84 ellipsoid
# area_thresh=1000 means don't plot coastline features less
# than 1000 km^2 in area.

plt.figure(figsize=(10, 10))

m = Basemap(width=d['dx']*d['e_we'],height=d['dy']*d['e_sn'],
            rsphere=(6378137.00,6356752.3142),\
            resolution='l',area_thresh=1000.,projection='lcc',\
            lat_1=d['truelat1'],lat_2=d['truelat2'],lat_0=d['ref_lat'],
            lon_0=d['ref_lon'])
m.drawcoastlines()
m.drawcountries(zorder=3)
if args.etopo:
    m.etopo(zorder=2, alpha=1)
m.fillcontinents(color='coral',lake_color='aqua')
m.readshapefile(os.path.join(shp_path, 'CHN_adm1'), 'states1', drawbounds=True,
                    zorder = 3, color = 'black')

if not args.suggest:
    # draw parallels and meridians.
    m.drawparallels(np.arange(-80.,81.,5.),labels=[False,True,True,False], zorder=3)
    m.drawmeridians(np.arange(-180.,181.,5.),labels=[True,False,False,True], zorder=3)
else:
    # suggest truelat1 and 2
    parallels = m.drawparallels(np.arange(-80.,81.,1.),labels=[False,True,True,False], zorder=3)
    meridians = m.drawmeridians(np.arange(-180.,181.,1.),labels=[True,False,False,True], zorder=3)
    minp, maxp = min(list(parallels.keys())), max(list(parallels.keys()))
    third = (maxp-minp)/3
    print('minimum latitude ~= '+str(minp))
    print('maximum latitude ~= '+str(maxp))
    print('set truelat1 ~= '+str(minp+third))
    print('set truelat2 ~= '+str(maxp-third))

# draw tissot's indicatrix to show distortion.
ax = plt.gca()
if args.tissot:
    for y in np.linspace(m.ymax/20,19*m.ymax/20,9):
        for x in np.linspace(m.xmax/20,19*m.xmax/20,12):
            lon, lat = m(x,y,inverse=True)
            poly = m.tissot(lon,lat,1.5,100,\
                            facecolor='green',zorder=3,alpha=0.3)
            


plt.title("WRF-Chem domain")
plt.show()
