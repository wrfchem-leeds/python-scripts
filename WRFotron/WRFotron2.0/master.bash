#!/bin/bash
# ------------------------------------------------------------------------------
# WRFOTRON
# ------------------------------------------------------------------------------
#
# Main script to execute chained WRF/chem simulations
# with meteo spinup and carried-on meteorology from
# previous runs.
#
# each run works like that:
#     |   spinup period    |     run period      |
#     | ------------------ | ------------------- |
# startDate             inpDate               endDate
#
# * WPS and real.exe from startDate to endDate
#
# * WRF only simulation to spin-up meteorology from
#    startDate to inpDate
#    --> creates restart file at inpDate
#
# * fill chemistry fields of restart file at
#    inpDate with data from previous run (if available)
#
# * WRF-Chem (restart) simulation from inpDate to endDate
#    --> creates (output, obviously, but also) restart file at endDate
#
# * in case of met-only simulations, there's only one (nudged) run
#   from startDate to endDate

# -----------------------------------------------------------------------------
# 1) input of parameters
# -----------------------------------------------------------------------------

OPTIND=1

experiment="base"
chainDir="."
while getopts ":e:c:" opt
do
  case $opt in
    e) experiment=${OPTARG} ;;
    c) chainDir=${OPTARG} ;;
    esac
done

shift $(($OPTIND - 1))

