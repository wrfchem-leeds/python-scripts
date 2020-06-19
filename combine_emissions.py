#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 09:43:24 2019

Script for merging TNO and NAEI emission files
;
;  This is based on Doug Lowes NCL script to do the same thing 
;  but with TNO/NAEI whereas we will use EDGAR/NAEI
;    - treatment of the emission variables will be hardcoded, 
;      so that we can check for existence of NAEI emissions.
;
;   Rules for merging:
;     1) EDGAR emissions will only be taken where there are no
;         NAEI emissions (this will be based on a total summation of 
;         NAEI emissions, rather than done on a species by species basis).
;     2) A multiplying factor of 1.6 is applied to OC_DOM, OC_TRA, and OC_25_10
;               emissions (to roughly account for the Carbon to "everything" mass ratio for OM)
;     4) OIN 2.5 PM species will be either the difference between
;               E_PM25 and the sum of BC_1 + EC_1_25 + OC_DOM + OC_TRA
;           or 10% of the E_PM25 mass (whichever is smaller)
;          (we'll make sure that all emissions are >0)
;     5) OIN 10 PM species will be the difference between
;               E_PM_10 and the sum of OC_25_10 + EC_25_10
;          (we'll make sure that all emissions are >0)
@author: ee15amg
"""
import numpy as np
from netCDF4 import Dataset
from netCDF4 import num2date, date2num
#import time
#from scipy.io.netcdf import netcdf_file
#import matplotlib.pyplot as plt

# define input and output files
filename_edgar = ('wrfchemi_edgar_00z_d01')
filename_naei = ('wrfchemi_naei_00z_d01')
filename_combined = ('wrfchemi_00z_d01')

# open the files for processing
F_NAEI = Dataset(filename_naei,"r")
F_EDGAR = Dataset(filename_edgar,"r")
F_OUT = Dataset(filename_combined, "w")
#F_OUT = netcdf_file(filename_combined, "w")

# full list of variables (for calculating the total NAEI emissions)
var_full = (['E_CH4','E_ECI','E_ECJ','E_CO','E_C2H2','E_NH3','E_NO',
             'E_NO2','E_ORGI','E_ORGJ','E_PM_10','E_PM25I','E_PM25J',
             'E_SO2','E_BIGALK','E_BIGENE','E_C2H4','E_C2H5OH','E_C2H6',
             'E_CH2O','E_CH3CHO','E_CH3COCH3','E_CH3OH','E_MEK','E_TOLUENE',
             'E_C3H6','E_C3H8','E_BENZENE','E_XYLENE'])

# list of variables for which we filter TNO emissions to avoid clashs with
# NAEI emissions
var_filter = (['E_CH4','E_ECI','E_ECJ','E_CO','E_C2H2','E_NH3','E_NO',
             'E_NO2','E_ORGI','E_ORGJ','E_PM_10','E_PM25I','E_PM25J',
             'E_SO2','E_BIGALK','E_BIGENE','E_C2H4','E_C2H5OH','E_C2H6',
             'E_CH2O','E_CH3CHO','E_CH3COCH3','E_CH3OH','E_MEK','E_TOLUENE',
             'E_C3H6','E_C3H8','E_BENZENE','E_XYLENE'])

#create output netcdf following same layout as input files

#;;;;;;;;;;;;;; operational section of script ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

# loop through variables to pull out for making full NAEI summation
#   (units don't matter here - it's a purely binary check)
var_tot = np.zeros([12,1,139,139])
for i_var in range(len(var_full)):
    var_temp = np.asarray(F_NAEI[var_full[i_var]])
    var_tot[:,:,:,:]=(var_tot[:,:,:,:] + var_temp[:,:,:,:])


# create data mask to apply to TNO data
# initialise mask to correct dimensions
naei_empty = var_tot[:,:,:,:]*0.0 
# set mask to zero where there's NAEI data - and 1.0 where there isn't
mask= np.where(var_tot==0) 
naei_empty[mask] = naei_empty[mask]+1.0
#check mask works
#print np.max(var_tot[mask])

## create NETCDF file to put data into
##create Dimensions
#
#get number of hours from netcdf data 
lenDateStr = len(np.asarray(F_NAEI['Times'])[0,:])
n_lons = np.size(np.asarray(F_NAEI['XLONG'])[0,:])
n_lats = np.size(np.asarray(F_NAEI['XLAT'])[0,:])
n_emis = np.size(np.asarray(F_NAEI['E_CO'])[0,:,0,0])
n_times = np.size(np.asarray(F_NAEI['Times'])[:,0])

# copy all global attributes from old file to new one 
# also copy old dimensions from old to new netcdf
F_OUT.setncatts(F_EDGAR.__dict__)
for name, dimension in F_EDGAR.dimensions.items():
        F_OUT.createDimension(
            name, (len(dimension) if not dimension.isunlimited() else None))
 
# add dimensions into netcdf
#Time = F_OUT.createDimension("Time",n_times)
#emissions_zdim_stag = F_OUT.createDimension("emissions_zdim_stag",n_emis)
#south_north = F_OUT.createDimension("south_north",n_lats)
#west_east = F_OUT.createDimension("west_east",n_lons)
#DateStrLen = F_OUT.createDimension("DateStrLen",lenDateStr)

#create Variables
Times = F_OUT.createVariable("Times","S1",("Time","DateStrLen")),
XLONG = F_OUT.createVariable("XLONG","f4",("south_north","west_east")), 
XLAT = F_OUT.createVariable("XLAT","f4",("south_north","west_east"))
for i_var in range(np.size(var_full)):
    var_filter[i_var] = F_OUT.createVariable((var_filter[i_var]),"f4",
            ("Time","emissions_zdim_stag","south_north","west_east"))

# fill basic variables manually
lat = np.asarray(F_NAEI['XLAT'])
lon = np.asarray(F_NAEI['XLONG'])
datetime = np.asarray(F_NAEI['Times'])
XLAT = lat
XLONG = lon
Times = datetime 

# then loop through chem species to add them into file
#loop through the variables to be combined (in a straightforward manner)
for i_var in range(len(var_filter)):
	
    # load data
    var_edgar = np.asarray(F_EDGAR[var_full[i_var]])
    var_naei= np.asarray(F_NAEI[var_full[i_var]])
    
    # merge data files - applying the filter 
    # where naei data exists we wont input edgar vars 
    #(multiplying them by zero takes care of this)                                                 
    var_naei_new = var_naei + naei_empty*var_edgar
    
    # save data
    #print var_full[i_var]
    var_filter[i_var][:,:,:,:] = var_naei_new[:,:,:,:]

F_OUT.close()
    

