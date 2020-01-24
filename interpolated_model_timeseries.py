#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 13:32:52 2020

Concatenates a list of wrfout files, then interpolates timeseries at given 
lat, lon locations
The wrfout files must have been regridded to a rectilinear grid
Returns a dataframe with the interpolated timeseries

@author: eebjs
"""

import xarray as xr
import pandas as pd
import numpy as np
from scipy.interpolate import RegularGridInterpolator

### Inputs ####################################################################

# a list of lat, lon tuples
locations = [(25, 100), (26, 101), (27, 102), (28, 103), (29, 101), (30, 101)]

# a list of filepaths to regridded wrfout files
wrfouts = ['/nfs/a68/eebjs/wrfoutput/p2run/202/ctl2016/feb/wrfout_feb2016_ctl_rgdd25.nc',
           '/nfs/a68/eebjs/wrfoutput/p2run/202/ctl2016/mar/wrfout_mar2016_ctl_rgdd25.nc',
           '/nfs/a68/eebjs/wrfoutput/p2run/202/ctl2016/apr/wrfout_apr2016_ctl_rgdd25.nc',
           '/nfs/a68/eebjs/wrfoutput/p2run/202/ctl2016/may/wrfout_may2016_ctl_rgdd25.nc']

#wrfouts = ['/nfs/a336/earlacoa/paper_aia_china/test_file/wrfout_combined-domains_global_0.25deg_2015-01_PM2_5_DRY.nc']

# a string of the data variable that should be extracted from the wrfout file 
pol = 'PM2_5_DRY'

# an integer representing the model level (z dim) to interpolate at 
level = 0

# name of co-ordinate used for time dimension
time = 'Time'

###############################################################################

# returns a concatenated data array of the files contained within 
def get_catda(wrfouts, pol, level):
    da_list = []
    for filepath in wrfouts:
        
        ds = xr.open_dataset(filepath)
        da = ds[pol]
            
        # chunk along time dim if length <1 
        tdim_len = len(da[time])
        if tdim_len > 1:
            da = da.chunk({time:tdim_len//10})
        
        if 'bottom_top' in da.dims:
            # slice by level
            da = da.loc[{'bottom_top':level}]
        
        da_list.append(da)
        
        
    catda = xr.concat(da_list, dim=time)
    
    return(catda)
    
def interpolate_model_timeseries(locations, times='all'):
    
    catda = get_catda(wrfouts=wrfouts, pol=pol, level=level)
    
    time_coord = np.arange(0, len(catda[time]))
    
    print('creating interpolator...')
    f = RegularGridInterpolator((time_coord, 
                                 catda.coords['lat'].values,
                                 catda.coords['lon'].values),
                                 catda.values
                                )
    print('...done')
    
    df = pd.DataFrame(index=catda[time].values)
    
    for lat, lon in locations:
        indexer = np.column_stack([time_coord,
                                  [lat]*len(time_coord),
                                  [lon]*len(time_coord)])
    
        series = f(indexer)
        
        df[(lat,lon)] = series
        
    return(df)


if __name__ == '__main__':
    interpolate_model_timeseries(locations=locations, times='all')
