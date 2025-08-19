# sst-benchmarks

This repository contains files implementing benchmarks using SST. Namely, a 1 or 2 dimensional ping-pong simulation and the scripts necessary to do scaling evaluation and profiling of the simulation.
The simulation code was prepared by Andy Stone and the submission/profiling scripts by Brandon Neth.

Prior to running the benchmark, please compile the source files by running:

```bash
make all
```

## The Ping Pong Simulation
To study SST’s scalability, we have developed a "ping pong” benchmark. The purpose of this benchmark is to study SST's performance when conducting a simulation that consists of large numbers of simple components.

Specifically, the "Ping Pong Simulation" adds two components to SST:

  - A simulator component whose only purpose is to manage the lifetime of the
    simulation (stop it after a set amount of simulated time has passed). And,
  - A Ponger component, this component connects to (up to) four adjacent ponger
    components to its north, south, west, and east.  When a ponger receives a
    message from its neighbor it will propagate it along.  If the ponger doesn't
    have a neighbor to propagate the message to it will "bounce" it back.

The ponger components can be arranged into a 1-dimensional grid of N components
that connect west-to-east or a 2D grid of NxN components.  The pongers are
preloaded with a set number of "ball" messages.

There are two python scripts that can be used as input configurations for SST.
Both have the same command line arguments.
- `pingpong.py`: A sequential version of the script
- `pingpong_parLoad.py`: A parallel loading version of the script.

To run, invoke SST with one of the two scripts.  E.g., ``sst pingpong.py --
--corners``

The scripts take the following parameters (each taking an integer argument):

- `--N` -- Size of the grid (defaults to 10)
- `--timeToRun` -- How long to run the simulation (in seconds; defaults to 200)
- `--numDims` -- Either 1 or 2 to specify dimensionality (defaults to 2)
- `--edgeDelay` -- How long it takes to propogate a message from one ponger to the next in simulated seconds (defaults to 50)
- `--artificialWork` -- When processing a ponger message conduct a meaningless loop that does a multiplication operation on a number for a set number of times. This is useful for studying scalability, where increasing this value can look at the impact of messages taking more or less time to conduct.

Additionally the user must choose exactly one of the following to set the initial placement of balls:
- `--corners` -- place balls in the corners of the 1D or 2D grid.
- `--random` -- randomly place balls in the grid such that no ponger has more than 1 ball
- `--randomOverlap` -- randomly place balls in the grid (where a single component may have more than one ball)
- `--wavefront` -- add balls along the perimeter of the grid (only works on 2d sim)

There is also a `--verbose` that if passed prints debugging information.


## Submission Scripts

This repository also contains scripts necessary to run scaling evaluations of the ping-pong simulation: `omnisubmit.py` and `omnidispatch.sh`.
**The purpose of these scripts is to be able to launch all the runs necessary for a particular experiment with a single command.**
These scripts are meant to be used on a machine that runs jobs using SLURM.
In general, you will only need to use the `omnisubmit.py` script, which submits the jobs for whatever scaling evaluation you wish to run.

In general, it is a good idea to read through the available flags that the script accepts, using `python3 omnisubmit.py -h`, but we review them here and give some examples.
Many of the arguments accept integers or quoted, space-separated lists of integers.
The script enumerates all combinations of all the lists and submits jobs for each of them.

### Scale Options
`omnisubmit.py` always takes three unnamed arguments: a list of node counts, a list of MPI ranks per node, and a list of threads per MPI rank.
These can be single integers or quoted, space-separated lists of integers.
For example, `"1 2 4" 1 2` would launch 3 jobs, one with a single node, one with two nodes, and one with four.
ALl three jobs would use one MPI rank per node and 2 C++ threads per MPI rank.
In the case where there are multiple lists, such as `"3 6" "1 4" 1`, the script enumerates and launches all combinations. Here, that would be:
- 3 nodes, 1 rank per node, 1 thread per rank
- 3 nodes, 4 ranks per node, 1 thread per rank
- 6 nodes, 1 rank per node, 1 thread per rank
- 6 nodes, 4 ranks per node, 1 thread per rank

### Grid Options
Next are the flags for specifying the size of the simulation itself.

The (required) `--dimensions` flag specifies how many dimensions your simulation should run. Valid options are 1 and 2, or a string separated list containing 1 and 2.
Like with the string separated scale options, the script enumerates and launches all combinations.

