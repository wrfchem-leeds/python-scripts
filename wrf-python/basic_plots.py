"""Example WRF-python script
.. module:: plot_grids
    :platform: Unix (tested on CentOS 7)
.. moduleauther: Helen - CEMAC (UoL)
.. description: Example plotting of basic variables
   :copyright: © 2020 University of Leeds.
   :license: MIT
.. python version: > 3.0
Example:
    To use::
        python basic_plots.py
    Requires:
       editting <location> L38 and <doms> L37
.. wrfchem-leeds/python-scripts:
   https://github.com/wrfchem-leeds/python-scripts
"""
import netCDF4 as nc
from netCDF4 import Dataset
from cartopy import crs
import numpy as np
from cartopy.feature import NaturalEarthFeature
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
from matplotlib.colors import from_levels_and_colors
import matplotlib as mpl
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from cartopy.feature import (OCEAN, LAKES, BORDERS, COASTLINE, RIVERS, COLORS,
                             LAND)
from wrf import (to_np, getvar, smooth2d, get_cartopy, cartopy_xlim,
                 cartopy_ylim, latlon_coords)
from wrf import (getvar, to_np, vertcross, smooth2d, CoordPair, GeoBounds,
                 get_cartopy, latlon_coords, cartopy_xlim, cartopy_ylim)
from wrf import getvar, interplevel, to_np, get_basemap, latlon_coords

# Required info
doms = ['d01', 'd02', 'd03']
location = "raw_output/"
date = "2016-06-20_00:00:00"
# Manually set the contour levels
slp_levels = np.arange(995., 1020., 5.0)
td2_levels = np.arange(62.5, 74., .5)

for dom in doms:
    # generate filename from info
    ncfile = Dataset(location + "wrfout_" + dom + "_" + date")
    wrf_file = Dataset(location + "wrfout_" + dom + "_" + date")

    # Get the slp, td2, u, and v variables
    slp = getvar(wrf_file, "slp", timeidx=0)
    td2 = getvar(wrf_file, "td2", timeidx=0, units="degF")
    u_sfc = getvar(wrf_file, "ua", timeidx=0, units="kt")[0, :]
    v_sfc = getvar(wrf_file, "va", timeidx=0, units="kt")[0, :]

    # Get the cartopy object and the lat,lon coords
    cart_proj = get_cartopy(slp)
    lats, lons = latlon_coords(slp)

    # Create a figure and get the GetAxes object
    fig = plt.figure(figsize=(12, 13))
    geo_axes = plt.axes(projection=cart_proj)

    # Download and add the states and coastlines
    # See the cartopy documentation for more on this.
    states = NaturalEarthFeature(category='cultural',
                                 scale='50m',
                                 facecolor='none',
                                 name='admin_1_states_provinces_shp')
    geo_axes.add_feature(states, linewidth=2.0, edgecolor='black', zorder=2)


    # Manually setting the td2 RGB colors (normalized to 1)
    # These colors originated from the now defunct hoot.metr.ou.edu
    # They work well for detecting moisture boundaries (e.g. the dryline)
    td2_rgb = np.array([[181, 82, 0], [181, 82, 0],
                        [198, 107, 8], [206, 107, 8],
                        [231, 140, 8], [239, 156, 8],
                        [247, 173, 24], [255, 189, 41],
                        [255, 212, 49], [255, 222, 66],
                        [255, 239, 90], [247, 255, 123],
                        [214, 255, 132], [181, 231, 148],
                        [156, 222, 156], [132, 222, 132],
                        [112, 222, 112], [82, 222, 82],
                        [57, 222, 57], [33, 222, 33],
                        [8, 206, 8], [0, 165, 0],
                        [0, 140, 0], [3, 105, 3]]) / 255.0

    td2_cmap, td2_norm = from_levels_and_colors(td2_levels, td2_rgb,
                                                extend="both")

    # Make the pressure contour lines
    slp_contours = plt.contour(to_np(lons),
                               to_np(lats),
                               to_np(slp),
                               levels=slp_levels,
                               colors="black",
                               transform=crs.PlateCarree())

    # Make filled contours of dewpoint
    plt.contourf(to_np(lons),
                 to_np(lats),
                 to_np(td2),
                 levels=td2_levels,
                 cmap=td2_cmap,
                 norm=td2_norm,
                 extend="both",
                 transform=crs.PlateCarree())

    # Plot the wind barbs, but only plot ~10 barbs in each direction.
    thin = [int(x / 10.) for x in lons.shape]
    plt.barbs(to_np(lons[::thin[0], ::thin[1]]),
              to_np(lats[::thin[0], ::thin[1]]),
              to_np(u_sfc[::thin[0], ::thin[1]]),
              to_np(v_sfc[::thin[0], ::thin[1]]),
              transform=crs.PlateCarree())

    # Add contour labels for pressure
    plt.clabel(slp_contours, fmt="%i")

    # Add a color bar. The shrink often needs to be set
    # by trial and error.
    plt.colorbar(ax=geo_axes, shrink=1.0, extend="both")

    # Set the map bounds
    plt.xlim(cartopy_xlim(slp))
    plt.ylim(cartopy_ylim(slp))
    plt.title('dewpoint (colour), slp (contours), surface windspeed (barbs)')
    plt.savefig(dom + 'overview.png')
