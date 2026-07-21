# Merlin Benchmark

This directory contains a configurable SST Merlin benchmark plus utilities for notebook-driven experiment generation.

## What is in this directory

- `merlin_benchmark.py`
  - Main SST Python configuration script.
  - Parses CLI arguments, selects a topology, applies network and traffic-generator parameters, and builds a distributed simulation.
- `merlin_topologies.py`
  - Topology and endpoint implementation module.
  - Defines mesh, dragonfly, and fat-tree topologies and endpoint classes, including a traffic generator endpoint.
- `workflow_args.py`
  - Notebook-friendly run-spec generator.
  - Produces structured argument tokens for launcher (`srun` and `mpirun`), `sst`, and `merlin_benchmark.py` config args.
- `src/trafficgen.cc`
  - C++ component implementation used by the benchmark plugin library.
- `Makefile`
  - Builds and installs `libmerlin_benchmark.so` and optionally registers it with `sst-register`.
- `run_check.sh`
  - Convenience script that runs the benchmark on node counts `1 2 4` and compares CHECK output consistency.
- `tests/test_workflow_args.py`
  - Unit tests for `workflow_args.py`.

## Prerequisites

- A working SST core installation with `sst-config` available.
- SST elements source available (for include headers referenced in `Makefile`).
- Python environment with SST Python bindings available when running `sst` scripts.

Optional environment overrides used by the Makefile:

- `SST_CONFIG`
- `SST_REGISTER`
- `SST_CORE_HOME`
- `SST_ELEMENTS_HOME`
- `SST_ELEMENTS_SRC`
- `SST_ELEMENT_LIBDIR`

## Build and install plugin

From this directory:

```bash
make print-config
make
```

This builds `libmerlin_benchmark.so`, copies it into the SST element library directory, and runs `sst-register` when available.

## Important module naming note

`merlin_benchmark.py` currently imports:

```python
import realistic_benchmarks
```

but this directory's topology implementation file is named `merlin_topologies.py`.

Use one of these approaches before running:

1. Create a local shim file named `realistic_benchmarks.py` that re-exports from `merlin_topologies`.
2. Rename/copy `merlin_topologies.py` to `realistic_benchmarks.py` in your local workflow.
3. Update the import in `merlin_benchmark.py` to `import merlin_topologies as realistic_benchmarks`.

## Running the benchmark script

General invocation pattern:

```bash
sst merlin_benchmark.py -- <benchmark-args>
```

For distributed runs, use launcher + `sst`, for example:

```bash
mpirun -N 2 sst --parallel-load=SINGLE merlin_benchmark.py -- --topology mesh
```

### Topology selection

- `--topology mesh`
  - Primary controls: `--mesh-shape`, `--mesh-width`, `--mesh-local-ports`
- `--topology dragonfly`
  - Primary controls: `--dragonfly-hosts-per-router`, `--dragonfly-routers-per-group`, `--dragonfly-intergroup-links`, `--dragonfly-num-groups`, `--dragonfly-algorithm`, `--dragonfly-global-routing-mode`
- `--topology fattree`
  - Primary control: `--fattree-shape`

### Global and network controls

- Global: `--stop-at`, `--verbose`
- Network: `--flit-size-bytes`, `--link-bw-gbps`, `--link-lat-ns`, `--xbar-bw-gbps`

### Endpoint/traffic-generator controls

The benchmark exposes many `tg-*` options for output behavior and packet destination/size/delay distributions. See `merlin_benchmark.py` argument groups for the complete list.

## Topology implementation details (`merlin_topologies.py`)

Key classes:

- `Topo`: base class for topology wiring and endpoint attachment.
- `topoMesh`, `topoDragonFly`, `topoFatTree`: concrete distributed topology builders.
- `EndPoint`, `TestEndPoint`, `TrafficGenerator`: endpoint abstractions and implementations.

Execution model highlights:

- The module stores global state in `_params`, including MPI rank count and thread count detected from SST.
- Each topology has `prepParams()` for parameter normalization/derived values and `build_distributed()` for rank-aware component/link construction.
- `merlin_benchmark.py` sets topology-specific values in `_params`, then calls:
  - `topo.prepParams()`
  - `endPoint.prepParams()`
  - `topo.setEndPoint(endPoint)`
  - `topo.build_distributed()`

## Notebook workflow with `workflow_args.py`

`workflow_args.py` is intended for generating experiment sweeps without submitting jobs directly.

Main APIs:

- `generate_merlin_run_specs(...)`
  - Returns a list of `MerlinRunSpec` objects.
  - Each run spec includes:
    - `launcher['srun']`: token list for `srun`
    - `launcher['mpirun']`: token list for `mpirun`
    - `sst_args`: token list for `sst`
    - `config_args`: token list for `merlin_benchmark.py -- ...`
    - `run_name`, `run_id`, and metadata
- `format_command_preview(run_spec, config_script='merlin_benchmark.py')`
  - Renders full preview command strings for `srun` and `mpirun` paths.

### Supported/unsupported behavior in workflow_args

- Supports deterministic mode (cartesian product) and stochastic mode.
- Requires `stochastic_seed` when `stochastic_samples` is used.
- Topology-specific parameter dictionaries are validated against known keys.
- Does not support thread-count sweep control in this API.

### Minimal notebook example

```python
from workflow_args import generate_merlin_run_specs, format_command_preview

specs = generate_merlin_run_specs(
    node_counts=[1, 2],
    rank_counts=[1, 2],
    topologies=["mesh", "dragonfly"],
    mesh_params={"mesh_shape": ["4x4", "8x8"]},
    dragonfly_params={"dragonfly_num_groups": [9, 16]},
    experiment_name="topo_sweep"
)

first = specs[0]
preview = format_command_preview(first)
print(first.run_name)
print(preview["mpirun"])
```

## Consistency check script

Use `run_check.sh` to compare CHECK output across node counts `1`, `2`, and `4`:

```bash
./run_check.sh --topology mesh --mesh-shape 4x4
```

The script writes `.check` files and pairwise `.diff` files and reports whether outputs match.

## Testing

Run workflow argument unit tests:

```bash
python3 -m unittest tests/test_workflow_args.py
```

## Current limitations

- No built-in submit/dispatch script in this directory yet (unlike the PHOLD benchmark flow).
- Result extraction/consolidation tooling is not yet implemented for Merlin in this directory.
