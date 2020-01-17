#!/bin/bash
# ------------------------------------------------------------------------------
# WRFOTRON v 1.0
# Christoph Knote (LMU Munich)
# 02/2016
# christoph.knote@lmu.de
# ------------------------------------------------------------------------------
#
## LSF batch script to run an MPI application
#BSUB -P P19010000                  # project core
#BSUB -W 0:30                       # wall clock time
#BSUB -n __nprocPre__               # number of MPI processors
#BSUB -J __PREJOBNAME__             # job name
#BSUB -o __PREJOBNAME__.%J.out      # output filename
#BSUB -e __PREJOBNAME__.%J.err      # error filename
#BSUB -q geyser                     # queue

#$ -cwd -V                          # execute from current working directory and export all current environment variables to all spawned processes
#$ -l h_rt=01:00:00                 # wall clock time
#$ -pe ib __nprocPre__              # use MPI - number of cores (x4 per processor)
#$ -l h_vmem=12G                    # memory per processor

# we assume we are called from master.bash, and hence know all variables
# e.g. startYear, startMonth, startDay...

. config.bash

# -----------------------------------------------------------------------------
# 1) WPS
# -----------------------------------------------------------------------------

msg "copying/linking files"

for aFile in util geogrid geogrid.exe ungrib ungrib.exe link_grib.csh metgrid metgrid.exe
do
  cp -fr ${WPSdir}/$aFile .
done

# -----------------------------------------------------------------------------
# 1a) ungrib - for GFS meteo
# -----------------------------------------------------------------------------
# fix for new GFS Vtable. Script will break if simulating through this date
# (do either before or after simulations)
if [ "__startYear____startMonth____startDay____startHour__" -ge "2015011412" ]
then
  ln -s ${chainDir}/Vtable.GFS_new Vtable
else
  ln -s ungrib/Variable_Tables/Vtable.GFS Vtable
fi

# list of met files to link
fileList=( ${metDir}/GF__startYear____startMonth____startDay____startHour__ )
let totTime="__fcstTime__+__spinupTime__+metInc"
for hour in $(seq -w ${metInc} ${metInc} ${totTime})
do
  curYear=$(date -u --date="__startYear__-__startMonth__-__startDay__ __startHour__:00:00 ${hour} hours" "+%Y")
  curMonth=$(date -u --date="__startYear__-__startMonth__-__startDay__ __startHour__:00:00 ${hour} hours" "+%m")
  curDay=$(date -u --date="__startYear__-__startMonth__-__startDay__ __startHour__:00:00 ${hour} hours" "+%d")
  curHour=$(date -u --date="__startYear__-__startMonth__-__startDay__ __startHour__:00:00 ${hour} hours" "+%H")
  fileList=( ${fileList[@]} ${metDir}/GF${curYear}${curMonth}${curDay}${curHour} )
done

/bin/csh ./link_grib.csh ${fileList[@]}

# -----------------------------------------------------------------------------
# 1b) ungrib - for ECMWF meteo
# -----------------------------------------------------------------------------
# link the Vtable
#ln -s ${chainDir}/Vtable.ECMWF Vtable
# link the ECMWF files to be ungribbed - both the surface and pressure levels for the date required (change)
#/bin/csh ./link_grib.csh ${metDir}/ecmwf_global_pressurelevels_20160901_20170101.grib ${metDir}/ecmwf_global_surface_20160901_20170101.grib

cp namelist.wps.prep namelist.wps

msg "ungrib"
./ungrib.exe > ungrib.log

rm GRIBFILE*

msg "geogrid"
${mpiCommandPre} ./geogrid.exe

msg "metgrid"
${mpiCommandPre} ./metgrid.exe

rm FILE*

# -----------------------------------------------------------------------------
# 2) first real w/o chemistry
# -----------------------------------------------------------------------------

