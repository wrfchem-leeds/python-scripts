#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 09:58:42 2021
 
Script that corrects for the change in the CNEMC measurement protocol
The change in measurement protocol occured on September 1st 2018
The change is described in 'Impact of China?s Recent Amendments to Air
Quality Monitoring Protocol on Reported Trends' 
https://doi.org/10.3390/atmos11111199
 
For gaseous pollutants, the standard temperature changed from 
0°C -> 25°C
The standard pressure remained 1013.25 hPa
 
For particulate matter, conditions changed from standard temperature 
and pressures, to actual measured temperature and pressures
 
This script uses ERA5 reanalysis data to restrospectively adjust 
pre-September 2018 CNEMC data for this change
 
@author: eebjs
"""
 
from datetime import datetime
import cdsapi
import os
from glob import glob
import xarray as xr
import pandas as pd
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from tqdm import tqdm
 
lookup = pd.read_csv('/nfs/a336/eebjs/bja_2020/station_lookup.csv',
                     index_col = 'station')
 
# path where to save the ERA5 data
spath = '/nfs/b0122/Users/eebjs/ERA5_p_and_T/'
 
#%% download the surface pressure and temperature ERA5 data
 
# function for retrieving ERA5 surface T and P
def get_year_era(year):
    
    startdate = datetime(year=year, month=1, day=1)
    enddate = datetime(year=year, month=12, day=31)
 
    reqdate = startdate.strftime(format='%Y-%m-%d') + '/' +\
              enddate.strftime(format='%Y-%m-%d')
 
    outdate = startdate.strftime(format='%Y%m%d') + '_' +\
              enddate.strftime(format='%Y%m%d')
              
              
    if os.path.exists(spath + 'ecmwf_china_surface_pT_'+outdate+'.nc'):
        print(year, 'already downloaded')
        return
              
    area = '54.1/72.9/17.4/135.6'
 
    c = cdsapi.Client()
 
     # surface
    c.retrieve(
         'reanalysis-era5-single-levels',
         {
             'product_type':'reanalysis',
             'format':'netcdf',
             'variable':[
                 '2m_temperature', 
                 'surface_pressure'
             ],
        'date':reqdate,
        'time':[
            '00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00',
            '07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00',
            '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00',
            '21:00', '22:00', '23:00'
            ],
         'area':area
         },
         spath + 'ecmwf_china_surface_pT_'+outdate+'.nc')
 
# retrieve for years 2014-2018
for year in range(2014,2019):
    get_year_era(year=year)
    
    
#%% interpolate pressure and temperature timeseries
 
metpaths = glob(spath+'ecmwf_china_surface_pT_*.nc')
 
mets = []
for metpath in metpaths:
    
    ds = xr.load_dataset(metpath)
    
    # convert time zone
    newtime = [t + pd.Timedelta(hours=8) for t in ds.coords['time'].values]
    ds.coords['time'] = newtime
    
    # append to list
    mets.append(ds)
 
# concatenate into single ds
met = xr.concat(mets, dim='time')
met = met.reindex(latitude=list(reversed(met.latitude)))
 
# create interpolators
time_dim = np.arange(0, len(met.time))
interpolators = {}
for interpvar in ['t2m', 'sp']:
    
    # create interpolator
    f = RegularGridInterpolator((time_dim, met.latitude.values, 
                             met.longitude.values),
                             met[interpvar].values)
    interpolators[interpvar] = f
    
# interpolate each station
for station in tqdm(lookup.index):
    interps = pd.DataFrame(index=met.time.values, columns=['t2m', 'sp'])
    
    lat, lon = lookup.loc[station, ['lat', 'lon']]
    indexer = np.column_stack([
                               time_dim,
                               [lat]*len(time_dim),
                               [lon]*len(time_dim)
                             ])
    
    for interpvar in ['t2m', 'sp']:
        interped = interpolators[interpvar](indexer)
        interps[interpvar] = interped
        
    interps.to_csv('/nfs/b0122/Users/eebjs/ERA5_p_and_T/interps/'+\
                   station+'.csv')
 
#%% correct data
 
# path to CNEMC netcdfs *A.nc
bja_path = '/nfs/b0122/Users/eebjs/bja_2020/'
# get paths to CNEMC netcdfs
station_paths = glob(bja_path+'*A.nc')
 
# path to save corrected files
out_path = '/nfs/b0122/Users/eebjs/bja_2020/protocol_corrected/'
 
def correct_for_protocol_change(ds, station):
    
    # drop AQI
    ds = ds.drop('AQI')
    
    # slice ds at 2018-09-01
    pre_change = ds.loc[{'time':slice('2018-09-01')}]
    pre_change_index = pre_change.time.values
    
    # adjust gaseous pollutants for standard temperature change
    # C_r = C_s * (T_s / T_r) 
    # which is different to Equation 1, Jin et al., 2020, cos I think that is wrong
    T_s = 273 # K, standard temp
    T_r = 298 # K, reference temp
    for pol in ['CO', 'NO2', 'O3', 'SO2']: 
         C_s = pre_change[pol].values  # conc at standard conditions
         # calculate conc at reference conditions
         C_r = C_s * (T_s / T_r)
         # round to 1dp
         C_r = C_r.round(1)
         # put back into ds
         ds[pol].loc[{'time':slice('2018-09-01')}] = C_r
         
    interps = pd.read_csv('/nfs/b0122/Users/eebjs/ERA5_p_and_T/interps/'+\
                   station+'.csv', index_col=0, parse_dates=True)
         
    # adjust PM using actual conditions
    # C_a = C_s * T_s * P_a / (P * T_a) (Equation 2, Jin et al., 2020)
    P = 101325 # Pa, standard pressure
    for pol in ['PM2.5', 'PM10']:
        C_s = pre_change[pol]  # conc at standard conditions
        # get actual pressure 
        P_a = interps.loc[pre_change_index, 'sp']
        # get actual temperature
        T_a = interps.loc[pre_change_index, 't2m']
        # calculate conc at actual conditions
        C_a = C_s * T_s * P_a / (P * T_a)
        # round to 1dp
        C_a = C_a.round(1)
        # put back into ds
        ds[pol].loc[{'time':slice('2018-09-01')}] = C_a
        
    return ds
        
# iterate through stations, correcting for protocol shift
for station_path in tqdm(station_paths):
    
    station = station_path.split('/')[-1].split('.')[0]
    
    ds = xr.open_dataset(station_path)
    
    # make copy of ds
    new_ds = ds.copy(deep=True)
    
    new_ds = correct_for_protocol_change(new_ds, station=station)
    
    # save corrected ds
    new_ds.to_netcdf(out_path+station+'.nc')
 
