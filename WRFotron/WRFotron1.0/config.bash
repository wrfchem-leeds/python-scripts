#!/bin/bash
# ------------------------------------------------------------------------------
# WRFOTRON v 1.0
# Christoph Knote (LMU Munich)
# 02/2016
# christoph.knote@lmu.de
# ------------------------------------------------------------------------------

# path to where these scripts are
chainDir=/nobackup/username/WRFChem3.7.1_WRFotron1.0_clean/WRF3.7.1_code/WRFotron1.0

. $chainDir/profile.bash

version=0.1

projectTag=wrfchem

withChemistry=true

# WPS installation directory
WPSdir=/nobackup/username/WRFChem3.7.1_WRFotron1.0_clean/WRF3.7.1_code/WPS3.7.1
# WRF installation directory
WRFdir=/nobackup/username/WRFChem3.7.1_WRFotron1.0_clean/WRF3.7.1_code/WRFChem3.7.1
# WRF meteo-only installation directory
WRFmeteodir=/nobackup/username/WRFChem3.7.1_WRFotron1.0_clean/WRF3.7.1_code/WRFMeteo3.7.1
# megan_bio_emiss installation directory
WRFMEGANdir=/nobackup/username/WRFChem3.7.1_WRFotron1.0_clean/WRF3.7.1_code/megan
# mozbc installation directory
WRFMOZARTdir=/nobackup/username/WRFChem3.7.1_WRFotron1.0_clean/WRF3.7.1_code/mozbc
# wesley/exocoldens installation directory
WRFmztoolsdir=/nobackup/username/WRFChem3.7.1_WRFotron1.0_clean/WRF3.7.1_code/wes-coldens
# anthro_emiss installation directory
WRFanthrodir=/nobackup/username/WRFChem3.7.1_WRFotron1.0_clean/WRF3.7.1_code/anthro_emis
# fire_emiss installation directory
WRFfiredir=/nobackup/username/WRFChem3.7.1_WRFotron1.0_clean/WRF3.7.1_code/finn/src

# path to GFS input data
metDir=/nobackup/username/WRFChem3.7.1_WRFotron1.0_clean/WRF3.7.1_data/initial_boundary_meteo
metInc=3

# path to geogrid input data
geogDir=/nobackup/username/WRFChem3.7.1_WRFotron1.0_clean/WRF3.7.1_data/wps_geog
# path to MEGAN input data
MEGANdir=/nobackup/username/WRFChem3.7.1_WRFotron1.0_clean/WRF3.7.1_data/emissions/MEGAN

# raw emission input - the files you read in with anthro_emiss
#emissDir=/nobackup/username/WRFChem3.7.1_WRFotron1.0_clean/WRF3.7.1_data/emissions/EDGAR-HTAP2/MOZART_MOSAIC
# Changing to sector specific EDGAR-HTAP2 emissions
emissDir=/nobackup/username/WRFChem3.7.1_WRFotron1.0_clean/WRF3.7.1_data/emissions/EDGAR-HTAP2/MOZART

# path to FINN fire emissions (requires a / at the end)
fireDir=/nobackup/username/WRFChem3.7.1_WRFotron1.0_clean/WRF3.7.1_data/emissions/FINN/
# FINN fire emissions input file
fireInpFile=fire_emis.mozm.inp

# emission conversion script for anthro_emis - must match emissions in emissDir
#emissInpFile=emis_edgarhtap_mozmos.inp
# Changing to sector specific EDGAR-HTAP2 emissions
emissInpFile=emis_edgarhtap2_mozmos.inp
# year the emissions are valid for (for offset calculation)
emissYear=2010
# MOZART boundary condition files
MOZARTdir=/nobackup/username/WRFChem3.7.1_WRFotron1.0_clean/WRF3.7.1_data/initial_boundary_chem

# where the WRF will run - /glade/scratch/something...
workDir=/nobackup/username/WRFChem3.7.1_WRFotron1.0_clean/wrf-chem_2014_test/run
# where the WRF output will be stored - also maybe /glade/scratch/something...
archiveRootDir=/nobackup/username/WRFChem3.7.1_WRFotron1.0_clean/wrf-chem_2014_test/output
# where the WRF restart files will be stored - also maybe /glade/scratch/something...
restartRootDir=/nobackup/username/WRFChem3.7.1_WRFotron1.0_clean/wrf-chem_2014_test/restart

# remove run directory after run is finished?
removeRunDir=false

nclPpScript=${chainDir}/pp.ncl

#number of cores to run with for each stage
nprocPre=1
nprocMain=32
nprocPost=1

#mpirun for real.exe and wrf.exe
mpiCommandPre=mpirun
mpiCommandMain=mpirun
submitCommand=qsub

usequeue=true
