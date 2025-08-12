#!/bin/bash
set -x
scriptDir="$(dirname "$(scontrol show job "$SLURM_JOB_ID" | awk -F= '/Command=/{print $2}')")"
echo "$scriptDir"

nodeCount=$1
ranksPerNode=$2
threadCount=$3
width=$4
height=$5
eventDensity=$6
ringSize=$7
timeToRun=$8
smallPayload=$9
largePayload=${10}
largeEventFraction=${11}
imbalanceFactor=${12}
componentSize=${13}
prefix=${14}

tmpFile=${prefix}.tmp
timeFile=${prefix}.time
outFile=${prefix}.err
outDir=${prefix}_dir


simFlags="--N $height --M $width --eventDensity $eventDensity --timeToRun ${timeToRun}ns --numRings $ringSize --smallPayload $smallPayload --largePayload $largePayload --largeEventFraction $largeEventFraction --imbalance-factor $imbalanceFactor --componentSize $componentSize"

sstFlags="--num-threads $threadCount --print-timing-info=true --parallel-load=SINGLE ${scriptDir}/phold_dist.py"

srunPortion="srun -N $nodeCount --cpus-per-task=$threadCount --ntasks-per-node=$ranksPerNode" 


mkdir $outDir
cd $outDir
rm $timeFile
touch $timeFile
$srunPortion sst $sstFlags -- $simFlags 1> $tmpFile 2> $outFile

grep "Build time:" $tmpFile | awk '{print $3}' > $timeFile
grep "Run stage Time:" $tmpFile | awk '{print $4}' >> $timeFile
grep "Max Resident Set Size:" $tmpFile | awk -F': *' '{print $2}' >> $timeFile
grep "Approx. Global Max RSS Size:" $tmpFile | awk -F': *' '{print $2}' >> $timeFile


cd -