This directory contains code for a PHOLD benchmark implemented using SST. 
The PHOLD benchmark is based on Fujimoto's 1990 paper [Performance of Time Warp Under Synthetic Workloads](https://gdo149.llnl.gov/attachments/20776356/24674621.pdf).
PHOLD is a synthetic benchmark developed to surface important simulation characteristics as parameters. 
This makes it useful for studying the behavior of PDES (parallel discrete event simulation) simulators like SST.
Some of the characteristic parameters in this implementation are:
- 2D grid size
- component connectivity (1 hop neighbors, 2 hop neighbors, etc)
- distribution of the data sizes of components and events
- number of events
- link delays

## Prerequisites

It is assumed you have installed [SST version 15.1.0](https://sst-simulator.org/SSTPages/SSTMainDownloads/). 
You can check which version of `sst` you have installed with the following command: `sst --version`.
You can also use containers to run this benchmark. See the [sst-containers](../sst-containers) directory for more information.


**When you build SST 15.1.0, you need to pass `--enable-perf-tracking` to the `./configure` script. This provides information used to determine how much time is spent synchronizing.**

## Workflow Overview

The general PHOLD workflow has 4 pieces:
- The `Node.cpp` and `Node.h` component definitions. These files define the component used in the PHOLD simulation.
- The `phold_dist.py` simulation description. This is the input that SST expects for the simulation.
- The `submit.py` and `dispatch.sh` scripts. These allow for the submission of multiple different PHOLD simulations as SLURM jobs, for example running a strong scaling evaluation.
- The `consolidate.py` script. This consolidates the outputs of the various jobs run by the `submit.py` and `dispatch.sh` scripts into a single `.csv` file for analysis.

Before detailing the various ways these scripts can be used, we review a simple strong scaling workflow.

First, we need to build the PHOLD library so that SST can use them in a simulation:
```
make
```
This will produce a file, `libphold.so` for use in the simulation.

Next, on a SLURM system, we will submit the jobs for the strong scaling evaluation, using 1, 2, 4, and 8 nodes on a 1000x1000 grid of components.
Each component will be connected to 2 rings of neighbors (25 connections total), and there will be 2 events moving around the simulation per component.
We will run the simulation for 100ns, as this simulation comfortably completes within 10 minutes, even on a single node. 
The name of this experiment is StrongScalingDemo.
```
python3 submit.py --name StrongScalingDemo --node-counts "1 2 4 8" --width 1000 --height 1000 --ring-size 2 --event-density 2 --time-to-run 100
```

As the 4 jobs proceed, they will each produce one `.out` file and one directory.
For example, the 8 node job will create the file `StrongScalingDemo_8_1_1_1000_1000_2.0_2_100_8_1024_0.0_0.0_0.out` and the directory `StrongScalingDemo_8_1_1_1000_1000_2.0_2_100_8_1024_0.0_0.0_0_dir`.
The directory contains the output for the SLURM job in the `.err` file, the simulation output in the `.tmp`, the extracted metrics about the simulation in `.time`, and the by-rank-and-thread synchronization metrics in the `rank_*_thread_*` files. 

Finally, we'll extract the data we want to collect about this simulation into a `.csv` with the `consolidate.py` script.
```
python3 consolidate.py StrongScalingDemo.csv StrongScalingDemo
```
This will produce the `StrongScalingDemo.csv` and `StrongScalingDemo-failures.csv` files which respectively contain the successful and failed runs with names starting with "StrongScalingDemo".
It is unlikely that this run will produce failures, but in the case of timeouts, OOM errors, or other failures, they will be populated there.

## `phold_dist.py`

`phold_dist.py` is the SST simulation description file for the PHOLD simulation.
The PHOLD simulation is a 2D grid of components, where each component is connected to some number of its neighbors in a regular topology.
Each component processes messages in the same way: it receives the message, and sends out a new message.
On the main branch, there is only one way the recipient is determined: randomly selected amongst its neighbors.
Note that, because each component's RNG is seeded by its global position in the 2D grid, you should expect to get deterministic results when rerunning a simulation, even if you change the distribution of the components across nodes.

When running with multiple MPI ranks / threads, the rows are distributed across MPI ranks, and the columns are then distributed across threads. 

The PHOLD simulation has a large number of parameters:
* `--height` and `--width`: Define the shape of the 2D grid of components
* `--time-to-run`: The duration to run the simulation. This should be an SST-style time string, i.e. `100ns` rather than `100`.
* `--link-delay`: The delay for the links in the simulation. Default is `1ns`, and should also be an SST-style time string.
* `--num-rings`, optionally `--ring-size`: The number of rings of neighbors to connect to. For example, `1` produces a grid of components where each only has 1 self-link. `2` produces components with 9 links total: 1 self-link and 8 to each of its surrounding neighbors. `2` produces components with 25 links. **Note that links do not wrap around the edge of the grid**.
* `--event-density`: The number of events the simulation is initialized with, per component. 
* `--node-type`: The type of node to use for the grid of components. The default is the constant-time delay `phold.Node`. You can also use `phold.ExponentialNode` and `phold.UniformNode`, where link delays are drawn from those types of distributions.
* `--exponent-multiplier`: For `phold.ExponentialNode`, this argument scales the exponential distribution from which additional delays on links are drawn.
* `--small-payload`, `--large-payload`, and `large-event-fraction`: Each event carries an (unused) payload of either a small or large size. These parameters set those sizes, in bytes, and the fraction of events that are sent with the large payload. By default, small is 8 bytes, large is 1024 bytes, and large event fraction is 0.1.
* `--component-size`: Each component has an additional field that is an allocated block of memory. This allows experimentation with the amount of memory used by each component. This argument controls the size of that field in bytes, and is 0 by default.
* `--imbalance-factor`: This parameter adds thread-level load imbalance to the distribution of components. Values should be between 0 and 1. A value of 0 indicates perfect balance and a value of 1 indicates complete imbalance (all work on one thread). 
* `--verbose`: This argument controls whether, at the end of the simulation, each component prints the number of events it received. This is useful for verifying correctness.

## `submit.py` and `dispatch.sh`

These two scripts, together, handle submitting, running, and collecting data from multiple PHOLD simulations in a single command.
Generally, users will only ever need to use the `submit.py` script. 

#### `submit.py`
`submit.py` enables parameter sweeps over both simulation parameters and execution environment parameters.
For each of the numeric parameters to `phold_dist.py`, there are corresponding parameters, optionally made plural, that accept quoted, space-separated strings of values.
`submit.py` iterates over all the combinations of the parameters provided. In addition, there are 3 parameters related to the execution environment that behave similarly:
* `--node-counts`: The number(s) of nodes to run the simulation across
* `--rank-counts`: The number(s) of MPI ranks to run on each node
* `--thread-counts`: The number(s) of C++ threads to run on each MPI rank. 

Additionally, the `--components-per-node` argument can be used in combination with `--heights` to have the script automatically calculate the corresponding widths.

There is also the `--name` argument. This one controls the prefix to the outputs put together containing any debugging and results output. 
It is usually best to give descriptive names to your experiments.


There are a couple of arguments that change the behavior of the `submit.py` script. 
First, is `--weak-scaling`. 
This argument is used to do node-level weak scaling. 
Its effect is to treat the values passed to `--heights` as per-node heights rather than global grid heights. This can be used to ensure that as the number of nodes being used in an experiment changes, the size of the simulation changes proportionally.

Second, there is the `--stochastic` argument.
This argument changes the behavior of the script from performing a total combinatorial sweep of the combinations to doing random sampling.
When used, all numeric parameters are interpreted as either constant values or a pair of bounds from which the script should sample actual values.
If you pass more than 2 arguments to a parameter when using `--stochastic`, all but the first two values will be ignored.
The argument passed to `--stochastic` determines how many samples to take and thus, how many simulations to run. 
For example, consider the following submission command:
```
python3 submit.py --node-counts "1 8" --width "1 1000" --height "256" --event-density "1.0 10.0" --ring-size 5 --stochastic 10
```
This will run 10 simulations. 
Each simulation will use a random number of nodes, between 1 and 8, a grid width between 1 and 1000, a height of 256, and event density between 1.0 and 10.0, and a ring size of 5.



#### `dispatch.sh`

Each job that `submit.py` queues is actually an instance of the `dispatch.sh` command. 
This command prepares the `sst` command, directing its outputs to different files, and collects global simulation metrics.
The metrics collected are: build time, run stage time, maximum global memory usage, and maximum per-rank memory usage.

## `consolidate.py`

Once the runs from an experiment are done, the `consolidate.py` script can be used to gather the results into a single `.csv` file.
The first argument to this script is the output `.csv` file name. All subsequent arguments are substrings to look for in the beginning of the output files.
This usually corresponds to the `--name` argument to the `submit.py` script. However if you have a series of experiments, say `exp1`, `exp2`, and `exp3`, you can run `python3 consolidate.py exp-all.csv exp` to gather all three experiment results into a single collection.

Also keep in mind that in addition to the file containing the results of successful runs, `consolidate.py` also creates a parallel `.csv` file containing information about failures.
This filename simply inserts `-failures` before the `.csv` in the provided output file argument.
In the `exp-all` example, it would produce `exp-all-failures.csv`.

## PHOLD AHP

PHOLD AHP is an alternative implementation of the PHOLD benchmark using the [AHP Graph](https://github.com/lpsmodsimteam/ahp_graph) library for topology construction. This approach uses a hierarchical device graph abstraction that partitions the 2D grid into row-based subgrids.

### Prerequisites

In addition to SST, you need the `ahp_graph` library.
```bash
git clone https://github.com/lpsmodsimteam/ahp_graph.git
cd ahp_graph
pip install -e .
```

### `phold_dist_ahp.py`

`phold_dist_ahp.py` is the AHP-based SST simulation description file. It constructs the same 2D grid topology as `phold_dist.py` but uses AHP's `Device` and `DeviceGraph` abstractions.

#### Simulation Parameters

Most parameters mirror those in `phold_dist.py`:

* `--height` and `--width`: Define the shape of the 2D grid of components.
* `--time-to-run`: Duration to run the simulation (SST-style time string, e.g., `100ns`).
* `--link-delay`: Delay for each link (default: `1ns`).
* `--num-rings` or `--ring-size`: Number of rings of neighbors to connect. `0` produces only self-links, `1` produces 9 links (self + 8 neighbors), etc.
* `--event-density`: Number of events per component at initialization.
* `--node-type`: Component type to use (default: `phold.Node`). Also supports `phold.ExponentialNode` and `phold.UniformNode`.
* `--exponent-multiplier`: Scales the exponential distribution for `phold.ExponentialNode`.
* `--small-payload` and `--large-payload`: Sizes of event payloads in bytes (defaults: 8 and 1024).
* `--large-event-fraction`: Fraction of events using the large payload (default: 0.0).
* `--component-size`: Size of additional memory allocated per component in bytes (default: 0).
* `--imbalance-factor`: Thread-level load imbalance factor between 0 (balanced) and 1 (all work on one thread).
* `--verbose`: Verbosity level for logging. Higher values print more detailed link wiring information.

#### AHP-Specific Parameters

* `--print-links`: Print detailed link wiring information during topology construction.
* `--no-self-links`: Disable self-links (by default, each component has a self-link).
* `--partitioner`: Choose the partitioner: `ahp_graph` (default) or `sst`.

#### Execution Mode Parameters

* `--build`: Build and run the topology with SST (default if no mode specified).
* `--write`: Write the topology to JSON files instead of running.
* `--draw`: Write the topology to DOT format (not currently implemented).
* `--numNodes` or `--num-nodes`: Number of compute nodes (used when running without SST).
* `--numRanks`: Number of MPI ranks per node (used when running without SST).
* `--rank`: Which rank to generate JSON for (used when running without SST).
* `--trial`: Trial number for output filename. When >= 0, output files use the pattern `ahp_phold_*_part_trialY_TYPEX.json`.

#### Example Usage

Run a simulation directly with SST:
```bash
sst phold_dist_ahp.py -- --height 100 --width 100 --num-rings 2 --event-density 1.0 --time-to-run 100ns
```

Generate JSON topology files for verification (without running SST):
```bash
python3 phold_dist_ahp.py --height 10 --width 10 --num-rings 2 --numNodes 2 --numRanks 1 --rank 0 --write
python3 phold_dist_ahp.py --height 10 --width 10 --num-rings 2 --numNodes 2 --numRanks 1 --rank 1 --write
```

This creates JSON files in `output/height-10_width-10_numRings-2_numNodes-2_numRanks-1/` for each rank.

### `compare_topologies.py`

`compare_topologies.py` is a utility script that compares topologies from SST JSON output files using NetworkX. It supports both the original PHOLD link naming convention and the AHP naming convention, making it useful for verifying that the AHP implementation produces equivalent topologies.

#### Features

- Parses both link naming conventions:
  - **Original**: `link_x_y_to_x_y` (e.g., `link_0_0_to_0_1`)
  - **AHP**: `SubGridN.comp_x_y.portN__delay__SubGridM.comp_a_b.portM`
- Loads and merges topologies from multiple JSON files (one per rank)
- Compares node sets, edge sets, and node degrees between graphs
- Generates visualization plots highlighting differences

#### Usage

```bash
python3 compare_topologies.py --og og_rank0.json og_rank1.json --ahp ahp_rank0.json ahp_rank1.json
```

#### Arguments

* `--og`: One or more JSON files containing the original topology (required).
* `--ahp`: One or more JSON files containing the AHP topology (required).
* `--output` or `-o`: Output image filename (default: `topology_comparison.png`).
* `--no-plot`: Skip plotting and only print the comparison results.

#### Example 1

Compare a 2-rank original topology against the AHP equivalent using SST JSON writing.
```bash
# Generate original topology JSON files
mpiexec -n 2 sst phold_dist.py --output-json=og_rank.json --parallel-output=true -- --height 10 --width 10 --num-rings 2

# Generate AHP topology JSON files
mpiexec -n 2 sst phold_dist_ahp.py --output-json=ahp_rank.json --parallel-output=true -- --height 10 --width 10 --num-rings 2

# Compare the topologies
python3 compare_topologies.py \
    --og og_rank0.json og_rank1.json \
    --ahp ahp_rank0.json ahp_rank1.json \
    --output comparison.png
```

#### Example 2

Compare a 2-rank original topology against the AHP equivalent using AHP JSON writing. For this we will directly use AHP's JSON writing functionality. For this, you need to specify directly the number of nodes, number of ranks per node, and the rank for which to write the JSON file. The script will automatically get the total number of ranks by multiplying number of nodes by number of ranks. 

```bash
# Generate the JSON for rank 0
python3 phold_dist_ahp.py --height 10 --width 10 --num-rings 2 --num-rings 2 --num-nodes 1 --num-ranks 2 --rank 0 --write

# Generate the JSON for rank 1
python3 phold_dist_ahp.py --height 10 --width 10 --num-rings 2 --num-rings 2 --num-nodes 1 --num-ranks 2 --rank 1 --write

# Compare the topologies
python3 compare_topologies.py \
    --og og_rank0.json og_rank1.json \
    --ahp output/height-10_width-10_numRings-2_numNodes-1_numRanks-2/ahp_phold_ahp_part_python0.json \
          output/height-10_width-10_numRings-2_numNodes-1_numRanks-2/ahp_phold_ahp_part_python0.json \
    --output comparison.png
```

Use this method to sidestep SST's build step if the end goal is only to generate JSON files.

#### Output

The script prints:
- Node counts for each topology
- Nodes unique to each topology
- Edge counts for each topology
- Edges unique to each topology
- Degree comparison for nodes present in both graphs

If topologies match:
```
✓ Topologies are IDENTICAL
```

If topologies differ:
```
✗ Topologies are DIFFERENT
```

When plotting is enabled, a side-by-side visualization is saved showing both topologies with differing edges highlighted in red.
