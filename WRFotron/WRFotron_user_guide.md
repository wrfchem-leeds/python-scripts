## WRFotron user guide
### Tools to automatise WRF-Chem runs with re-initialised meteorology  
WRFotron created by Christoph Knote (christoph.knote@lmu.de)  
User guide created by Luke Conibear (l.a.conibear@leeds.ac.uk)  
*Helpful additions from Carly Reddington, Ben Silver, Laura Kiely, Thomas Thorp, Ailish Graham, Doug Lowe, Scott Archer-Nicholls, and Edward Butt.*  
#### Version
0.0 15/10/2015 CK - Initial release  
1.0 01/06/2018 LC  
2.0 01/02/2019 LC  
#### License  
Free of charge for non-commercial use. If you intend to publish something based on WRF simulations made using the WRFotron scripts, and you think this contributed substantially to you research, please consider offering co-authorship.
___
### Contents
1. [Background and further information](#background)  
2. [Before you start](#before)  
3. [Setup](#setup)  
    a. [Steps](#steps)  
    b. [Conda](#conda)  
4. [Compilation](#compile)  
5. [Manual simulation](#manual)  
6. [Automatic simulation (i.e. WRFotron)](#auto)  
    a. [How it works](#auto-how)  
    b. [Running](#auto-running)  
7. [Versions](#versions)  
8. [Miscellaneous](#misc)  
    a. [Recommendations](#recom)  
    b. [Output process](#output)  
    c. [Troubleshooting and errors](#errors)  
    d. [Download ECMWF meteorlogy files](#ecmwf)  
    e. [To run with a nest](#nest)  
    f. [To run with cumulus parameterisation off](#cumpar)  
    g. [Changes for WRF-Chem version 4](#wrfchem4)  
    h. [To run with a diurnal cycle](#diurnal)  
    i. [To run with NAEI emissions](#naei-emissions)
___
### 1. Background and further information <a name="background"/>
- National Center for Atmospheric Research (NCAR) Weather Research and Forecasting (WRF) Model Users [website](http://www2.mmm.ucar.edu/wrf/users/).  
- NCAR WRF with chemistry (WRF-Chem) [website](https://www2.acom.ucar.edu/wrf-chem).  
- National Oceanic and Atmospheric Administration (NOAA) WRF-Chem [website](https://ruc.noaa.gov/wrf/wrf-chem/).  
- WRF version 4.0 [user guide](https://www2.mmm.ucar.edu/wrf/users/docs/user_guide_V4/WRFUsersGuide_july2018_tutorial.pdf).  
- WRF-Chem version 3.9.1.1 [user guide](https://ruc.noaa.gov/wrf/wrf-chem/Users_guide.pdf).  
- WRF-Chem emissions version 3.9.1.1 [user guide](https://ruc.noaa.gov/wrf/wrf-chem/Emission_guide.pdf).  
- WRF workshops, in person, UK [here](https://www.ncas.ac.uk/index.php/en/wrf-tutorials).  
- Past WRF-Chem presentation [here](http://www2.mmm.ucar.edu/wrf/users/workshops/).  
- WRF-Chem tutorials [here](https://ruc.noaa.gov/wrf/wrf-chem/tutorialexercises.htm).  
- Fire INventory from NCAR (FINN) emission preparation [here](https://github.com/lukeconibear/wrf-analysis/blob/master/WRFotron/additional_docs/FINN_Emiss_prep_MOZART.pdf).  
- Guidance for Model for Ozone and Related Chemical Tracers (MOZART) gas scheme with Model for Simulating Aerosol Interactions and Chemistry (MOSAIC) aerosol scheme [here](https://github.com/lukeconibear/wrf-analysis/blob/master/WRFotron/additional_docs/MOZART_MOSAIC_V3.6.readme_dec2016.pdf). 
- Key papers:  
    - Grell, G.A., Peckham, S.E., Schmitz, R., McKeen, S.A., Frost, G., Skamarock, W.C., Eder, B., 2005. Fully coupled “online” chemistry within the WRF model. Atmos. Environ. 39, 6957–6975. [DOI](https://doi:10.1016/j.atmosenv.2005.04.027).  
    - Fast, J. D., Gustafson, W. I., Easter, R. C., Zaveri, R. A., Barnard, J. C., Chapman, E. G., et al. (2006). Evolution of ozone, particulates, and aerosol direct radiative forcing in the vicinity of Houston using a fully coupled meteorology-chemistry-aerosol model. Journal of Geophysical Research: Atmospheres, 111(21), 1–29. [DOI](https://doi.org/10.1029/2005JD006721).  
    - Skamarock, W. C., & Klemp, J. B. (2008). A time-split nonhydrostatic atmospheric model for weather research and forecasting applications. Journal of Computational Physics, 227(7), 3465–3485. [DOI](https://doi.org/10.1016/j.jcp.2007.01.037).  
- Information regarding WRF Model citations (including a DOI) can be found [here](http://www2.mmm.ucar.edu/wrf/users/citing_wrf.html).  
- The WRF Model is open-source code in the public domain, and its use is unrestricted. The name "WRF", however, is a registered trademark of the University Corporation for Atmospheric Research. The WRF public domain notice and related information may be found [here](http://www2.mmm.ucar.edu/wrf/users/public.html).  
___
### 2. Before you start <a name="before"/>
- [Register](http://www2.mmm.ucar.edu/wrf/users/download/wrf-regist.php) as a WRF-Chem user.  
- Require knowledge of Linux (bash shell, grep, cut, sed, sort, awk, cat, scp) / FORTRAN (basics) / Python (mainly version 3, with small use of version 2) / high-performance computing (qsub) / [NCO](http://nco.sourceforge.net/) / [NCL](http://www.meteo.mcgill.ca/ncar/ngdoc/ng4.0/ug/ncl/ncloview.html).  
- Request account on your local high-performance computer (HPC). For those at the University of Leeds visit Advanced Research Computing (ARC) site [here](https://arc.leeds.ac.uk/apply/getting-an-account/).  
___
### 3. Setup <a name="setup"/>
- Change username and all paths specific to your own.
- For submissions to HPC (.bash), may require own project ID.
#### a. Steps <a name="steps"/>
- Log into your HPC (e.g. ARC3/4).  
`ssh –Y username@arc4.leeds.ac.uk`  
- Copy [WRF-Chem version 4.0.3](https://github.com/wrf-model/WRF) and [WRFotron version 2.0](https://github.com/lukeconibear/wrf-analysis/tree/master/WRFotron/WRFotron2.0) to your nobackup.  
    - Copy from LC's (earlacoa) ARC3/4 account. If complete this step, then skip next section.   
`cd nobackup`  
`mkdir username`  
`cd username`  
`cp –r /nobackup/earlacoa/WRFChem4.0.3_WRFotron2.0_clean .`  
        - Contains WRF4.0.3_code:  
            - anthro_emis (anthropogenic emissions preprocessor).  
            - fire_emiss (fire emissions preprocessor).  
            - megan (biogenic emissions preprocessor).  
            - mozbc (preprocessor for lateral boundary and initial conditions).  
            - wes-coldens (exocoldens and season_wesely, O<sub>2</sub> and O<sub>3</sub> column densities and dry deposition).  
            - flex (tool for generating scanners: programs which recognize lexical patterns in text).  
            - WRF Pre-Processing System (WPS) version 4.0.3.  
            - WRF with meteorology only version 4.0.3.  
            - WRF-Chem version 4.0.3.  
            - [WRFotron version 2.0](https://github.com/lukeconibear/wrf-analysis/tree/master/WRFotron/WRFotron2.0).  
                - This is called the "chain" directory, and contains only program code and configuration file blueprints. Data and run directories will reside elsewhere.   
            - [WRF_UoM_EMIT](https://github.com/douglowe/WRF_UoM_EMIT).  
                - An NCL based pre-processing script, for generating anthropogenic emissions files for use with WRF-Chem. Created by Doug Lowe.  
        - Contains WRF4.0.3_data:  
            - Emissions.  
                - EDGARHTAP2 files for MOZART chemical regime (anthropogenic emissions, sector specific, annual, specie specific).  
                - MEGAN files (biogenic emissions files).  
                - FINN files (fire emissions).  
            - Initial and boundary meteorology.  
                - GFS.  
                - ECMWF.  
            - Initial and boundary chemistry.  
                - MZ4 (MOZART) / CAM-Chem (pre 2018).  
                - WACCM (post 2018).  
            - Files for test run folder for manual practice simulation (testrun_files).  
            - Geography files for WPS.  
                - These are in a shared directory (/nobackup/wrfchem).  
    - If cannot copy from LC's ARC3/4 account, then:  
        - Download [WRF-Chem version 4.0.3](https://github.com/wrf-model/WRF).  
            - Make two copies:  
                - One with chemistry.  
                - One without chemistry.  
        - Download [WPS](https://github.com/wrf-model/WPS).  
        - Download [WPS Geography files](https://www2.mmm.ucar.edu/wrf/users/download/get_sources_wps_geog.html).  
        - Download [WRFotron version 2.0](https://github.com/lukeconibear/wrf-analysis/tree/master/WRFotron/WRFotron2.0).   
        - Download flex (tool for generating scanners: programs which recognize lexical patterns in text).  
        - Download and compile (in serial) preprocessors from [here](https://www2.acom.ucar.edu/wrf-chem/wrf-chem-tools-community):  
            - anthro_emis (anthropogenic emissions preprocessor).  
                - Compile (first 5 steps required for all):  
`export FC=ifort`  
`module load intel netcdf`  
`module unload intelmpi`  
`export NETCDF_DIR=/apps/developers/libraries/netcdf/4.6.3/1/intel-19.0.4`  
`export NETCDF_DIR=$NETCDF`  
`./make_anthro`  
            - fire_emiss (fire emissions preprocessor).  
`./make_fire_emis`  
            - megan (biogenic emissions preprocessor).  
`./make_util megan_bio_emiss`  
            - mozbc (preprocessor for lateral boundary and initial conditions).  
`./make_mozbc`  
            - wes-coldens (exocoldens and season_wesely, O<sub>2</sub> and O<sub>3</sub> column densities and dry deposition).  
`./make_util wesely`  
`./make_util exo_coldens`  
            - Check preprocessors have the correct modules and libraries linked via: ldd preprocessor.  

#### b. Conda <a name="conda"/>
- Download the latest [miniconda](https://docs.conda.io/en/latest/miniconda.html)  
`wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh  `
- Run bash script, read terms, and set path  
`bash Miniconda3-latest-Linux-x86_64.sh  `
- Create conda environment for running WRF-Chem with python 3 (including data science recommended, NCL, and NCO):  
`conda create -n python3_ncl_nco -c conda-forge -c oggm xarray salem xesmf wrf-python geopandas numpy scipy pandas netcdf4 matplotlib pyresample jupyter basemap rasterio affine regionmask pyhdf geoplot memory_profiler jupyterlab nodejs ncl nco `  
- To activate/deactivate conda environment:  
`conda activate python3_ncl_nco  `  
`conda deactivate  `  
- For more information on conda, visit [here](https://docs.conda.io/projects/conda/en/latest/user-guide/index.html).  
- Create separate environments for downloading ecmwf (requires python2) and ncview, which you can then load temporarily to execute these functions:  
`conda create -n python2_ecmwf -c conda-forge ecmwf-api-client`  
`conda create -n ncview -c eumetsat -c conda-forge ncview libpng`  
___
### 4. Compilation <a name="compile"/>
```
#!/bin/bash
# example compilation script for WRF-Chem version 4.0.3

# modules
conda deactivate
module unload conda
module unload openmpi
module load intel
module load intelmpi
module load netcdf

# environment variables - shell
export FC=ifort
export NETCDF=$(nc-config --prefix)
export NETCDF_DIR=$NETCDF
export YACC='/usr/bin/yacc -d'
export FLEX_LIB_DIR='/nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_code/flex/lib'
export LD_LIBRARY_PATH=$FLEX_LIB_DIR:$LD_LIBRARY_PATH
export JASPERLIB=/usr/lib64
export JASPERINC=/usr/include

# environment variables – WRF-Chem
export WRF_EM_CORE=1 # selects the ARW core
export WRF_NMM_CORE=0 # ensures that the NMM core is deselected
export WRF_CHEM=1 # selects the WRF-Chem module
export WRF_KPP=1 # turns on Kinetic Pre-Processing (KPP)
export WRFIO_NCD_LARGE_FILE_SUPPORT=1 # supports large wrfout files

# WRF-Chem compilation
cd /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_code/WRFChem4.0.3
./clean -a
./configure
# HPC option will be specific to your HPC architecture 
# ARC3 = 15 = INTEL (ifort/icc) (dmpar) e.g. Distributed-Memory Parallelism MPI
# Compile for basic nesting: option 1
# Compile real (as oppose to ideal simulations)
# thousands of messages will appear. Compilation takes about 20-30 minutes.
./compile em_real >& log.compile
# how do you know your compilation was successful?
# --> if you have WRFChem4.0.3/main/wrf.exe
# check the executables have all relevant linked libraries: ldd real.exe

# WRF Preprocessing System (WPS) compilation - requires a successfully compiled WRF
cd /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_code/WPS4.0.3
./clean -a
./configure
# HPC option will be specific to your HPC architecture 
# ARC3 = 17 = INTEL (ifort/icc) (serial)
# sometimes configure.wps can assign the incorrect path to WRFChem, check and edit if required:
# gedit configure.wps
# or set as an environment variable
#export WRF_DIR="/nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_code/WRFChem4.0.3"
./compile >& log.compile
# how do you know your compilation was successful?
# --> if you have geogrid.exe/metgrid.exe/ungrib.exe
# check the executables have all relevant linked libraries: ldd geogrid.exe

# WRF (meteo only) compilation
export WRF_CHEM=0    # deselects the WRF-Chem module
cd /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_code/WRFMeteo4.0.3
./clean -a
./configure
# HPC option will be specific to your HPC architecture 
# ARC3 = 15 = INTEL (ifort/icc) (dmpar)
# Compile for basic nesting: option 1
# Compile real (as oppose to ideal simulations)
# thousands of messages will appear. Compilation takes about 20-30 minutes.
./compile em_real >& log.compile
# check have WRFMeteo4.0.3/main/wrf.exe
# check the executables have all relevant linked libraries: ldd real.exe

# If make any changes to pre-processor settings then require a fresh re-compile
# also check if preprocessor requires a different module version that currently compiled with
# run above environment variables to get NetCDF
# add -lnetcdff to Makefile
# note for wes_coldens: FC hardcoded in make_util
# downloaded tools from http://www.acom.ucar.edu/wrf-chem/download.shtml

# If need JASPER
#cd WRF4.0.3_code
#wget http://www2.mmm.ucar.edu/wrf/OnLineTutorial/compile_tutorial/tar_files/jasper-1.900.1.tar.gz
#tar xvfz jasper-1.900.1.tar.gz
#./configure
#make
#make install
#export JASPERLIB=/usr/lib64 #not installed need own jasper
#export JASPERINC=/usr/include

# If need FLEX
#cd /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_code/flex/lib
#./configure --prefix=$(pwd)/../flex
#export FLEX_LIB_DIR='/nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_code/flex/lib'
```
___
### 5. Manual simulation <a name="manual"/>
Independently run a 24 hour simulation for India from 2016 10 05.

- Check you have the GFS data you need for the dates required to initialise and force meteorological conditions (1 file per 3 hours, 8 files per day, none are too small):  
`cd /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/initial_boundary_meteo_gfs`  
    - If require more GFS data:  
`cd /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_code/download_and_find_gfs_mz4`  
`get_GFS_analysis_2004-current.bash`  
`get_GFS_analysis_parallel.bash`  
- Create a test run folder for the manual run of WRF:  
`cd /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/`  
`mkdir testrun`  
- Copy link_grib.csh to the new folder.  
`cd /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/testrun`  
`cp /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/testrun_files/link_grib.csh .`  
- Link the required GFS data via link_grib.csh in to the new simulation folder.  
`./link_grib.csh /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/initial_boundary_meteo_gfs/GF201610*`  
- Copy over the ungrib, geogrid and metgrid folders.  
`cp -r /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/testrun_files/ungrib .`  
`cp -r /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/testrun_files/geogrid .`  
`cp -r /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/testrun_files/metgrid .`  
- Link the ungrib, geogrid and metgrid executables from the folders that are now copied over.  
`ln -sf metgrid/src/metgrid.exe`  
`ln -sf geogrid/src/geogrid.exe`  
`ln -sf ungrib/src/ungrib.exe`  
- Copy over the WPS and input namelists.  
`cp /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/testrun_files/namelist.wps .`  
`cp /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/testrun_files/namelist.input .`  
- Link to the variables table.  
    - If post-2015 simulation, use new variable table:  
`ln -sf /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_code/Vtable.GFS_new Vtable`  
    - If pre-2015 simulation, use old variable table.  
`ln -sf /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_code/Vtable.GFS Vtable`  
- Copy over the WRF and real executables, and the WRF and real bash scripts for job submission.  
`cp /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/testrun_files/real.exe .`  
`cp /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/testrun_files/real.bash .`  
`cp /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/testrun_files/wrf.exe .`  
`cp /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/testrun_files/wrf.bash .`  
- Edit the time for the run on the WPS namelist according to the new requirements for the simulation. Be careful for leap years, and any changes made in the WPS namelist have to mirrored if the same variables are present in the input namelist.  
    - start_date = '2016-10-05_00:00:00'.  
    - end_date   = '2016-10-06_00:00:00'.  
    - number of domains (use 1).  
    - spatial resolution (dx and dy).  
    - map projection (i.e. Lambert conformal, Mercator, polar stereographic, or Regular latitude-longitude also known as cylindrical equidistant).  
        - If ‘lambert’, dx and dy are in metres.  
    - Uses projection parameters: truelat1, truelat2, stand_lon.  
        - See page 37 of WRF User Guide.  
- Update and edit the namelist.input.  
    - make sure the run_hours, start date, end date, timestep, e_we, e_sn, dx, dy are the same here as they are in the namelist.wps.  
    - time step for integration seconds (recommended 6*dx in km for a typical case).  
- Load the netCDF module.  
`module load netcdf`  
`export NETCDF=$(nc-config --prefix)`  
`export NETCDF_DIR=$NETCDF`  
- Run geogrid.  
`./geogrid.exe`  
    - configures the horizontal domain, interpolating static geographical data.  
    - creates geography (geo_em.d01.nc) for each domain.  
    - Progress logged in geogrid.log.  
- Run ungrib.  
`./ungrib.exe`  
    - reads, reformats, and extracts meteo input data.  
    - creates meteorology by ungribbing the GFS grb2 files.  
    - intermediate files for every time step.  
    - Progress logged in ungrib.log.  
- Run metgrid.  
`./metgrid.exe` 
    - ingests and interpolates input data creating initial and boundary meteorological conditions.  
    - create met_em.d01.2016-02-25_00:00:00.nc for every 6 hour time step, for both domains.  
    - also metgrid.log.  
- Copy the anthro_emiss, wesely, exo_coldens, megan_bio_emiss, mozbc executables.  
`cp /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/testrun_files/anthro_emis .`  
`cp /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/testrun_files/wesely .`  
`cp /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/testrun_files/exo_coldens .`  
`cp /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/testrun_files/megan_bio_emiss .`  
`cp /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/testrun_files/mozbc .`  
- Copy the input files for these executables.  
`cp /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/testrun_files/emis_edgarhtap2_mozmos.inp .`  
`cp /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/testrun_files/wesely.inp .`  
`cp /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/testrun_files/exo_coldens.inp .`  
`cp /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/testrun_files/megan_bio_emiss.inp .`  
`cp /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/testrun_files/mozbc.inp .`  
- Copy over the run subdirectory from WRF.  
`cp -r /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_code/WRFChem4.0.3/run/* .`  
- Remove the testrun version of real.exe and wrf.exe and copy the freshly compiled versions.  
`rm real.exe`  
`rm wrf.exe`  
`cp /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_code/WRFChem4.0.3/main/real.exe .`  
`cp /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_code/WRFChem4.0.3/main/wrf.exe .`  
- Link the required MOZART chemical boundary condition files (need previous day too for spin up).  
`ln -sf /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_data/initial_boundary_chem_mz4/MZ2014jan moz0000.nc`  
    - Pre-2018.  
        - Download [MZ4](http://www.acom.ucar.edu/wrf-chem/mozart.shtml).  
        - Download [CAM-Chem](https://www.acom.ucar.edu/cam-chem/cam-chem.shtml).  
    - Post-2018 download [WACCM](https://www.acom.ucar.edu/waccm/download.shtml).  
    - Note the directory needs to change in config.bash (MOZARTdir).  
    - Can access individual days using the script.  
`cd /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_code/download_and_find_gfs_mz4`  
`. get_MZ4_fcst.bash YYYY MM DD`  
- Edit bash script for real.exe.  
`vi real.bash`  
    - this has all the requirements for time, nodes, cores, processors.  
    - 1 core required, with h_vmem 6GB.  
    - May need to change the project code.  
- Before running real.exe, may need to comment out (with a ! in Fortran) in namelist.input aux_input_6 for megan_bio_emiss (3 lines which relates to this).  
- Check namelists, run real, and check progress.  
`qsub real.bash`  
    - interpolates between the intermediate files to create the time domain data at the prescribed time intervals.  
`qstat`  
    - when complete, creates:  
        - real.bash.o3502300.  
            - output from the job submission script (MPI output from job id 3502300).  
        - real.bash.e3502300.  
            - error from the job submission script (MPI output from job id 3502300).  
    - namelist.output.  
        - wrfinput_d01 (for initial conditions).  
        - wrfinput_d02 (for initial conditions).  
        - wrfbdy_d01 (for boundary conditions).  
        - check rsl.error* that the run was successful.  
    - If it fails, the wrfinput and wrfbdy won't be created.  
        - Check in rsl.error* and rsl.out* files for each core.  
- Edit namelist for biogenic emissions.  
`vi megan_bio_emiss.inp`  
- Run MEGAN.  
`./megan_bio_emiss < megan_bio_emiss.inp`  
    - Creates for both domains - wrfbiochemi_d.  
- Edit and run mozbc.  
`vi mozbc.inp`  
    - domain 1, do_ic = .true.  
        - Updates wrfinput_d01 (netCDF) with initial conditions.  
    - domain 1, do_bc = .true.  
        - Updates wrfbdy_d01 (netCDF) with boundary conditions.  
        - If ncview wrfbdy_d01, then can see the 2D curtains in space of the boundary conditions (think of box walls), i.e. T is transect or not, X or Y domain, E east or S south.  
    - domain 2, do_ic = .true.  
        - Updates wrfinput_d02 (netCDF) with initial conditions for the nested domain, as gets its boundary conditions from the outer domain.  
`./mozbc < mozbc.inp`  
- Run wesely.  
    - Reads, reformats, and extracts input data for dry deposition.  
    - Copy over the season_wes_usgs.nc file from ~/wrf_new/wes-coldens.  
`cp /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_code/wes-coldens/season_wes_usgs.nc .`  
`./wesely < wesely.inp`  
    - creates wrf_season_wes_usgs_d01.nc and wrf_season_wes_usgs_d02.nc.  
- Run EXO COLDENS. 
    - Reads, reformats, and extracts input data.  
    - Copy over the exo_coldens.nc file from ~/wrf_new/wes-coldens.  
`cp /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_code/wes-coldens/exo_coldens.nc .`  
`./exo_coldens < exo_coldens.inp`  
    - creates exo_coldens_d01 and exo_coldens_d02
- Edit anthropogenic namelist (check the NO/NO2 ratio from NOX is correct for your domain).  
`vi emis_edgarhtap2_mozmos.inp`  
- Run ANTHRO.  
`./anthro_emis < emis_edgarhtap2_mozmos.inp`  
    - run for both domain 1 and 2 separately.  
    - change the start_output_time and stop_output_time.  
    - creates wrfchemi.  
- Before running wrf.exe, may need to comment back in (removing the !) in namelist.input aux_input_6 for megan_bio_emiss (3 lines which relates to this).  
- Create bash script for wrf.exe.  
`vi wrf.bash`  
    - this has all the requirements for time, nodes, cores, processors.  
    - 32 cores required.  
- Run wrf.exe.  
`qsub wrf.bash`  
    - Can follow the progress by tailing the rsl.error.0000 file.  
`tail rsl.error.0000`  
    - Can also check jobs running on HPC through.  
`qstat`  
    - Creates.  
        - wrfout files per hour.  
        - rsl.out.* (for each core).  
        - rsl.error.* (for each core).  
- Check linked files were for this username and not earlacoa.  
- Post-processing.  
    - not doing in the test run.  
- To view wrfout files (without the post-processing).  
`conda activate ncview`  
`ncview wrfout*`  
___
### 6. Automatic simulation (i.e. WRFotron) <a name="auto"/>
#### a. How it works <a name="auto-how"/>
- WRFotron is used by calling the `master.bash` bash script. `master.bash` takes a starting date, a run time, a spinup time, and (optionally) a previous run's job ID on the queuing system as arguments.  
- According to the run configuration in `config.bash`, WRFotron then prepares a run directory (typically on scratch/nobackup) with all necessary data, and submits 3 jobs to the queue:  
    - a preprocessing script (`pre.bash`), containing calls to ungrib.exe, metgrid.exe, real.exe and the preprocessor tools for chemistry.  
    - a main execution script (`main.bash`), which does the actual wrf.exe runs (spinup and chemistry run).  
    - a postprocessing script (`post.bash`), which can be extended to do any kind of postprocessing on the wrfout* files of the WRF-Chem run.  
- Calling `master.bash` and giving it the job ID of another WRFotron `main.bash` process in the queue will tell the `main.bash` script to wait for this process to end before starting - thereby allowing you to submit several runs in a row at the same time, each of them restarting using the result of the previous run.  
- The re-initialisation of meteorology works as follows:  
    - After each successful WRFotron WRF-Chem run, wrfrst restart files are saved in a common directory. When a new run is called using `master.bash`, a meteo-only spinup run is made first, and a restart file is created at its end - now containing only "fresh" meteorology variables. It is then checked whether a restart file (with chemistry) from a previous run exists in the common restart directory. If this is the case, only the chemistry variables are copied from the previous run's restart file to the meteo spinup restart file. Then, a WRF-Chem run is started using this combined restart file as initial conditions, thereby using "fresh" meteorology while carrying on chemistry variables across runs. In case no restart file is found, a "cold start" chemistry run is conducted, starting with MOZART global model forecast values as initial conditions.
- If main.bash breaks in the middle of the simulation, can restart using `main_restart.bash`:  
    - Edited to not repeat the meteo spin up and carry on from where chem wrf.exe stopped.
    - Steps:
        - Go to the run folder where main.bash stopped
        - Copy the latest restart file with 00 hours over to the restart/base directory
        - Edit main_restart.bash:
            - Change newRunRstFile to this latest restart file
            - Change submission time length appropriately
            - Change lastRstFile to the final restart file date at the end of run
            - Change curDate to the first wrfout file date
        - Edit namelist.input:
            - Ensure restart = .true.
            - Change start date to match date of newRunRstFile
        - `qsub main_restart.bash`
        - When finished:
            - Manually copy over the final restart file to restart/base
            - Manually move the wrfout files to run/base/staging
            - Manually `qsub post.bash`
- Other files within WRFotron:  
    - pp.ncl (post-processing script).  
        - Calculates AOD for 550nm through interpolations and just extracting for the surface.  
        - Converts units of aerosols (µg / kg of dry air) to (µg/m3) at a certain STP (standard temperature and pressure, there is 3 types), by dividing by the inverse of density (ALT i.e. m3/kg).  
    - WRF-Chem namelists (read /WRFChem4.0.3/run/README.namelist or user guide for detailed information).  
        - namelist.chem.  
        - namelist.wrf.  
        - namelist.wps.  
    - Vtable.ECMWF/GFS.  
        - Variable table for the intial and boundary meteorological conditions.  
    - preprocessor input files (emis_edgarhtap2_mozmos.inp, exo_coldens.inp, fire_emis.mozm.inp, mozbc.inp, megan_bio_emiss.inp, mozbc.inp.blueprint_201_mz4, mozbc.inp.blueprint_202_mz4).     
    - For files which depend on the aerosol / chemistry schemes (mozbc.inp, namelist.chem, and namelist.wrf), there are blueprints of each of these files for both the mozart_mosaic_4bin (chem_opt=201) and the mozart_mosaic_4bin_aq (chem_opt=202). See [document](https://github.com/lukeconibear/wrf-analysis/blob/master/WRFotron/additional_docs/MOZART_MOSAIC_V3.6.readme_dec2016.pdf).  
        - Replace the contents of the namelist with the blueprint_201 / 202 version.  
- Crontab script.  
    - Not normally allowed, check with HPC staff first.  
    - Touches all files in /nobackup/username – to update their date and stop them getting deleted. 
    - Create a hidden file in home directory (`vi ~/.not_expire.sh`) and add to it triples of lines such as:  
`cd /nobackup/username`  
`find . -exec touch -ah {} \;`  
`find . -exec touch -a {} \;`  
        - touch -h makes sure symlinks don’t expire too.  
        - This script will change the last accessed date for all the specified directories and files underneath that path.  
        - Change permissions 755 on .not_expire.sh (`chmod 755 ~/.not_expire.sh`).  
        - Use the crontab command to edit the crontab file.  
`crontab -e`  
            - The add a line:  
`0 4 4 * * ~/.not_expire.sh`  
        - This has now set a cronjob to run that will automatically touch (and thus reset last accessed time) the files once a month at 0400 on the 4th of the month.
        - runs on the login nodes
- Simulation folder layout – automatically created by WRF-Chem.  
    - Output/Base/ (NetCDF files for wrfout).  
    - Restart/Base/ (Restart files for simulation runs).  
    - Run/Base/Folder per simulation run/ (Everything gets created in here, specific to run).  
    - Run/Base/Staging (wrfout files are stored for post-processing).  
    
#### b. Running <a name="auto-running"/>
- Acquire meteorological NCEP GFS files.  
    - Will have to change all scripts with dataDir locations to the correct username.  
`cd /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_code/download_and_find_gfs_mz4`  
`get_GFS_analysis_2004-current.bash`  
`get_GFS_analysis_parallel.bash`  
    - If these have a size of 0, use FNL analysis files at lower resolution from [here](https://rda.ucar.edu/datasets/ds083.2/index.html#!description).  
        - The Globus Transfer Service (GridFTP) option to transfer the FNL files from the RDA.  
        - The other option is to go to that link, click data access, click web file listing for either GRIB1 (pre 2007.12.06) or GRIB2 (post 2007.12.06), click complete file list, click on the year of interest within the group ID column and checkbox the timeframe you're interested in. Now either click csh download script and follow the instructions in the comments of the script (remembering to change your linux shell to csh), or click get as a tar file (though this is limited to 2GB), or again there is the option for globus.
        - To download for more than 1 day at a time. First changing the script to the time frame required, ensuring download for the spin-up timeframe too.  
    - Go over GFS folder to check have 8 files per day for each day of simulation.  
`.find_missing_GFS.bash`  
`qsub find_missing_GFS_parallel.bash`  
    - Rename FNL files to original GFS naming convention and copy for 3 hourly interval midpoints.
- Acquire MOZART (MZ4) files for chemical initial and boundary conditions.  
    - Pre-2018.  
        - Download [MZ4](http://www.acom.ucar.edu/wrf-chem/mozart.shtml).  
        - Download [CAM-Chem](https://www.acom.ucar.edu/cam-chem/cam-chem.shtml).  
    - Post-2018 download [WACCM](https://www.acom.ucar.edu/waccm/download.shtml). 
    - Ensure for a month have day either side of time frame of interest, and go for global domain.  
- Emissions.  
    - Choose anthropogenic input namelist – setting in config.bash.  
`cd /nobackup/username/WRFChem4.0.3_WRFotron2.0_clean/WRF4.0.3_code/WRFotron2.0`  
`vi emis_edgarhtap2_mozmos.inp`  
    - Fire emissions (FINN).  
        - Update fire_emis.mozm.inp to have to correct filename for the year of simulation – careful to update file for the correct chemical mechanism.  
- Config.bash.  
    - Check all directories are correct.  
    - Change where wrf will run.  
    - Keep the same name for synchronous runs.  
    - Or if a new simulation, change.  
        - workDir / achiveRootDir / restartRootDir.  
- Check pre.bash.  
    - Check the linked MZ4 files are for timeframe required – e.g. 2015.  
    - If using daily files, use this portion of code and comment out the monthly section.  
    - Vice versa for if using monthly files.  
- namelist.wps.blueprint.  
    - Change domain, resolution, map projection, map area.  
    - Edit namelist.wps.domain_test to try out different domain settings.  
    - Create domain plot `ncl plotgrids.ncl`.  
    - View the PDF of the domain `evince wps_show_dom.pdf`.  
    - When decided update setting in namelist.wps.blueprint.  
- namelist.wrf.blueprint.  
    - Change domain, resolution, number of levels.  
- namelist.chem.blueprint.  
    - Change chemistry options.  
    - See WRF-Chem User Guide.  
- Master.bash.  
    - Calling master.bash without arguments gives you usage instructions:  
`. master.bash`  
`Call with arguments <year (YYYY)> <month (MM)> <day (DD)> <hour (hh)> ...  `  
`                 or <year (YYYY)> <month (MM)> <day (DD)> <hour (hh)> ...  `  
` possible options (have to go before arguments):  `  
`                  -e <experiment name>  `  
`                  -c <chain directory (submission from CRON)>`  
    - Master.bash submits pre.bash, main.bash and post.bash.  
    - creates output, restart and run directories on /nobackup/username.  
        - /run/base/startdate_enddate.  
    - in this folder is all the files copied over with the settings updated in all the bash scripts (master, pre, main, post, config).  
    - test run for 24 hours.  
`. master.bash 2016 10 05 00 24 06`  
        - Start year / start month / start day / start hour (UTC time) / simulation length / spin up length.  
        - Spin-up runs from 2016-10-04_18:00:00 to 2016-10-05_00:00:00.  
        - Simulation runs from 2016-10-05_00:00:00 to 2016-10-06_00:00:00.  
        - check linked files were for this username and not earlacoa.  
    - Now make another run starting when the first one finishes, which will use the output of the previous run for chemistry initial conditions (rather than MOZART chemical boundary conditions), while re-initialising meteorology (from GFS/ECMWF data):
`. master.bash 2016 10 05 00 24 06 999999`   
        - The 999999 is the job id for the `main.bash` from the previous run. This is used in the syntax to tell the HPC machine to wait until this job has finished before starting the new run. This is because the new run uses the files created from the first run. This allows you to submit several runs in a row at the same time, each of them restarting using the result of the previous run.
        - Four-dimension data assimilation (FDDA, i.e. re-initialisation of meteorology).  
`vi master.bash`  
`S/GRIDFDDA/0/g #(to turn it off)`  
`S/GRIDFDDA/1/g #(to turn it on)`  
        - Nudges horizontal and vertical wind, potential temperature and water vapor mixing ratio to analyses. It doesn’t take the analyses fields for its values like some other models do. It uses them as initial conditions and then uses the primitive atmospheric equations. This is not for chemistry directly, though affects chemicals through transport.  
    - After each successful WRFotron WRF-Chem run, wrfrst restart files are saved in the restart directory. When a new run is called using `master.bash`, a meteo-only spinup run is made first, and a restart file is created at its end - now containing only "fresh" meteorology variables. It is then checked whether a restart file (with chemistry) from a previous run exists in the common restart directory. If this is the case, only the chemistry variables are copied from the previous run's restart file to the meteo spinup restart file. Then, a WRF-Chem run is started using this combined restart file as initial conditions, thereby using "fresh" meteorology while carrying on chemistry variables across runs. In case no restart file is found, a "cold start" chemistry run is conducted, starting with MOZART global model forecast values as initial conditions.
- If need to re-submit any parts of the simulation, from within the folder, make changes to the relevant bash script and then:  
`qsub pre.bash`  
`qsub main.bash`  
`qsub post.bash`  
- Approximate job run times and HPC requirements.  
    - 1 day simulation takes 1 hour wall clock time approximately.  
    - 1 month simulation takes 2 days wall clock time approximately.  
    - 1 year simulations takes 1 month wall clock time approximately.  
    - pre.bash = 7 hours, 1 core, 32GB/process (run in serial)
    - main.bash = 48 hours, 32 cores, 1GB/process (run in parallel)
    - post.bash = 48 hours, 4 core, 12GB/process (run in parallel)
___
### 7. Versions <a name="versions"/>
Setup configurations for key components of WRFotron releases.
#### [WRFotron0.0](https://github.com/lukeconibear/wrf-analysis/tree/master/WRFotron/WRFotron0.0)
- WRF-Chem version 3.7.1.  
- Single domain.  
- Continuous nudged meteorology each timestep (with target fields on a 3-hour update freq) with chemical restarts.  
- Initial and boundary conditions for meteorology from GFS.  
- Initial and boundary conditions for chemistry from MOZART.  
- MOZART-MOSAIC 4 bin, without aqueous chemistry and simple SOA (chem_opt = 201).  
- Horizontal spatial resolution of 30 km spatial resolution.  
- 33 vertical levels.  
- 27 meteoroglogical levels .  
- 180 second timestep for meteorology.  
- Thompson microphysics scheme (mp_physics = 8).  
- Radiation from RRTMG for both long and short-wave.  
- Boundary layer scheme from Mellor-Yamada Nakanishi and Niino-2.5.  
- Noah Land Surface Model.  
- Convective parameterisation from Grell 3-D ensemble.  
- Photolysis scheme from Madronich fTUV.  
- Emissions.  
    - Anthropogenic from EDGAR-HTAPv2.2.  
    - Fire from FINN.  
    - Biogenic from MEGAN.  
    - Dust from GOCART with AFWA.  
#### [WRFotron1.0](https://github.com/lukeconibear/wrf-analysis/tree/master/WRFotron/WRFotron1.0)
- Changes relative to version 0.0:  
    - MOZART-MOSAIC 4 bin, with aqueous chemistry and VBS SOA (chem_opt = 202).  
    - Without aqueous chemistry in stratocumulus clouds (cldchem_onoff = 0).  
    - Morrison microphysics (mp_physics= 10).  
    - Initial and boundary conditions for meteorology from ECMWF.  
    - 38 meteoroglogical levels.  
    - 3 meteorological soil levels for WRFChem4.0.3 and 4 for WRFChem3.7.1.  
    - Consistent timestep for chemistry and biogenics with meteorology.  
#### [WRFotron2.0](https://github.com/lukeconibear/wrf-analysis/tree/master/WRFotron/WRFotron2.0)
- Changes relative to version 1.0:
- WRF-Chem version 4.0.3.  
- With aqueous chemistry in stratocumulus clouds (cldchem_onoff = 1).  
- Biomass burning plume rise throughout the boundary layer (bbinjectscheme = 2).  
- The original option 2 was 50% at the surface and 50% evenly throughout the BL.  
- The new option 2 has all BB emissions evenly distributed throughout the BL.  
- Diurnal cycle from Olivier et al., (2003).  
- Aerosol optical properties approximated by Maxwell-Garnett.  
- Updated TUV scheme for photolysis (phot_opt = 4).  
- Initial and boundary conditions for chemistry from WACCM for post 2018 or CAM-Chem for pre 2018 (see [here](https://github.com/lukeconibear/wrf-analysis/blob/master/WRFotron/additional_docs/CESM-WRFchem_aerosols_plusgas.pdf)).  
- Fixed the bug where nudging would stop after 312 hours (i.e. after day 13 of a simulation) i.e. changed gfdda_end_h to 10,000.  
- Nudge above the boundary layer. To do this, go into namelist.wrf.blueprint, and within the FDDA section change:  
    - if_no_pbl_nudging_uv = 1.  
    - if_no_pbl_nudging_t = 1.  
    - if_no_pbl_nudging_q = 1.  
- Hard-coded NCL and NCO commands, removing profile.bash.  
- Fixed the bug where within the anthro_emiss namelist for EDGAR-HTAP2, NH3 was incorrectly set as an aerosol I.e. removed (a) in the emis_map.  
- Fixed the bug in plume rise where extra biomass burning mass was added aloft when the thickness of the vertical grid (dz) increases by altitude.  
    - Within chem/module_chem_plumerise_scalar.F:  
        - dz_flam=zzcon(k2)-zzcon(k1-1) ! original version.  
        - dz_flam=zzcon(k2+1)-zzcon(k1)   ! fixed version.  
- Corrected the metInc within config.bash for ECMWF to be 6 (3 was for GFS).  
- Added the faster version of post.bash from Helen Burns in CEMAC.  
    - Hard coded NCL and NCO commands in.  
    - Also, removed the deletion of pre-processed and temporary wrfout files from the staging directory, as these are often needed for error diagnosis.  
___
### 8. Miscellaneous <a name="misc"/>
#### a. Recommendations <a name="recom"/>
- Submit runs individually and quality control.  
- Check all steps in the process have run correctly.  
- Check main.bash.o has “substituting initial chemistry from restart” if do not want a cold start.  
- Manage space requirements, as run and output folders can get very large.  
- Make use of CPU affinity to have dedicated input/output processors, as these are not scalable in WRF-Chem:
    - Within namelist.wrf.blueprint:
        - &namelist_quilt
            - nio_tasks_per_group = 5
            - nio_tasks_per_group = 2
            - So the number of cores = nproc_x * nproc_y + nio_groups * nio_tasks_per_group
            - For example, 44 = 4 * 8 + 2 * 5
    - Currently unresolved issue with WRFChem4.0.3 being slow for input / output at the meteorological increment (i.e. every 6 hours for ECMWF). 

#### b. Output <a name="output"/>
- LC and BS have created a selection of data science scripts using Python available [here](https://github.com/wrfchem-leeds/python-scripts). 

#### c. Troubleshooting and errors <a name="errors"/>
- Find the errors' first occurance, checking rsl.error, rsl.out, .e, .o, and .log files within the run folder.  
- You need to make sure all programs are compiled and useable, and that the paths in your config.bash point to the correct locations.  
- You need to ensure that your data is all available for the period you want to simulate (including meteo spin-up).  
- You need to ensure your namelists are correct.  
- If the error if related to a FORTRAN run-time error, check this [website](https://software.intel.com/en-us/fortran-compiler-developer-guide-and-reference-list-of-run-time-error-messages).  
- Check WRF FAQ's [here](http://www2.mmm.ucar.edu/wrf/users/FAQ_files/).  
- Check WRF forums [here](http://forum.wrfforum.com/).  
- Check Google groups for:  
    - [WRF-Chem](https://groups.google.com/a/ucar.edu/forum/#!forum/wrf-chem).  
    - [fire_emiss](https://groups.google.com/a/ucar.edu/forum/#!forum/wrf-chem-fire_emiss).  
    - [anthro_emis](https://groups.google.com/a/ucar.edu/forum/#!forum/wrf-chem-anthro_emiss).  
    - [Runs](https://groups.google.com/a/ucar.edu/forum/#!forum/wrf-chem-run).  
- Try increasing the debug level.  
- Timesteps for meteorology (time_step in namelist.wrf), chemistry (chemdt in namelist.chem), and biogenics (bioemdt in namelist.chem) need to match (careful of units).  
- If no error message given at the bottom of rsl.error. file:  
    - Potentially a violation of the CFL criterion:  
        - Try reducing the timestep.  
        - Try turning w_damping off.  
    - Potentially a memory error:  
        - Increase the number of cores.  
        - Increase the memory per core.  
        
#### d. Download ECMWF meteorlogy files <a name="ecmwf"/>
- Create an account with ECMWF [here](https://apps.ecmwf.int/registration/).  
- Follow the steps [here](https://confluence.ecmwf.int/display/WEBAPI/Access+ECMWF+Public+Datasets).  
- Login.  
- Retrieve your key.  
- Copy the information to ~/.ecmwfapirc  
- Create a python2 environment for ecmwf-api-client (this library has not yet been updated for python 3).  
`conda create -n python2_ecwmf -c conda-forge ecmwf-api-client`
- Go to the folder initial_boundary_meteo_ecmwf
- Edit the python scripts
    - Both surface and pressurelevels
    - Only need to change the date and target name
- Qsub the .bash scripts
- Edit pre.bash to comment out the GFS and comment in the ECMWF files
- Ensure the date and target name correspond to those you want to run with
- Change the number of meteorological vertical levels from 27 (GFS) to 38 (ECMWF)
- Also, the number of meteorological soil levels from 4 (GFS):
    - To 3 for ECMWF with WRFChem4.0.3
    - To 4 for ECMWF with WRFChem3.7.3

#### e. To run with a nest <a name="nest"/>
- Offline nests
    - See step-by-step guide to run with a nest document from Carly Reddington [here](https://github.com/lukeconibear/wrf-analysis/blob/master/WRFotron/additional_docs/Guide_to_offline_nesting_CR.pdf).  
    - Uses ndown.exe for one-way nesting
    - Feedback=0
    - Parent and nest domain may drift apart
- Online nests
    - Turn off urban physics (i.e. sf_urban_physics = 0, 0, 0) in physics subsection of namelist.wrf.  
    - Requires a large amount of cores, as memory intensive
    - Uses wrf.exe for two-way nesting
    - Feedback=1
    - Have an odd number for the parent_grid_ratio.
    - For nest 2, (e_we-s_we+1) must be one greater than an integer multiple of the parent_grid_ratio (3 or 5).
    - WRF will decompose each domain in the exact same way, so ensure all the domains are similar shapes (i.e. don’t have a square domain within a rectangular domain, or even a rectangular domain which is longer in the x-direction within another domain which is longer in the y-direction).  
    - Check all namelist settings and check all required nest parameters are set (use registry to check which parameters need to be set for every domain).
    - All variables with dimension = max_domains or (max_dom) need to be set for the nests
    - Careful the domains are not too big, otherwise wrfinput won’t be created
    - Use same physics options and physics calling options e.g. radt/cudt
        - An exception is cumulus scheme. One may need to turn it off for a nest that has grid distance of a few kilometers or less.
    - For nest, e_we and e_sn for a parent_grid_ratio of 3 must be return a whole number when minus 1 and divide by parent_grid_ratio (3)
    - Decrease restart_interval to 720 (2/day) from 360 (4/day)
    - Tests with less than 24 hours break the coarsest domains mozbc
    - Add diurnal cycle for all domains
        - Within MAIN_emission_processing.ncl, change to all domains.
    - Timestep
        - Decrease propotionally
    - Radiation timestep should coincide with the finest domain resolution (1 minute per km dx), but it usually is not necessary to go below 5 minutes. All domains should use the same value, so that radiation forcing is applied at the same time for all domains.
    - Other namelist.wrf settings specific for domains < 3km res
        - &domains
            - smooth_option = 0
        - &physics
            - cugd_avedx = 3
            - smooth_option = 0
            - cu_rad_feedback = .false.
            - cu_diag = 0
            - slope_rad = 1
            - topo_shading = 1
        - &dynamics
            - non_hydrostatic = .false.

#### f. To run with cumulus parameterisation off <a name="cumpar"/>
- Namelist.chem
    - cldchem_onoff = 1
    - chem_conv_tr = 0 (subgrid convective transport)
    - conv_tr_wetscav = 0 (subgrid convective wet scavenging)
    - conv_tr_aqchem = 0 (subgrid convective aqueous chemistry)
- Namelist.wps
    - Resolution < 5 km
- Namelist.wrf
    - Resolution < 5 km
    - cu_physics = 0 (cumulus parameterization off)
    - cugd_avedx = 3 (number of grid boxes over which subsidence is spread)
- Master.bash, turn off nudging
    - s/GRIDFDDA/0/g

#### g. Changes for WRF-Chem version 4 <a name="wrfchem4"/>
- Select updates for WRFChem4.0.3
    - Bug fixes:
        - NOAH land surface scheme
        - Thompson microphysics scheme
        - Boundary layer and surface schemes from MYNN.
        - Chemical reaction rate constant for reaction: SO<sub>2</sub> + OH -> SO<sub>4</sub>
        - Dust < 0.46 microns contribution to AOD.
        - Dust and salt bin contributions to AOD.
        - Urban physics.
        - Fires (module_mosaic_addemiss.F).
        - glysoa not needed as no longer uses to_toa variable which has the summation error (module_mosaic_driver.F).
        - GEOGRID.TBL within WPS4.0.3/geogrid is a hard copy of the GEOGRID.TBL.ARW_CHEM including erod.
    - New defaults
        - Hybrid sigma-pressure vertical coordinate.
        - Temperature variable is now moist theta. 
        - Method to compute vertical levels, smooth variation of dz.
    - Various improved options available:
        - RRTMK (ra_sw_physics=14, ra_lw_physics=14) improves RRTMG
- Setting changes
    - namelist.wps.blueprint
        - Need to change geog_data_res from ‘modis_30s+30s ‘ to ‘default’
    - Namelist.wrf.blueprint
        - Num_metgrid_soil_layers from 4 to 3
        - Num_soil_layers from 4 to 3
        - Num_land_cat from 20 to 21
        - io_form_auxinput12 = ISRESTARTVALUE
    - master.bash
        - WPS and spin up
            - s/ISRESTARTVALUE/0/g
        - WRFChem
            - s/ISRESTARTVALUE/1/g
    - New static geography files in WPSGeog4

#### h. To run with a diurnal cycle <a name="diurnal"/>
- Choosing the diurnal cycle:
    - There are several different diurnal cycles in WRF_UoM_EMIT.
    - They are contained in the emission_script_data*.ncl files. Whichever of these files is named emission_script_data.ncl will be the diurnal cycle that is read by MAIN_emission_processing.ncl. The current emission_script_data.ncl is a copy of emission_script_data_EU.ncl.
        - EU = European diurnal cycles based on Olivier et al 2003
        - EX = Exaggerated diurnal cycle with 99% of emissions during daytime
        - QH = Qinghua diurnal cycle
    - Change settings in MAIN_emission_processing.ncl
        - time_offset
        - oc_om_scale
- To check if the diurnal cycle application was successful, run the following python script, which should be within WRF_UoM_EMIT, and is automatically linked to your run folder during pre.bash. Take a copy of the file from the following location if you don’t have it:  
`python plot_wrfchemi.py`

#### i. To run with NAEI emissions <a name="naei-emissions"/>
- Follow the guide created by Ailish Graham [here](https://github.com/lukeconibear/wrf-analysis/blob/master/WRFotron/additional_docs/Guide_to_NAEI_emissions_AG.pdf).  
