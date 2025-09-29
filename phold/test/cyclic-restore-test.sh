
#!/bin/bash
sst --checkpoint-sim-period=8ns phold_dist.py -- --N 10 --M 10 --timeToRun 10ns --numRings 1 --movementFunction "cyclic" --verbose 1 --eventDensity -1
sst --load-checkpoint checkpoint/checkpoint_0_8000/checkpoint_0_8000.sstcpt