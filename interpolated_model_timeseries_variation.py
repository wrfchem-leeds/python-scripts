#!/usr/bin/env python3
import xarray as xr
import pandas as pd
import numpy as np
from scipy.interpolate import RegularGridInterpolator

locations = [(25, 100), (26, 101), (27, 102), (28, 103), (29, 101), (30, 101)]
wrfouts = ['/nfs/a68/eebjs/wrfoutput/p2run/202/ctl2016/feb/wrfout_feb2016_ctl_rgdd25.nc',
           '/nfs/a68/eebjs/wrfoutput/p2run/202/ctl2016/mar/wrfout_mar2016_ctl_rgdd25.nc',
           '/nfs/a68/eebjs/wrfoutput/p2run/202/ctl2016/apr/wrfout_apr2016_ctl_rgdd25.nc',
           '/nfs/a68/eebjs/wrfoutput/p2run/202/ctl2016/may/wrfout_may2016_ctl_rgdd25.nc']
#wrfouts = ['/nfs/a336/earlacoa/paper_aia_china/test_file/wrfout_combined-domains_global_0.25deg_2015-01_PM2_5_DRY.nc']
pol = 'PM2_5_DRY'
level = 0
with xr.open_dataset(wrfouts[0]) as ds:
    if 'time' in ds[pol].coords:
        tdim = 'time'
    elif 'Time' in ds[pol].coords:
        tdim = 'Time'

def get_catda(wrfouts, pol, level, tdim):
    """
    Description:
        Returns a concatenated data array of the files contained within.
    Args:    
        wrfouts (list): List of wrfout files.
        pol (str): Pollutant.
        level (int): Model level as an index location.
        tdim (str): Name of the time dimension.
    Returns:
        catda (xarray DataArray): Concatenate data array.
    """
    da_list = []
    for filepath in wrfouts:
        with xr.open_dataset(filepath) as ds:
            da = ds[pol]
        tdim_len = len(da[tdim])
        if tdim_len > 1:
            da = da.chunk({tdim:tdim_len//10})
        if 'bottom_top' in da.dims:
            da = da.loc[{'bottom_top':level}]
        da_list.append(da)
    catda = xr.concat(da_list, dim=tdim)
    return catda
    
def interpolate_model_timeseries(locations, tdim, times='all'):
    """
    Description:
        Interpolates timeseries at given lat/lon locations.
        The wrfout files must be regridded to a rectilinear grid.
    Args:
        locations (list of tuples): Observation lat lon locations.
        tdim (str): Name of the time dimension.
        times (str, optional): Times of interpolation, default = 'all'.
    Returns:
        df (pandas DataFrame): Interpolated timeseries.
    """
    catda = get_catda(wrfouts, pol, level, tdim)
    time_coord = np.arange(0, len(catda[tdim]))
    print('creating interpolator...')
    f = RegularGridInterpolator((time_coord, 
                                 catda.coords['lat'].values,
                                 catda.coords['lon'].values),
                                 catda.values
                                )
    print('...done')
    df = pd.DataFrame(index=catda[tdim].values)
    for lat, lon in locations:
        indexer = np.column_stack([time_coord,
                                  [lat]*len(time_coord),
                                  [lon]*len(time_coord)])
        series = f(indexer)
        df[(lat,lon)] = series
    return df

if __name__ == '__main__':
    df = interpolate_model_timeseries(locations, tdim, times='all')
