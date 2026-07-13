#!/bin/bash


for NODECOUNT in 1 2 4; 
do
    # Run the benchmark
    mpirun -N=$NODECOUNT sst --parallel-load=SINGLE merlin_benchmark.py -- --topology=mesh --tg-output-file-name="mesh_${NODECOUNT}nodes.out" --verbose=5

    # Grab the output lines to check
    rm -f mesh_${NODECOUNT}nodes.check
    touch mesh_${NODECOUNT}nodes.check

    # Only a suffix if NODECOUNT != 1
    if [ $NODECOUNT -eq 1 ]; then
        grep "CHECK" mesh_${NODECOUNT}nodes.out >> mesh_${NODECOUNT}nodes.check
    else
        for i in $(seq 0 $((NODECOUNT-1))); do
            grep "CHECK" mesh_${NODECOUNT}nodes.out$i >> mesh_${NODECOUNT}nodes.check
        done
    fi
    

    # Sort the checked lines
    sort mesh_${NODECOUNT}nodes.check -o mesh_${NODECOUNT}nodes.check
done

ALLMATCH=1
for NODECOUNT1 in 1 2 4; do
    for NODECOUNT2 in 1 2 4; do
        if [ $NODECOUNT1 -eq $NODECOUNT2 ]; then
            continue
        fi
        # Compare the outputs and print a message if they're different
        diff mesh_${NODECOUNT1}nodes.check mesh_${NODECOUNT2}nodes.check > mesh_${NODECOUNT1}nodes_vs_${NODECOUNT2}nodes.diff
        if [ $? -ne 0 ]; then
            echo "Output mismatch between ${NODECOUNT1} and ${NODECOUNT2} nodes."
            echo "See mesh_${NODECOUNT1}nodes_vs_${NODECOUNT2}nodes.diff for details."
            ALLMATCH=0
        fi
    done
done

if [ $ALLMATCH -eq 1 ]; then
    echo "All outputs match across node counts."
else
    echo "There were output mismatches across node counts."
fi