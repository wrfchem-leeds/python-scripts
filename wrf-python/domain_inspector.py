"""Example WRF-python script
.. module:: domain_inspector
    :platform: Unix (tested on CentOS 7)
.. moduleauther: Helen - CEMAC (UoL)
.. description: This is an example script for using wrf-python module to take
                and indepth look at domains. This can be adapted for bespoke
                purpose
   :copyright: © 2020 University of Leeds.
   :license: MIT
.. python version: > 3.0
Example:
    To use::
        python domain_inspector.py
    Requires:
       geo_em*.nc files in current working directory
.. wrfchem-leeds/python-scripts:
   https://github.com/wrfchem-leeds/python-scripts
"""

from netCDF4 import Dataset
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.cm import get_cmap
import cartopy.crs as crs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from cartopy.feature import OCEAN, LAKES, BORDERS, COASTLINE, RIVERS, COLORS
from wrf import (to_np, getvar, smooth2d, get_cartopy, cartopy_xlim,
                 cartopy_ylim, latlon_coords)


# Open the NetCDF files
ncfile1 = Dataset("geo_em.d01.nc")
ncfile2 = Dataset("geo_em.d02.nc")
ncfile3 = Dataset("geo_em.d03.nc")
filelist = [ncfile1, ncfile2, ncfile3]
fig = plt.figure(figsize=(12, 8))
# Assign format baed on domain width
gs = gridspec.GridSpec(5, 6, height_ratios=[0.1, 1, 1, 0.2, 0.2],
                       width_ratios=[1, 1, 1, 1, 1, 1])

# for each file plot the topography
for i, f in enumerate(filelist):
    # Get the sea level pressure
    HGT = getvar(f, "HGT_M")
    # Get the latitude and longitude points
    lats, lons = latlon_coords(HGT)
    # Get the cartopy mapping object
    cart_proj = get_cartopy(HGT)
    # Set the GeoAxes to the projection used by WRF
    if i == 0:
        ax = plt.subplot(gs[0:4, 0:3], projection=cart_proj)
    elif i == 1:
        ax = plt.subplot(gs[0:4, 3:5], projection=cart_proj)
    elif i == 2:
        ax = plt.subplot(gs[0:4, 5:6], projection=cart_proj)
        lat3, lons3 = lats, lons
    gl = ax.gridlines(draw_labels=True, alpha=0.2)
    gl.xlabels_top = gl.ylabels_right = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    if i == 0:
        gl.xlabel_style = {'weight': 'bold', 'fontsize': '16'}
        gl.ylabel_style = {'weight': 'bold', 'fontsize': '16'}
    else:
        gl.xlabel_style = {'weight': 'normal', 'fontsize': '12'}
        gl.ylabel_style = {'weight': 'normal', 'fontsize': '12'}
    # Make the contour outlines and filled contours for the smoothed sea level
    # pressure.
    plt.contour(to_np(lons), to_np(lats), to_np(HGT), 10, colors="black",
                transform=crs.PlateCarree())
    p = plt.pcolormesh(to_np(lons), to_np(lats), to_np(HGT), cmap='terrain',
                       vmin=1, vmax=to_np(HGT).max(), alpha=0.8,
                       transform=crs.PlateCarree(), zorder=1)
    ax.add_feature(OCEAN, edgecolor='k', facecolor=COLORS['water'], zorder=2)
    ax.add_feature(LAKES, edgecolor='k', zorder=2)
    ax.add_feature(COASTLINE, edgecolor='k', linewidth=5)
    ax.add_feature(BORDERS, edgecolor='k', linewidth=3, linestyle='--')
    ax.add_feature(RIVERS, edgecolor='b', linewidth=3, zorder=2)
    # Set the map bounds
    ax.set_xlim(cartopy_xlim(HGT))
    ax.set_ylim(cartopy_ylim(HGT))
    ax.set_title('topography for d0' + str(i + 1), fontweight='bold',
                 fontsize=12)
# Add the gridlines
fig.suptitle("Topography of 3 domains", fontsize=32,
             fontweight='bold')
fig.canvas.draw()
cax = plt.subplot(gs[4, 1:5])
cbar = fig.colorbar(mappable=p, cax=cax, shrink=0.95, orientation='horizontal',
                    extend='both')
cbar.ax.set_xlabel('GMTED2010 30-arc-second topography height (m)',
                   fontsize=16, labelpad=10)
cbar.ax.tick_params(labelsize=20)
plt.tight_layout()
plt.savefig('domains.png')
