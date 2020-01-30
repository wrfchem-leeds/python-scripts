"""Example WRF-python script
.. module:: plot_grids
    :platform: Unix (tested on CentOS 7)
.. moduleauther: Helen - CEMAC (UoL)
.. description: Generic plot grids tool. This is an example script for using
                wrf-python module.
   :copyright: © 2020 University of Leeds.
   :license: MIT
.. python version: > 3.0
Example:
    To use::
        python plot_grids.py <ndomains>
        <ndomains> - integer number of domains
    Requires:
       geo_em*.nc files in current working directory
.. wrfchem-leeds/python-scripts:
   https://github.com/wrfchem-leeds/python-scripts
"""
import netCDF4 as nc
import numpy as np
import argparse
from netCDF4 import Dataset
from cartopy import crs
from cartopy.feature import NaturalEarthFeature
import matplotlib.pyplot as plt
import matplotlib as mpl
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from cartopy.feature import (OCEAN, LAKES, BORDERS, COASTLINE, RIVERS,
                             COLORS, LAND)
from wrf import (to_np, getvar, smooth2d, get_cartopy, cartopy_xlim,
                 cartopy_ylim, latlon_coords)

# -----------------------------------------------------------------------------
# Variables:
# -----------------------------------------------------------------------------
# Add additional domains here if more than 6 domains required
domnames = ['d01', 'd02', 'd03', 'd04', 'd05', 'd06']
# edit colours assigned here
edgecols = ['k', 'silver', 'red', 'b', 'm', 'c']
# Standard figsize
fig = plt.figure(figsize=(8, 6))
# Default number domains
ndomains = 3


# ---------------------- Command line arguments -----------------------------
hstring = ("plot_grids.py. Requires geo_em.d0X.nc files to be present in " +
           " current working directory run by using command: \n "
           + "python plot_grids <ndomains> \n ndomains = number of domains")
dstring = ("number of domains (integer)")

parser = argparse.ArgumentParser(description=hstring)
parser.add_argument("ndomains", help=dstring, type=int)
args = parser.parse_args()
ndomains = args.ndomains


# ------------------------ Required functions --------------------------------
def get_plot_element(infile):
    """get_plot_element
    .. description: get boxes from geo_em files to draw on plot
    .. args:
        infile (str): filename (e.g. geo_em.d01.nc)
    .. returns:
        cart_proj
        xlim
        ylim
    """
    rootgroup = nc.Dataset(infile, 'r')
    p = getvar(rootgroup, 'HGT_M')
    cart_proj = get_cartopy(p)
    xlim = cartopy_xlim(p)
    ylim = cartopy_ylim(p)
    rootgroup.close()
    return cart_proj, xlim, ylim


# -------------------- Box dimensions ---------------------------------------
for i in np.arange(ndomains):
    if i == 0:
        infile = 'geo_em.d01.nc'
        cart_proj, xlim_d01, ylim_d01 = get_plot_element(infile)
        xlims = [xlim_d01]
        ylims = [ylim_d01]
    elif i == 1:
        infile = 'geo_em.d02.nc'
        _, xlim_d02, ylim_d02 = get_plot_element(infile)
        xlims = [xlim_d01, xlim_d02]
        ylims = [ylim_d01, ylim_d02]
    elif i == 2:
        infile = 'geo_em.d03.nc'
        _, xlim_d03, ylim_d03 = get_plot_element(infile)
        xlims = [xlim_d01, xlim_d02, xlim_d03]
        ylims = [ylim_d01, ylim_d02, ylim_d03]
    elif i == 3:
        infile = 'geo_em.d04.nc'
        _, xlim_d04, ylim_d04 = get_plot_element(infile)
        xlims = [xlim_d01, xlim_d02, xlim_d03, xlim_d04]
        ylims = [ylim_d01, ylim_d02, ylim_d03, ylim_d04]
    elif i == 4:
        infile = 'geo_em.d05.nc'
        _, xlim_d05, ylim_d05 = get_plot_element(infile)
        xlims = [xlim_d01, xlim_d02, xlim_d03, xlim_d04, xlim_d05]
        ylims = [ylim_d01, ylim_d02, ylim_d03, ylim_d04, ylim_d05]
    elif i == 5:
        infile = 'geo_em.d06.nc'
        _, xlim_d06, ylim_d06 = get_plot_element(infile)
        xlims = [xlim_d01, xlim_d02, xlim_d03, xlim_d04, xlim_d05, xlim_d06]
        ylims = [ylim_d01, ylim_d02, ylim_d03, ylim_d04, ylim_d05, ylim_d06]
        # If more domains required please add below

# -------------------- Main figure -----------------------------------------
ax = plt.axes(projection=cart_proj)
# add coastlines, land, ocean, country boarders, rivers, gridlines
ax.coastlines('50m', linewidth=3, zorder=4)
ax.add_feature(LAND, zorder=1)
ax.add_feature(OCEAN, edgecolor='k', facecolor=COLORS['water'], zorder=3)
ax.add_feature(LAKES, edgecolor='k', zorder=3)
ax.add_feature(BORDERS, edgecolor='k', linewidth=3, linestyle='--', zorder=3)
ax.add_feature(RIVERS, edgecolor='b', linewidth=3, zorder=3)
gl = ax.gridlines(draw_labels=True, alpha=0.1, zorder=2)
gl.xlabels_top = gl.ylabels_right = False
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
# use wrfpython to height above sea level
HGT = getvar(Dataset("geo_em.d01.nc"), "HGT_M")
# Get the latitude and longitude points
lats, lons = latlon_coords(HGT)
# Get the cartopy mapping object
cart_proj = get_cartopy(HGT)
plt.contour(to_np(lons), to_np(lats), to_np(HGT), 10, colors="black",
            transform=crs.PlateCarree(),  alpha=0.4, zorder=2)
plt.pcolormesh(to_np(lons), to_np(lats), to_np(HGT), cmap='terrain',
               vmin=1, vmax=to_np(HGT).max(), alpha=0.6,
               transform=crs.PlateCarree(), zorder=2)


# set fig lims
ax.set_xlim([xlim_d01[0] - (xlim_d01[1] - xlim_d01[0]) / 15,
             xlim_d01[1] + (xlim_d01[1] - xlim_d01[0]) / 15])
ax.set_ylim([ylim_d01[0] - (ylim_d01[1] - ylim_d01[0]) / 15,
             ylim_d01[1] + (ylim_d01[1] - ylim_d01[0]) / 15])

for i in np.arange(ndomains):
    ax.add_patch(mpl.patches.Rectangle((xlims[i][0], ylims[i][0]),
                                       xlims[i][1] - xlims[i][0],
                                       ylims[i][1] - ylims[i][0], fill=None,
                                       lw=3, edgecolor=edgecols[i], zorder=10))
    ax.text(xlims[i][0] + (xlims[i][1] - xlims[i][0]) * 0.01, ylims[i][0] +
            (ylims[i][1] - ylims[i][0]) * 1.01, domnames[i], size=15,
            color=edgecols[i], zorder=10, fontweight='bold')

plt.show()
fig.savefig('WRF_plot_grid.png', dpi=600)