cp -r ${WRFdir}/run/* .
rm *.exe
cp -r ${WRFdir}/main/*.exe .
cp -r ${WRFmeteodir}/main/wrf.exe wrfmeteo.exe

rm namelist.input
cp namelist.wrf.prep.real_metonly namelist.input

msg "first real"
${mpiCommandPre} ./real.exe

mkdir first_real_out
mv rsl* first_real_out

# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
# stuff that follows is for runs with chemistry only...
if $withChemistry
then

# -----------------------------------------------------------------------------
# 3) MEGAN, Wesely, Exo_coldens
# -----------------------------------------------------------------------------

msg "MEGAN"

# MEGAN takes a long time, but does not really depend on the time of simulation.
# Hence we create one file for the whole year (that is - LAI for all months)
# and only replace start date etc ...

# assume if one is missing, all are missing!
if [ ! -f ${workDir}/wrfbiochemi_d01_${projectTag} ]
then
  echo "MEGAN input files do not not exist - recreating from scratch. Grab a coffee..."
  ln -s ${WRFMEGANdir}/megan_bio_emiss .
  ./megan_bio_emiss < megan_bio_emiss.inp > megan_bio_emiss.out
  for domain in $(seq -f "0%g" 1 ${max_dom})
  do
    meganDataFile=${workDir}/wrfbiochemi_d${domain}_${projectTag}
    mv wrfbiochemi_d${domain} ${meganDataFile}
  done
fi

julday=$(date -u --date="__inpDateTxt__" '+%-j')
for domain in $(seq -f "0%g" 1 ${max_dom})
do
  meganDataFile=${workDir}/wrfbiochemi_d${domain}_${projectTag}
  $ncattedBin -a START_DATE,global,o,c,"__inpDate__" \
          -a SIMULATION_START_DATE,global,o,c,"__inpDate__" \
          -a JULYR,global,o,i,__inpYear__ \
          -a JULDAY,global,o,i,${julday} \
          ${meganDataFile} wrfbiochemi_d${domain}
  $ncksBin -A -v Times wrfinput_d${domain} wrfbiochemi_d${domain}
done

msg "wesely"
ln -s ${WRFmztoolsdir}/* .
./wesely < wesely.inp > wesely.out
msg "exo_coldens"
./exo_coldens < exo_coldens.inp > exo_coldens.out

# -----------------------------------------------------------------------------
# 4) emissions
# -----------------------------------------------------------------------------

msg "emissions"

ln -s ${WRFanthrodir}/anthro_emis .
./anthro_emis < anthro_emis.inp > anthro_emis.out

# -----------------------------------------------------------------------------
# 4.b) Fire FINN emissions
# -----------------------------------------------------------------------------

msg "Fire FINN emissions"

ln -s ${WRFfiredir}/fire_emis .
./fire_emis < fire_emis.inp > fire_emis.out

# -----------------------------------------------------------------------------

rm namelist.input
cp namelist.wrf.prep.real namelist.input

msg "second real"
${mpiCommandPre} ./real.exe

mkdir second_real_out
mv rsl* second_real_out

# -----------------------------------------------------------------------------
# 5) MOZART/WACCM IC/BC
# -----------------------------------------------------------------------------

msg "MOZART/WACCM"

ln -s $WRFMOZARTdir/mozbc .

# If daily MOZBC files use this portion (otherwise comment out)
#let totDays="((__spinupTime__+__fcstTime__)/24)+2"
#i=0
#for day in $(seq -w -2 $totDays)
#do
#  # date format stupidity
#  txty="${day} days"
#  if [ $day -lt 0 ]
#  then
#    txty="${day/-/} days ago"
#  fi
#
#  curDate=$(date -u --date="__inpYear__-__inpMonth__-__inpDay__ __inpHour__:00:00 ${txty}" "+%Y%m%d")
#
#  ln -s ${MOZARTdir}/MZ${curDate} ./moz$(printf "%04d" $i).nc
#  let i=i+1
#done

# If monthly files use this portion (otherwise comment out)
# MOZART - pre 2018
ln -s /nobackup/user/wrf3.7.1_data/initial_boundary_chem/MZ2014jan ./moz0000.nc
#ln -s /nobackup/user/wrf3.7.1_data/initial_boundary_chem/MZ2014feb ./moz0001.nc
#ln -s /nobackup/user/wrf3.7.1_data/initial_boundary_chem/MZ2014mar ./moz0002.nc
# WACCM - post 2018
#ln -s /nobackup/user/wrf3.7.1_data/initial_boundary_chem/WACCM2018jan ./moz0000.nc
#ln -s /nobackup/user/wrf3.7.1_data/initial_boundary_chem/WACCM2018feb ./moz0001.nc
#ln -s /nobackup/user/wrf3.7.1_data/initial_boundary_chem/WACCM2018mar ./moz0002.nc

# first domain, always
./mozbc < mozbc_outer.inp > mozbc_bc.log

for domain in $(seq 2 ${max_dom})
do
  /bin/sed -s "s/__domain__/${domain}/" < mozbc_inner.inp > mozbc_inner_d${domain}.inp
  ./mozbc < mozbc_inner_d${domain}.inp > mozbc_inner_d${domain}.log
done

fi
# that stuff was for runs with chemistry only...
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

# -----------------------------------------------------------------------------
# 6) Bring over last restart file / main_restart
# -----------------------------------------------------------------------------

msg "bring over restart file from previous run"

for domain in $(seq -f "0%g" 1 ${max_dom})
do
  newRunRstFile=wrfrst_d${domain}___inpYear__-__inpMonth__-__inpDay_____inpHour__:00:00
  cp ${restartDir}/${newRunRstFile} ${newRunRstFile}
done

fi

# -----------------------------------------------------------------------------

msg "bring over main_restart"

cp ${chainDir}/main_restart.bash .

# ------------------------------------------------------------------------------

rm met_em*

msg "finished preprocessing"




