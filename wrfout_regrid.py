#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 10 11:33:51 2018

Runs on a concatenated .nc file. The script can be run on the command line e.g.
    python wrfout_regrid.py *path to file*
The regrid function can also be imported into another python process e.g.
    from wrfout_regrid import regrid

Currently the script converts species ppmv -> µg/m³ using the surface pressure
and temperature

It also sums the size bins of aerosol species

It will create a file with the suffix _rgdd25.nc

ds = DataSet
da = DataArray

@author: eebjs
"""

# dependencies
import xarray as xr
import xesmf as xe
from numpy import arange
import molmass # used to get Mr for unit conversion
import time
import sys
import os


aerosol_species = {'bc','biog1_c','biog1_o','ca','cl','co3','glysoa_sfc',
                   'hysw','na','nh4','no3','num','oc','oin','smpa','smpbb',
                   'so4','water'} # not a complete list

# unit conversion function
def ppm_to_ugm3 (da, da_T2, da_PSFC):
    
    name = da.name
    new_attrs = da.attrs
    
    # get variables needed
    chem = da.name.upper()
    M = molmass.Formula(chem).mass
    R = 8.3145
    
    # convert unit ppmv -> µg/m³
    da = (M * da_PSFC * da) / (R * da_T2)
    
    # update attributes with new units
    new_attrs['units'] = 'ug m^-3'
    new_attrs['description'] = chem + \
                               ' mixing ratio converted to mass concentration'
    da.attrs = new_attrs
    da.name = name
    
    return(da)

# function that floats and rounds to 3dp
def fr(x):
    return((round(float(x),3)))
    
def sum_abins(ds, var, convert_to_conc):
    
    # get size bin DataArrays
    bin_das = []
    for abin in ['_a01', '_a02', '_a03', '_a04']:
        # also get surface level
        bin_das.append(ds[var + abin][:,0])
        
    # sum size bins
    with xr.set_options(keep_attrs=True): 
        sumda = sum(bin_das)
        
    sumda.name = var
    # update description
    sumda.attrs['description'] = sumda.description.split(',')[0] + \
    ' summed aerosol bins'
    
    # convert µg/kg-dryair 
    if convert_to_conc:
        with xr.set_options(keep_attrs=True): 
            sumda = sumda / ds['ALT']
        sumda['units'] = 'ug/m3'
        
    return(sumda)


def regrid(readpath):
    
    # list of variables to regrid:
    rgvars = ['PBLH', 'PM2_5_DRY', 'PM10', 'no2', 'o3', 'so2', 'co',
              'so4', 'no3', 'co3', 'nh4', 'oc', 'bc']
    
    # set resolution of destination grid
    res = .25
    
    # open file to be regridded
    ds = xr.open_dataset(readpath)
    
    # rename spatial coordinates
    ds = ds.rename({'XLONG': 'lon', 'XLAT': 'lat'})
    
    # create destination grid
    dest_grid = {'lon': arange(round(float(ds.lon.min()), 1)-res, 
                               round(float(ds.lon.max()), 1)+res,
                               res),
                 'lat': arange(round(float(ds.lat.min()), 1)-res, 
                               round(float(ds.lat.max()), 1)+res,
                               res)
                  }
    
    # create regridder for the first timestep
    # (should be the same for each timestep as shape of grid stays the same)
    regridder = xe.Regridder(ds.isel(Time=0), dest_grid, 'bilinear')
    
    # append to path to create new filename
    # assumes only '.' in filepath is in filename
    suffix = 'rgdd25'
    writepath = readpath.split('.')[0] + '_' + suffix + '.nc'
    
    # get vars already regridded if any
    already_regridded = []
    if os.path.exists(writepath):
        ds_rgdd = xr.open_dataset(writepath)
        already_regridded = list(ds_rgdd)
        
    
    for i, var in enumerate(rgvars):
        
        # skip if already regridded
        if var in already_regridded:
            print(var, 'already regridded, skipping', var)
            continue
        
        # skip if not present in concatenated file
        if var not in aerosol_species:
            if var not in ds.variables:
                print(var, 'not present, skipping', var)
                continue
        elif var in aerosol_species:
            bin_vars = [var + str(x) for x in [1,2,3,4]]
            if not all(x in ds.variables for x in bin_vars):
                print(var, 'not present, skipping', var)
                continue
            
        # if variable is size binned aerosol species, sum bins to make da
        if var in aerosol_species:
            da = sum_abins(ds, var, convert_to_conc = True)
        
        # if multiple levels, extract surface only
        elif 'bottom_top' in ds[var].dims:
            da = ds[var][:,0]
        else:
            da = ds[var]
        
        if var in ['no2', 'o3', 'so2', 'co']: # <- convert units of these variables
            print('converting', var, 'to µg/m³')
            # use var, T2 and PSFC to convert
            da = ppm_to_ugm3(da, ds['T2'][:,0], ds['PSFC'][:,0])
        
        print('regridding...', var)
        # regrid
        start_time = time.time()
        da_regridded = regridder(da)
        print(var, 'regridding time:', round(time.time()-start_time),
              'seconds')
        
        # preserve time coordinate
        da_regridded = da_regridded.assign_coords(
                Time=[str(t.values)[2:-1] for t in ds.Times])
        
        # preserve some attributes
        attrs = da.attrs
        # add some new attributes
#        attrs['coordinates'] = 'lon lat Time'
        attrs['resolution'] = res
        # update attributes of regridded da
        da_regridded.attrs.update(attrs)
        
        # use this to control compression of output netcdf
        encode_dict = {var:{'zlib': True, 'complevel': 9, 'shuffle':True}}
        
        print('writing...')
        
        # if new file needs to be created:
        if i == 0:
        # for the first variable, the netcdf is written
            da_regridded.to_netcdf(writepath, format='NETCDF4', mode='w',
                                   encoding = encode_dict)
            print('written', var ,'to: \n', writepath)
        # for subsequent variables, the netcdf is appended to
        else:
            da_regridded.to_netcdf(writepath, format='NETCDF4', mode='a',
                                   encoding = encode_dict)
            print('appended', var ,'to: \n', writepath)

def main():
    regrid(sys.argv[1])
    
if __name__ == '__main__':
    main()