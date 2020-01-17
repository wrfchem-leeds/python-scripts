#!/bin/bash
# ------------------------------------------------------------------------------
# WRFOTRON v 1.0
# Christoph Knote (LMU Munich)
# 02/2016
# christoph.knote@lmu.de
# ------------------------------------------------------------------------------
#
## LSF batch script to run an MPI application
#BSUB -P xxx                  # project code
#BSUB -W 12:00                      # wall clock time 
#BSUB -n __nprocMain__              # number of processors (can have min,max)
#BSUB -R "span[ptile=16]"           # number of cores (i.e. 16 x 4 = 64 cores per processor)
#BSUB -J __MAINJOBNAME__            # job name
#BSUB -o __MAINJOBNAME__.%J.out     # output filename
#BSUB -e __MAINJOBNAME__.%J.err     # error filename
#BSUB -q regular                    # queue

#$ -cwd -V                          # execute from current working directory and export all current environment variables to all spawned processes
#$ -l h_rt=20:00:00                 # wall clock time
#$ -pe ib 32             # use MPI - number of cores

. config.bash

# fix hyper-threading issue with Yellowstone after upgrade
unset MP_PE_AFFINITY
export MP_TASK_AFFINITY=cpu

# -----------------------------------------------------------------------------
# 2) Chemistry simulation
# -----------------------------------------------------------------------------

# update restart files with previous results for chemistry, or do cold start

# restart check logic assumes that once we have restart file for domain 1
# we continue, even though further domains might be missing a restart file.
# Logic does not account for the case that restart file for domain 1 is missing,
# but is available for another domain (--> would attempt restart run...)
restartFound=false

for domain in $(seq -f "0%g" 1 ${max_dom})
do

newRunRstFile=wrfrst_d${domain}_YYYY-MM-DD_HH:00:00
prevRunRstFile=${restartDir}/${newRunRstFile}

if [ -f ${prevRunRstFile} ]
then

msg "substituting initial data with ${prevRunRstFile}"

# listing variables in old (chemistry) and new (met-only) restart files
$ncksBin -m ${prevRunRstFile} | grep -E ': type' | cut -f 1 -d ' ' | sed 's/://' | sort > chemVarList
$ncksBin -m ${newRunRstFile} | grep -E ': type' | cut -f 1 -d ' ' | sed 's/://' | sort  > metVarList

# determining arrays only in old (chemistry) restart file
chemVarsArr=( $(awk 'FNR==NR{a[$0]++;next}!a[$0]' metVarList chemVarList) )
# converting to comma-separated string
chemVarsLst=${chemVarsArr[@]}
chemVarsTxt=${chemVarsLst// /,}

# adding chemistry variables to new restart file
$ncksBin -A -v ${chemVarsTxt} ${prevRunRstFile} ${newRunRstFile}

restartFound=true

fi

done

msg "chem"

# do the chem run
${mpiCommandMain} ./wrf.exe

mkdir chem_out
mv rsl* chem_out

