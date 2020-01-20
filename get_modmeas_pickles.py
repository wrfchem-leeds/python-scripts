#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  6 11:20:12 2019

@author: eebjs
"""

import xarray as xr
import pandas as pd
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from calendar import monthrange


meas_dirpath = '/nfs/a68/eebjs/bja_ncs_2018update/'
rootdir = '/nfs/a68/eebjs/wrfoutput/p2run/202/'

stations_df = pd.read_csv('/nfs/a68/eebjs/bja_ncs_2018update/station_lookup.csv',
                          index_col = 'station')


def good_stations_list(pol, 
                       path = '/nfs/a68/eebjs/output/datafiles/slopes_ds_mda8.csv'):
    df = pd.read_csv(path)
    idx = pd.IndexSlice
#    df =   df.loc[(df['station_lat'] > 19.97)\
#                & (df['station_lat'] < 42.52)\
#                & (df['station_lon'] > 95.23)\
#                & (df['station_lon'] < 128.01), :]
    df = df.rename(columns={'station_lat':'lat', 'station_lon':'lon'})
    df = df.set_index(['station', 'lat', 'lon', 'pollutant'])
    df = df.loc[idx[:,:,:,pol], :]
    good = list(df[df['slope'].notnull()].index.get_level_values('station'))
#    df = df[df['pstars'].isin(['*', '**', '***'])]
    return(good)
    

def get_catda(pol, runtype):
    
    poltr = {'O3':'o3', 'PM2.5':'PM2_5_DRY', 
             'SO2':'so2', 'NO2':'no2'}
    
    if runtype == 'ctl':
        years = [('ctl', '2015'),('ctl', '2016'),('ctl', '2017')]
    elif runtype == 'ce':
        years = [('ctl', '2015'),('ce', '2016'),('ce', '2017')]
    
    # load das for pol
    monthdirs = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    months = []
    for runtype, year in years:
        
        yeardir = rootdir + runtype+year + '/'
        for monthi, month in enumerate(monthdirs):
            cdir = yeardir + '/'
            print(month)

            da = xr.open_dataset(cdir + month + '/wrfout_'+ month + year + '_' + runtype + '_rgdd25.nc',
                                 chunks={'Time':100})[poltr[pol]]
            
            
            # pad missing hours with NaN
            hrs_in_month = monthrange(int(year), monthi+1)[1] * 24
            if len(da.Time) < hrs_in_month:
                print('!!!!!')
                tval = da['Time'].drop('XTIME').values
                for x in reversed(range(0,13)):
                    print(str(x))
                    s = year +  '-01-01_'+str(x).zfill(2)+':00:00'
                    tval = np.concatenate(([s],tval))
                da_newdim = xr.DataArray([np.nan]*len(tval), dims='Time', coords={'Time':tval})
                da = da.reindex_like(da_newdim)
            

            print(len(da.Time))
            if 'XTIME' in da.coords:
                da = da.drop('XTIME')
            if 'bottom_top' in da.dims:
                da = da.loc[dict(bottom_top=0)]
            if 'bottom_top' in da.coords:
                da = da.drop('bottom_top')
            months.append(da)
            da.close()
    
    catda = xr.concat(months, dim='Time')
    
    # create pandas DatetimeIndex
    datetimes = pd.to_datetime(catda.coords['Time'], format='%Y-%m-%d_%H:%M:%S')
#    time = pd.DatetimeIndex(start=datetimes[0], end=datetimes[-1], freq='H')
    
    # convert to local time
    time = datetimes.tz_localize('UTC').tz_convert('Asia/Shanghai')
    
    # convert time coordinate to datetime64
    catda.coords['Time'] = time
    
    return(catda)
    
# gets a timeseries to match the wrfout times for a measurement station
def get_measurement_timeseries(station, pol, meanby, da_tdim):
    
    # open station dataset
    mxr = xr.open_dataset(meas_dirpath+'/'+station + '.nc')
    # add times to coordinate
    mxr  = mxr.assign_coords(time=mxr['times'].values)
    
    da_tdim = pd.to_datetime(da_tdim)
    
    # extract pol and times arrays
    try:
        pxr = mxr[pol.upper()]
    except KeyError: # catching this error to avoid stations without certain variables
        return(None)
        
    meas_times = pd.DatetimeIndex(mxr['times'].values).tz_localize('Asia/Shanghai')
    
    # get index of 'time' supplied to function 
#    tidx = np.searchsorted(meas_times, wrf_times)
    start = np.searchsorted(meas_times, da_tdim[0])
    end =   np.searchsorted(meas_times, da_tdim[-1])
#    tidx = np.delete(tidx, np.argwhere(tidx == len(meas_times)))
    
    # slice pxr to match wrf_times
#    pxrdf = pxr[start:end].to_pandas()
    pxrdf = pxr.to_pandas()
    
    if not meanby == 'H':
        mean_pxrdf = pxrdf.resample(meanby).mean()
    else:
        mean_pxrdf = pxrdf
    mean_pxrdf.name = pol+'_meas'
    
    mxr.close()
    
    return(mean_pxrdf)
    
def get_model_timeseries(f, station, time_dim, mda_time, stations_df, pol):
    
    lat, lon = stations_df.loc[station][['lat', 'lon']]
    
    
    indexer = np.column_stack([time_dim,
                               [lat]*len(time_dim),
                               [lon]*len(time_dim)])
    
    interped = f(indexer)
    
    df = pd.DataFrame(index=mda_time, data={pol+'_mod':interped})
    
    return(df)
    

def get_pearson_r(pol, meanby):
    da = get_catda(pol, 'ctl')
    da_tdim = da.Time.values
    # resample by meanby
    if not meanby == 'H':
        mda = da.resample({'Time':meanby}).mean('Time')
    else:
        mda = da
    mda_time = mda.Time.values
    
    time_dim = np.arange(0, len(mda.Time))
    
    # build interpolator function
    f = RegularGridInterpolator((time_dim, mda.lat.values, mda.lon.values),
                                 mda.values)
    
    stations = good_stations_list(pol)
    df = pd.DataFrame()
    for station in stations:
        
        lat, lon = stations_df.loc[station][['lat', 'lon']]
        if not (9.85 < lat < 48.35) & (84.65 < lon < 137.15):
            print(station, 'out of bounds')
            continue
        
        
        meas = get_measurement_timeseries(station=station, pol=pol, 
                                          meanby=meanby, da_tdim=da_tdim)
        
        mod = get_model_timeseries(f=f, station=station, pol=pol,
                                   time_dim=time_dim, mda_time=mda_time,
                                   stations_df=stations_df, lat=lat,
                                   lon=lon)
        
        
        both = mod.join(meas)
        # calculate r
        r = both[pol+'_mod'].corr(both[pol+'_meas'])
        # calculated normalised mean bias
        NMB = (both[pol+'_mod']-both[pol+'_meas']).sum()/both[pol+'_meas'].sum()
        print(station, 'r:', r)
        print(station, 'NMB:', NMB)
        df.loc[station, 'r'] = r
        df.loc[station, 'NMB'] = NMB
        df.loc[station, 'lat'] = lat
        df.loc[station, 'lon'] = lon
        
    return(df)
    
def get_measmod_df(station, pol):
    meas = get_measurement_timeseries(station=station, pol=pol, meanby='H',
                                      da_tdim=da_tdim)
    if meas is None:
        return(None)
    meas.index =  meas.index.tz_localize('Asia/Shanghai')

    
    
    mod = get_model_timeseries(f=f, station=station, time_dim=time_dim,
                               mda_time=da_tdim, stations_df=stations_df,
                               pol=pol)
    mod.index = pd.to_datetime(mod.index).tz_localize('UTC').tz_convert('Asia/Shanghai')
    
    return(mod.join(meas, how='right'))
    
for pol in ['PM2.5', 'O3', 'SO2', 'NO2']:

    da = get_catda(pol, 'ctl')
    da_tdim = da.Time.values
    time_dim = np.arange(0, len(da.Time))
    f = RegularGridInterpolator((time_dim, da.lat.values, da.lon.values),
                                 da.values)
    
        
    for station in stations_df.index:
        print(station, pol)
        
        lat, lon = stations_df.loc[station][['lat', 'lon']]
        if not (9.85 < lat < 48.35) & (84.65 < lon < 137.15):
            print(station, 'out of bounds')
            continue
        
        df = get_measmod_df(station, pol)
        if df is None:
            continue
        df.lat = lat
        df.lon = lon
        # save
        df.to_pickle('/nfs/a68/eebjs/meas_v_mod/'+station+'_'+pol+'.P')
        df.to_csv('/nfs/a68/eebjs/meas_v_mod/'+station+'_'+pol+'.csv')
