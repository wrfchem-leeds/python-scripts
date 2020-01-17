#!/bin/bash
# ------------------------------------------------------------------------------
# WRFOTRON
# ------------------------------------------------------------------------------
# code
# ------------------------------------------------------------------------------
# WRFotron
chainDir=/nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_code/WRFotron2.0
version=0.1
projectTag=WRFChem4.0.3
withChemistry=true
# WPS
WPSdir=/nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_code/WPS4.0.3
# WRFChem
WRFdir=/nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_code/WRFChem4.0.3
# WRFMeteo
WRFmeteodir=/nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_code/WRFMeteo4.0.3
# ------------------------------------------------------------------------------
# preprocessors
# ------------------------------------------------------------------------------
# MEGAN
WRFMEGANdir=/nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_code/megan
# MOZBC
WRFMOZARTdir=/nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_code/mozbc
# WESLEY/EXOCOLDENS
WRFmztoolsdir=/nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_code/wes-coldens
# ANTHRO_EMISS
WRFanthrodir=/nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_code/anthro_emis
# FIRE_EMISS
WRFfiredir=/nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_code/finn/src
# ------------------------------------------------------------------------------
# input data
# ------------------------------------------------------------------------------
# initial and boundary meteorological data
metDir=/nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/initial_boundary_meteo_ecmwf
#metDir=/nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/initial_boundary_meteo_gfs
metInc=6
# initial and boundary chemistry data (MZ4/CAM-Chem pre 2018, WACCM post 2018)
MOZARTdir=/nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/initial_boundary_chem_mz4
#MOZARTdir=/nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/initial_boundary_chem_camchem
#MOZARTdir=/nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/initial_boundary_chem_waccm
# geography data
geogDir=/nobackup/wrfchem/WPSGeog4
landuseDir=modis_landuse_21class_30s/
# MEGAN input data
MEGANdir=/nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/emissions/MEGAN
# anthropogenic emissions - data
emissDir=/nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/emissions/EDGAR-HTAP2/MOZART
# anthropogenic emissions - input namelist
emissInpFile=emis_edgarhtap2_mozmos.inp
# anthropogenic emissions - year the emissions are valid for (for offset calculation)
emissYear=2010
# fire emissions from FINN (requires a / at the end)
fireDir=/nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/emissions/FINN/
# FINN fire emissions input file
fireInpFile=fire_emis.mozm.inp
# diurnal cycle code
WRFemitdir=/nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_code/WRF_UoM_EMIT
# ------------------------------------------------------------------------------
# simulation directories
# ------------------------------------------------------------------------------
# run folder
workDir=/nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRFChem4.0.3_test/run
# output folder
archiveRootDir=/nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRFChem4.0.3_test/output
# restart folder
restartRootDir=/nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRFChem4.0.3_test/restart
# remove run directory after run is finished?
removeRunDir=false
# post processing script
nclPpScript=${chainDir}/pp.ncl
# ------------------------------------------------------------------------------
# HPC settings
# ------------------------------------------------------------------------------
# number of cores to run with for each stage
nprocPre=1
nprocMain=32
nprocPost=4
# mpirun for real.exe and wrf.exe
mpiCommandPre=mpirun
mpiCommandMain=mpirun
submitCommand=qsub
usequeue=true
# ------------------------------------------------------------------------------
# misc.
# ------------------------------------------------------------------------------
function msg {
  echo ""
  echo "---"
  echo $1
  echo "---"
  echo ""
}
