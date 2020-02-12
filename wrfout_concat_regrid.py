#!/usr/bin/env python3
import xarray as xr
import salem
import os
import glob
import xesmf as xe
import numpy as np

year   = '2015'
month  = '01'
res    = 0.25
domains = ['1', '2']
variables = ['PM2_5_DRY', 'o3', 'AOD550_sfc']
aerosols = ['bc', 'oc', 'nh4', 'so4', 'no3', 'asoaX', 'bsoaX', 'oin']
variables.extend(aerosols)
surface_only = 'yes'
regrid = 'yes'

for domain in domains:
    path = os.getcwd()
    filelist = []
    filelist.extend(glob.glob(path + '/wrfout_d0' + domain + '_' + year + '-'+ month + '*'))
    filelist = sorted(filelist)
    for variable in variables:
        with salem.open_mf_wrf_dataset(filelist, chunks={'Time': -1}) as ds:
            if (surface_only == 'yes') and (variable in aerosols):
                wrf_a01 = ds[variable + '_a01'].isel(bottom_top=0)
                wrf_a02 = ds[variable + '_a02'].isel(bottom_top=0)
                wrf_a03 = ds[variable + '_a03'].isel(bottom_top=0)
                wrf = wrf_a01 + wrf_a02 + wrf_a03
            elif (surface_only == 'yes') and (variable == 'PM2_5_DRY') or (variable == 'o3'):
                wrf = ds[variable].isel(bottom_top=0)
            else:
                wrf = ds[variable]

        if regrid == 'yes':
            ds_out = xr.Dataset({'lat': (['lat'], np.arange(-60, 85, 0.25)), 'lon': (['lon'], np.arange(-180, 180, 0.25)),})
            regridder = xe.Regridder(wrf, ds_out, 'bilinear', reuse_weights=True)
            wrf_regrid = regridder(wrf)

        if variable in aerosols:
            wrf_regrid.to_netcdf(path + '/wrfout_d0' + domain + '_global_'+ str(res) +'deg_' + year + '-' + month + '_' + variable + '_2p5.nc')
        else:
            wrf_regrid.to_netcdf(path + '/wrfout_d0' + domain + '_global_'+ str(res) +'deg_' + year + '-' + month + '_' + variable + '.nc')

    regridder.clean_weight_file()
