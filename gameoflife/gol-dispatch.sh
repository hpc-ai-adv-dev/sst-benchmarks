#!/bin/bash
set -x
scriptDir="$(dirname "$(scontrol show job "$SLURM_JOB_ID" | awk -F= '/Command=/{print $2}')")"
echo "$scriptDir"

script=$1
nodeCount=$2
ranksPerNode=$3
threadCount=$4
width=$5
height=$6
timeToRun=$7
simFlags=$8
prefix=$9


tmpFile=${prefix}.tmp
timeFile=${prefix}.time
outFile=${prefix}.err
outDir=${prefix}_dir


simFlags="$simFlags --N $width --M $height --stop-at $timeToRun"


sstFlags="--num-threads $threadCount --print-timing-info=true --parallel-load=SINGLE  ${scriptDir}/${script}"


srunFlags="-N $nodeCount --cpus-per-task=$threadCount --ntasks-per-node=$ranksPerNode" 

mkdir $outDir
cd $outDir
rm $timeFile
touch $timeFile
srun $srunFlags sst $sstFlags -- $simFlags 1> $tmpFile 2> $outFile


grep "Build time:" $tmpFile | awk '{print $3}' > $timeFile
grep "Run stage Time:" $tmpFile | awk '{print $4}' >> $timeFile
grep "Max Resident Set Size:" $tmpFile | awk -F': *' '{print $2}' >> $timeFile
grep "Approx. Global Max RSS Size:" $tmpFile | awk -F': *' '{print $2}' >> $timeFile

cd -