# sst-benchmarks

This repository contains benchmarks and related scripts and tools for studying
SST-Cores performance and scalability.

Currently, it includes the following:

- Benchmarks
- [Containers](sst-containers/README.md)
- A memory model

The benchmarks (in their respective directories) include:
- [pingpong]() - simulates messages bouncing back-and-forth in a 1 or 2 dimensional space.
- [gameoflife] - an SST-based version of Conway's Game of Life.
- [phold](phold/README.md) - a benchmark used across several studies to evaluate the scalability and performance of parallel discrete event simulation (PDES) systems.

The `sst-containers` directory includes a containerfile for using SST-core on
either a desktop or Cray EX supercomputer. It also includes
[documentation](sst-containers/README.md) on on how to build and deploy this container.

The memory `modelModel` directory includes a Jupyter notebook with a script to estimate SST core's memory usage.