There are two flags that together specify how many components should be in the simulation: `--side-length` and `--component-counts`.
`--component-counts` is dimension-independent, whereas `--side-length` will have different behavior based on the dimensionality being used.
For example, if a script is run with the arguments: `--dimensions "1 2" --side-length "4 9"`, it will run simulations with the following configurations:
- 1 dimensional simulation, 4 components total
- 1 dimensional simulation, 9 components total
- 2 dimensional simulation, 16 (4x4) components total
- 2 dimensional simulation, 81 (9x9) components total
If, instead, the script is run with the arguments `--dimensions "1 2" --component-counts "4 9"`, it will run:
- 1 dimensional simulation, 4 components total
- 1 dimensional simulation, 9 components total
- 2 dimensional simulation, 4 (2x2) components total
- 2 dimensional simulation, 9 (3x3) components total
`--side-length` and `--component-counts` can both be used in the same launch. For example, `--dimensions 2 --component-count "4 9" --side-length "4 9" will run:
- 2 dimensional simulation, 4 (2x2) components total
- 2 dimensional simulation, 9 (3x3) components total
- 2 dimensional simulation, 16 (4x4) components total
- 2 dimensional simulation, 81 (9x9) components total

At least one of  `--side-length` or `--component-counts` needs to be present or the script will exit.

### Communication Options
Next are the flags for specifying the messages being passed among the components.
There are four possible communication patterns, described above, which correspond to the following flags: `--corners`, `--wavefront`, `--random`, and `--randomOverlap`.
The `--random` and `--randomOverlap` flags require an integer, or quoted, space-separated list of integers, indicating how many balls to place randomly.
Like the grid options, multiple communication patterns can be specified, but at least one must be present.
For example, if you use the flags `--corners --random 100 --randomOverlap "200 300"`, there will be four types of runs (each possibly present multiple times if there are other lists):
- Runs using `--corners`
- Runs using `--random 100`
- Runs using `--randomOverlap 200`
- Runs using `--randomOverlap 300`

### Simulation Time Options
There are two flags related to the simulated time.
First is `--timestep-counts` which is another integer list of the number of timesteps to run in the simulation.
Second is `--edge-delay` which is an integer representing the delays for the messages moving across the links.
The edge delay is optional and defaults to 50. `--timestep-counts` needs to have at least one value, but like many others can have a list of integers.

### Remaining Simulation Options
Two other flags are related to the simulation itself: `--input-method` and `--verbose`.
`--input-method` indicates which method(s) the script should use to configure the simulation.
There are three options:
- "python": Use the sequential python loading script
- "pallelPython": Uses the parallel python loading script
- "json": Use the JSON generator to generate the input JSON script and load it into SST in parallel
Like most arguments to `omnisubmit.py`, this flag can take a space separated list of the above options.
At least one input method must be specified.

`--verbose` passes the `--verbose` flag through to SST.

### Experiment Options

Two flags support different types of experiments with the simulation: `--hpctoolkit` and `--weak-scaling`.

The `--hpctoolkit` flag indicates that the submitted simulations should be run using hpctoolkit to collect profiling information about the run.
If used, the submitted job will use `hpcrun` to run the job, `hpcstruct` to gather source information from the `sst` binary, and then use `hpcprof` to attribute the profiling data to the code.
Arguments passed to the `--hpctoolkit` flag will be forwarded to the `hpcrun` call. For example, using `--hpctoolkit "-e MEMLEAK"` will collect memory usage information from the application rather than execution time information.

The `weak-scaling` flag indicates that the submitted jobs are for a weak scaling run.
Weak scaling means that as the number of nodes / threads the program is run on increases, so does the size of the problem.
This means that problem information, like component counts and message counts, need to increase in propotion to the node/thread count.
To support this, the `--weak-scaling` flag treats all problem configuration information (side lengths, communication pattern information, etc.) as "base configurations" i.e. the configurations to use for a 1 node, 1 rank, 1 thread run.
For each of the scale configuration, the base configuration is scaled proportionally.

An example helps clarify. Say we were to run the following full submit command: `python3 omnisubmit.py "1 2 4 8" 1 1 --dimensions 2 --side-lengths "20 40" --random 100 --corners --timestep-count 1000 --input-method python`. What would happen?
First, we gather our base configurations. This is the product of the grid options and the communication pattern options. There are four for this submission:
- side length 20, random 100
- side length 20, corners
- side length 40, random 100
- side length 40, corners

Next, for each of the scale configurations, we submit a job where the base configuration is scaled by the appropriate scale. For the "side length 20, random 100", we get the following:
- 1 node, 1 rank, 1 thread, side length 20, random 100
- 2 nodes, 1 rank, 1 thread, side length 28 (`sqrt(20*20*2)`), random 200
- 4 nodes, 1 rank, 1 thread, side length 40 (`sqrt(20*20*4)`), random 400
- 8 nodes, 1 rank, 1 thread, side length 56 (`sqrt(20*20*8)`), random 800

Note that 2 dimensional cases may require rounding. It helps with data collection and analysis to use square node counts when doing weak-scaling runs.
