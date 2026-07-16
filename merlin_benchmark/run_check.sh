#!/bin/bash
# Arguments to this are passed to the benchmark script.

for NODECOUNT in 1 2 4; 
do
    # Run the benchmark
    echo mpirun -N=$NODECOUNT sst --parallel-load=SINGLE merlin_benchmark.py -- --tg-output-file-name="simulation_${NODECOUNT}nodes.out" --verbose=5 $@
    mpirun -N=$NODECOUNT sst --parallel-load=SINGLE merlin_benchmark.py -- --tg-output-file-name="simulation_${NODECOUNT}nodes.out" --verbose=5 $@

    if [ $? -ne 0 ]; then
        echo "Error: Benchmark failed for ${NODECOUNT} nodes."
        exit 1
    fi
    # Grab the output lines to check
    rm -f simulation_${NODECOUNT}nodes.check
    touch simulation_${NODECOUNT}nodes.check

    # Only a suffix if NODECOUNT != 1
    if [ $NODECOUNT -eq 1 ]; then
        grep "CHECK" simulation_${NODECOUNT}nodes.out >> simulation_${NODECOUNT}nodes.check
    else
        for i in $(seq 0 $((NODECOUNT-1))); do
            grep "CHECK" simulation_${NODECOUNT}nodes.out$i >> simulation_${NODECOUNT}nodes.check
        done
    fi
    

    # Sort the checked lines
    sort simulation_${NODECOUNT}nodes.check -o simulation_${NODECOUNT}nodes.check
done

ALLMATCH=1
for NODECOUNT1 in 1 2 4; do
    for NODECOUNT2 in 1 2 4; do
        if [ $NODECOUNT1 -eq $NODECOUNT2 ]; then
            continue
        fi
        # Compare the outputs and print a message if they're different
        diff simulation_${NODECOUNT1}nodes.check simulation_${NODECOUNT2}nodes.check > simulation_${NODECOUNT1}nodes_vs_${NODECOUNT2}nodes.diff
        if [ $? -ne 0 ]; then
            echo "Output mismatch between ${NODECOUNT1} and ${NODECOUNT2} nodes."
            echo "See simulation_${NODECOUNT1}nodes_vs_${NODECOUNT2}nodes.diff for details."
            ALLMATCH=0
        fi
    done
done

if [ $ALLMATCH -eq 1 ]; then
    echo "All outputs match across node counts."
else
    echo "There were output mismatches across node counts."
fi