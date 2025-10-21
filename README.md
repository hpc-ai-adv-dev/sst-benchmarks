# sst-benchmarks

This repository contains benchmarks and related scripts and tools for studying
SST-Cores performance and scalability.

Currently, it includes:

- Benchmarks
- [Containers](sst-containers/README.md)
- A memory model

### The benchmarks (found in their respective directories):
- [pingpong](pingpong/README.md) - simulates messages bouncing back-and-forth in one or two dimensions.
- gameoflife - an SST-based implementation of Conway's Game of Life.
- [phold](phold/README.md) - a benchmark widely used to assess the scalability and performance of parallel discrete event simulation (PDES) systems.

### Containers
the `sst-containers` directory contains a container file for running SST-core
on either a desktop or a Cray EX supercomputer. It also provides
[documentation](sst-containers/README.md) on how to build and deploy the
container.

### Memory Model
The `memoryModel` directory includes a Jupyter notebook with a script that can
be used to estimate SST core's memory usage and experiment with ideas on how to
reduce its memory footprint.