if [[ $# -lt 6 || $# -gt 7 ]]
then
  echo "Call with arguments <year (YYYY)> <month (MM)> <day (DD)> <hour (hh)> <forecast time (h)> <spinup time (h)>"
  echo "                 or <year (YYYY)> <month (MM)> <day (DD)> <hour (hh)> <forecast time (h)> <spinup time (h)> <PID of job dependency>"
  echo "possible options (have to go before arguments): "
  echo "                  -e <experiment name> "
  echo "                  -c <chain directory (submission from CRON)>"
    return 1
fi

inpYear=$1
inpMonth=$2
inpDay=$3
inpHour=$4

fcstTime=$5
spinupTime=$6

isDependent=false
if [ $# -eq 7 ]
then
  isDependent=true
  depjobnr=$7
fi

# load configuration file
# note - in case of submission by CRON, you need to tell it the chainDir!
. ${chainDir}/config.bash

# check passed arguments
let dtTest="inpHour % metInc"
if [ $dtTest -ne 0 ]
then
  echo "Hour needs to be multiple of $metInc."
  return 1
fi
let dtTest="fcstTime % metInc"
if [ $dtTest -ne 0 ]
then
  echo "forecast time needs to be multiple of $metInc."
  return 1
fi
let dtTest="spinupTime % metInc"
if [ $dtTest -ne 0 ]
then
  echo "spinup time needs to be multiple of $metInc."
  return 1
fi

# -----------------------------------------------------------------------------
# 2) calculation of date variables
# -----------------------------------------------------------------------------

dateTxt="$inpYear-$inpMonth-$inpDay $inpHour:00:00"

startYear=$(date -u --date="${dateTxt} ${spinupTime}hours ago" '+%Y')
startMonth=$(date -u --date="${dateTxt} ${spinupTime}hours ago" "+%m")
startDay=$(date -u --date="${dateTxt} ${spinupTime}hours ago" "+%d")
startHour=$(date -u --date="${dateTxt} ${spinupTime}hours ago" "+%H")

endYear=$(date -u --date="${dateTxt} ${fcstTime}hours" "+%Y")
endMonth=$(date -u --date="${dateTxt} ${fcstTime}hours" "+%m")
endDay=$(date -u --date="${dateTxt} ${fcstTime}hours" "+%d")
endHour=$(date -u --date="${dateTxt} ${fcstTime}hours" "+%H")

# wrfout-file-style dates
startDate="${startYear}-${startMonth}-${startDay}_${startHour}:00:00"
inpDate="${inpYear}-${inpMonth}-${inpDay}_${inpHour}:00:00"
endDate="${endYear}-${endMonth}-${endDay}_${endHour}:00:00"

# metInc in seconds
let metIncSec='metInc*3600'

# difference in years for emission offset
emissYearOffset=0
let "emissYearOffset = startYear - emissYear"

archiveDir=${archiveRootDir}/${experiment}
restartDir=${restartRootDir}/${experiment}

stagingDir=${workDir}/${experiment}/staging
runDir=${workDir}/${experiment}/${startDate}-${endDate}

if [ "$experiment" != "base" ]
then
  WRFdir=${WRFdir}_${experiment}
fi

prejobname=${projectTag}${inpYear}${inpMonth}${inpDay}${experiment}.pre
mainjobname=${projectTag}${inpYear}${inpMonth}${inpDay}${experiment}.main
postjobname=${projectTag}${inpYear}${inpMonth}${inpDay}${experiment}.post

startoutDir=$(pwd)

mkdir -p ${stagingDir} ${archiveDir} ${restartDir} ${workDir}

rm -rf $runDir
mkdir -p $runDir

# -----------------------------------------------------------------------------
# 3) determine number of domains
# -----------------------------------------------------------------------------

# get the max_dom line from the namelist.wps file
max_dom=$(grep max_dom ${chainDir}/namelist.wps.blueprint)
# cut out the (only) number
max_dom=$(expr "$max_dom"  : '.*\([0-9]\).*')

# -----------------------------------------------------------------------------
# 4) configuration printout
# -----------------------------------------------------------------------------

cat > ${runDir}/run.config << EOF

************************************************************
WRF/chem auto-queue $version
at $chainDir
************************************************************

source code / binaries
------------------------------------------------------------
WPSdir          $WPSdir
WRFdir          $WRFdir
WRFMEGANdir     $WRFMEGANdir
WRFMOZARTdir    $WRFMOZARTdir
WRFmztoolsdir   $WRFmztoolsdir

data
------------------------------------------------------------
metDir          $metDir (metInc=${metInc}h)
geogDir         $geogDir
MEGANdir        $MEGANdir
MOZARTdir       $MOZARTdir
emissDir        $emissDir
fireDir         $fireDir
SSTdir          $NAVYSSTdir

workspace
------------------------------------------------------------
workDir         $workDir
restartRootDir  $restartRootDir
archiveRootDir  $archiveRootDir

run settings
------------------------------------------------------------
meteo spinup    ${startDate} (spinupTime: -${spinupTime}h)
do chemistry?   ${withChemistry}
chem start      ${inpDate}
run end         ${endDate} (fcstTime: ${fcstTime}h)

project         ${projectTag}
experiment      ${experiment}

run directory   ${runDir}
staging dir     ${stagingDir}
archive dir     ${archiveDir}
restart dir     ${restartDir}

num. domains    ${max_dom}

execution settings
------------------------------------------------------------

jobnames        preprocessing:  ${prejobname}
                WRF:            ${mainjobname}
                postprocessing: ${postjobname}

cores used      preprocessing:  ${nprocPre}
                WRF:            ${nprocMain}
                postprocessing: ${nprocPost}

use queue       $usequeue
queueing call   $submitCommand

MPI calls       preprocessing:  ${mpiCommandPre}
                WRF:            ${mpiCommandMain}

dependency?     ${isDependent}
                on job nr. ${depjobnr}
------------------------------------------------------------
------------------------------------------------------------

EOF

# -----------------------------------------------------------------------------
# 3) preparation of run directory
# -----------------------------------------------------------------------------

cd $runDir

# setup sed scripts to replace in namelist blueprints

# variables that are used in various scripts
cat > sedMiscScript << EOF
s/__fcstTime__/${fcstTime}/g
s/__spinupTime__/${spinupTime}/g
s/__geogDir__/${geogDir//\//\\/}/g
s/__emissDir__/${emissDir//\//\\/}/g
s/__fireDir__/${fireDir//\//\\/}/g
s/__MEGANdir__/${MEGANdir//\//\\/}/g
s/__PREJOBNAME__/${prejobname}/g
s/__MAINJOBNAME__/${mainjobname}/g
s/__POSTJOBNAME__/${postjobname}/g
s/__inpYear__/${inpYear}/g
s/__inpMonth__/${inpMonth}/g
s/__inpDay__/${inpDay}/g
s/__inpHour__/${inpHour}/g
s/__inpDate__/${inpDate}/g
s/__inpDateTxt__/${dateTxt}/g
s/__nprocPre__/${nprocPre}/g
s/__nprocMain__/${nprocMain}/g
s/__nprocPost__/${nprocPost}/g
s/__domains__/${max_dom}/g
s/__REMOVERUNDIR__/${removeRunDir}/g
s/__CONFIGDIR__//g
s/__metIncSec__/${metIncSec}/g
s/__emissYearOffset__/${emissYearOffset}/g
EOF

# WPS and real run from -spinup to +fcstTime
cat > sedWPSScript << EOF
s/__startYear__/${startYear}/g
s/__startMonth__/${startMonth}/g
s/__startDay__/${startDay}/g
s/__startHour__/${startHour}/g
s/__startDate__/${startDate}/g
s/__endYear__/${endYear}/g
s/__endMonth__/${endMonth}/g
s/__endDay__/${endDay}/g
s/__endHour__/${endHour}/g
s/__endDate__/${endDate}/g
s/__ISRESTART__/.false./g
s/__ISRESTARTVALUE__/0/g
s/__GRIDFDDA__/1/g
s/__REMOVERUNDIR__/${removeRunDir}/g
EOF

# spinup only runs from -spinup to 0
cat > sedSpinupScript << EOF
s/__startYear__/${startYear}/g
s/__startMonth__/${startMonth}/g
s/__startDay__/${startDay}/g
s/__startHour__/${startHour}/g
s/__startDate__/${startDate}/g
s/__endYear__/${inpYear}/g
s/__endMonth__/${inpMonth}/g
s/__endDay__/${inpDay}/g
s/__endHour__/${inpHour}/g
s/__endDate__/${inpDate}/g
s/__ISRESTART__/.false./g
s/__ISRESTARTVALUE__/0/g
s/__GRIDFDDA__/1/g
EOF

# Chemistry as well as met-only runs start at 0 until +fcstTime
cat > sedChemScript << EOF
s/__startYear__/${inpYear}/g
s/__startMonth__/${inpMonth}/g
s/__startDay__/${inpDay}/g
s/__startHour__/${inpHour}/g
s/__startDate__/${inpDate}/g
s/__endYear__/${endYear}/g
s/__endMonth__/${endMonth}/g
s/__endDay__/${endDay}/g
s/__endHour__/${endHour}/g
s/__endDate__/${endDate}/g
s/__ISRESTART__/.true./g
s/__ISRESTARTVALUE__/1/g
s/__GRIDFDDA__/1/g
EOF

# Meteo-only runs are nudged start fresh at 0 until +fcstTime
cp sedWPSScript sedMetScript

cat >> sedWPSScript         < sedMiscScript
cat >> sedSpinupScript      < sedMiscScript
cat >> sedChemScript        < sedMiscScript
cat >> sedMetScript         < sedMiscScript

# replace placeholders in respective scripts,
# and copy them to the run directory

/bin/sed -f sedWPSScript    < ${chainDir}/namelist.wps.blueprint > namelist.wps.prep

/bin/sed -f sedWPSScript    < ${chainDir}/namelist.wrf.blueprint > namelist.wrf.prep.real
/bin/sed -f sedSpinupScript < ${chainDir}/namelist.wrf.blueprint > namelist.wrf.prep.spinup
/bin/sed -f sedMetScript    < ${chainDir}/namelist.wrf.blueprint > namelist.wrf.prep.met
/bin/sed -f sedChemScript   < ${chainDir}/namelist.wrf.blueprint > namelist.wrf.prep.chem
/bin/sed -f sedWPSScript    < ${chainDir}/namelist.wrf.blueprint > namelist.wrf.prep.chem_cold

/bin/sed -f sedWPSScript    < ${chainDir}/pre.bash               > pre.bash
/bin/sed -f sedWPSScript    < ${chainDir}/main.bash              > main.bash
/bin/sed -f sedMiscScript   < ${chainDir}/post.bash              > post.bash

/bin/sed -f sedMiscScript   < ${chainDir}/megan_bio_emiss.inp    > megan_bio_emiss.inp
/bin/sed -f sedWPSScript    < ${chainDir}/${emissInpFile}        > anthro_emis.inp
/bin/sed -f sedWPSScript    < ${chainDir}/${fireInpFile}         > fire_emis.inp

# patch chem namelist for aux input files

cp namelist.wrf.prep.real namelist.wrf.prep.real_metonly

cat < ${chainDir}/namelist.chem.blueprint >> namelist.wrf.prep.real
cat < ${chainDir}/namelist.chem.blueprint >> namelist.wrf.prep.chem
cat < ${chainDir}/namelist.chem.blueprint >> namelist.wrf.prep.chem_cold

# meh - auxinput_interval_d might need max_domains values!
cat > patchy << PATCH_END
 io_form_auxinput5                   = 2,
 ! io_form_auxinput5                   = 2,
 ! auxinput5_interval_m                = 60,
 ! frames_per_auxinput5                = 1,
 ! auxinput5_inname                    = 'wrfchemi_d<domain>_<date>'
 io_form_auxinput6                   = 2,
 auxinput6_inname                    = 'wrfbiochemi_d<domain>'
 auxinput6_interval_d                = 600,
PATCH_END

sed -e "/! CHEM/r patchy" namelist.wrf.prep.real      > tmp; mv tmp namelist.wrf.prep.real
sed -e "/! CHEM/r patchy" namelist.wrf.prep.chem      > tmp; mv tmp namelist.wrf.prep.chem
sed -e "/! CHEM/r patchy" namelist.wrf.prep.chem_cold > tmp; mv tmp namelist.wrf.prep.chem_cold
rm patchy

# copy ancillary namelists

/bin/sed -e "s/__domains__/${max_dom}/g" < ${chainDir}/wesely.inp      > ./wesely.inp
/bin/sed -e "s/__domains__/${max_dom}/g" < ${chainDir}/exo_coldens.inp > ./exo_coldens.inp

# several runs of mozbc - IC (all (sub-)domains) and BC (only the first)
cat > sedMozOuterScript << EOF
s/__do_ic__/.true./g
s/__do_bc__/.true./g
s/__domain__/1/g
EOF

cat > sedMozInnerScript << EOF
s/__do_ic__/.true./g
s/__do_bc__/.false./g
EOF

/bin/sed -f sedMozOuterScript < ${chainDir}/mozbc.inp > ./mozbc_outer.inp
/bin/sed -f sedMozInnerScript < ${chainDir}/mozbc.inp > ./mozbc_inner.inp

if $withChemistry
then
  cp ${chainDir}/iofields.chem iofields
else
  cp ${chainDir}/iofields.met iofields
fi

# copy and augment config file
cp ${chainDir}/config.bash .

cat >> config.bash << EOF

# run-dependent variables:

runDir=${runDir}
archiveDir=${archiveDir}
stagingDir=${stagingDir}
restartDir=${restartDir}

experiment=${experiment}

startDate=${startDate}
inpDate=${inpDate}
endDate=${endDate}

prejobname=${prejobname}
mainjobname=${mainjobname}
postjobname=${postjobname}

WRFdir=${WRFdir}

max_dom=${max_dom}

EOF

# -----------------------------------------------------------------------------
# 4) run submission
# -----------------------------------------------------------------------------

if $usequeue
then
  if $isDependent
  then
    pretxt=$(${submitCommand} -hold_jid ${depjobnr} pre.bash)
  else
    pretxt=$(${submitCommand} pre.bash)
  fi
  prejobnr=$(echo $pretxt | grep -o "[0-9]\{1,10\}" )

  maintxt=$(${submitCommand} -hold_jid ${prejobnr} main.bash)
  mainjobnr=$(echo $maintxt | grep -o "[0-9]\{1,10\}" )

  posttxt=$(${submitCommand} -hold_jid ${mainjobnr} post.bash)
  postjobnr=$(echo $posttxt | grep -o "[0-9]\{1,10\}" )

  echo "WRF/chem main job has been submitted as <$mainjobnr>"
else
  ${submitCommand} pre.bash
  ${submitCommand} main.bash
  ${submitCommand} post.bash
fi

# -----------------------------------------------------------------------------
# 5) cleanup
# -----------------------------------------------------------------------------

cd ${startoutDir}

#exit 0



