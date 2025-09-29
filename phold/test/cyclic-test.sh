#!/bin/bash
make
sst phold_dist.py -- --N 10 --M 10 --timeToRun 10ns --numRings 1 --movementFunction "cyclic" --verbose 1 --eventDensity -1