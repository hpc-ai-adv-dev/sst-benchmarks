# Simple Merlin Network Benchmark - Design Document

## Overview

This design proposes a scalable, configurable network benchmark using the Merlin element library. The benchmark will evaluate network topology performance by injecting synthetic traffic patterns and measuring key metrics such as latency, throughput, and link utilization.

**Primary Goal**: Create a standalone benchmark that demonstrates:
1. Successful use of Merlin outside the sst-elements repository
2. Scalable network topology simulation (from 4 to 1000+ routers)
3. Configurable traffic generation and measurement
4. Easy parameter variation for design space exploration

---

## Benchmark Scope

### What This Benchmark Tests
- **Network Topology Behavior**: How different topologies (mesh, torus, fat-tree) handle traffic
- **Routing Efficiency**: Path diversity and congestion effects
- **Link Utilization**: Bandwidth saturation and underutilization patterns
- **Packet Latency**: Dependency on topology, routing, and link congestion
- **Scalability**: Simulation time and memory scaling with topology size

### What This Benchmark Does NOT Include (Phase 1)
- Detailed CPU core simulation (no Vanadis)
- Memory system effects (no MemHierarchy)
- Application-level communication patterns (synthetic traffic only)
- NUMA effects or multi-layer topology studies

---

## Architecture

### Benchmark Components

```
┌─────────────────────────────────────────────┐
│     Simple Merlin Network Benchmark         │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────────────────────────┐       │
│  │   Traffic Generator Endpoints    │       │
│  │  (Simple packet injectors)       │       │
│  │  (1-256 endpoints)               │       │
│  └──────────┬───────────────────────┘       │
│             │ (packets)                     │
│  ┌──────────▼───────────────────────┐       │
│  │   Merlin Network Topology        │       │
│  │   ┌─────────────────────────┐    │       │
│  │   │  Routers (1-256)        │    │       │
│  │   │  Connected in topology: │    │       │
│  │   │  - Mesh (2D/3D)         │    │       │
│  │   │  - Torus (2D/3D)        │    │       │
│  │   │  - Fat-tree             │    │       │
│  │   │  - Single router        │    │       │
│  │   └─────────────────────────┘    │       │
│  └──────────────────────────────────┘       │
│             │ (collected stats)             │
│  ┌──────────▼───────────────────────┐       │
│  │   Statistics Collection          │       │
│  │   - Packet latencies             │       │
│  │   - Throughput per link          │       │
│  │   - Router occupancy             │       │
│  │   - Congestion metrics           │       │
│  └──────────────────────────────────┘       │
│                                             │
└─────────────────────────────────────────────┘
```

### Key Merlin Components Used

1. **Merlin Routers** (`merlin.hr_router`)
   - Configurable radix (ports per router)
   - Crossbar switching with arbitration
   - Virtual networks for traffic separation
   - Port-level flow control

2. **Network Topology** (Python helpers)
   - Dynamically instantiate routers
   - Connect routers based on topology specification
   - Create endpoint connections

3. **Simple Endpoints** (Custom SST component or synthetic generator)
   - Generate network traffic
   - Various patterns: uniform random, local, hotspot
   - Configurable injection rate

4. **Statistics Collection**
   - Per-router statistics (flits processed, congestion)
   - Per-link statistics (utilization, latency)
   - End-to-end packet latencies

---

## Benchmark Design Details

### Traffic Patterns

Four configurable traffic patterns:

```
1. **Uniform Random (UR)**
   - Each endpoint sends to random destinations
   - Tests balanced load distribution
   - Parameter: injection_rate (packets/cycle)

2. **Local Neighbor (LN)**
   - Send preferentially to nearby routers
   - Tests locality exploitation
   - Parameters: locality_radius, local_probability

3. **Hotspot (HS)**
   - All endpoints send to a few "hot" routers
   - Tests congestion handling
   - Parameters: num_hot_routers, concentration_factor

4. **Bit-Reversal Permutation (BR)**
   - Bit-reversal address mapping
   - Tests pathological patterns
   - Parameter: rank (log2 of system size)
```

### Configurable Parameters

#### Topology Parameters
```
topology_type:
  - "mesh_2d"      : 2D mesh
  - "torus_2d"     : 2D torus with wraparound
  - "mesh_3d"      : 3D mesh
  - "torus_3d"     : 3D torus
  - "fattree"      : Fat-tree hierarchy
  - "single"       : Single router (for endpoint count scaling)

topology_dimensions:
  - "mesh_2d" / "torus_2d": [rows, cols]
  - "mesh_3d" / "torus_3d": [x, y, z]
  - "fattree": radix (k parameter)
  - Examples:
    - [4, 4]        → 16 routers (2D mesh)
    - [4, 4, 4]     → 64 routers (3D mesh)
    - 4             → 20 routers (fat-tree k=4)
```

#### Network Parameters
```
router_radix:                  # Ports per router (default: 4)
link_bandwidth:               # Per-link bandwidth (e.g., "10GB/s")
link_latency:                 # Per-hop latency (e.g., "100ns")
flit_size:                    # Flit size in bits (default: 128)
num_virtual_networks:         # VNs for traffic separation (default: 1)
arbitration_type:             # "rr", "lru", "age", "rand"
```

#### Traffic Parameters
```
traffic_pattern:              # Pattern type (see above)
injection_rate:              # Packets/cycle per endpoint
message_size:                # Packet size in flits (default: 1)
simulation_cycles:           # Total simulation length
warmup_cycles:              # Discard stats during warmup
```

#### Output Parameters
```
enable_detailed_stats:        # Per-router statistics
stat_interval:               # Statistic output interval
```

### Configuration File Format

JSON-based configuration with profiles:

```json
// merlin_config.json

  "quick_test": {
    "topology": {
      "type": "mesh_2d",
      "dimensions": [2, 2]
    },
    "network": {
      "router_radix": 4,
      "link_bandwidth": "10GB/s",
      "link_latency": "100ns"
    },
    "traffic": {
      "pattern": "uniform_random",
      "injection_rate": 0.1,
      "simulation_cycles": 10000,
      "warmup_cycles": 1000
    }
  },
  "medium_mesh": {
    "topology": {
      "type": "mesh_2d",
      "dimensions": [8, 8]
    },
    "network": {
      "router_radix": 4,
      "link_bandwidth": "12.5GB/s",
      "link_latency": "100ns"
    },
    "traffic": {
      "pattern": "uniform_random",
      "injection_rate": 0.3,
      "simulation_cycles": 100000,
      "warmup_cycles": 10000
    }
  },
  "large_fattree": {
    "topology": {
      "type": "fattree",
      "dimensions": 8
    },
    "network": {
      "router_radix": 8,
      "link_bandwidth": "25GB/s",
      "link_latency": "50ns"
    },
    "traffic": {
      "pattern": "uniform_random",
      "injection_rate": 0.4,
      "simulation_cycles": 500000,
      "warmup_cycles": 50000
    }
  }
}
```

---

## Implementation Approach

### Phase 1: Foundation (This Deliverable)

**Step 1: Create Python SST Configuration Script** (`benchmark.py`)
- Import Merlin topology modules
- Parse configuration (from file or command-line)
- Instantiate topology and routers
- Create simple endpoint generators (as sub-components or external sources)
- Wire everything together
- Add statistics collection

**Step 2: Create Simple Endpoint Generator Component** (`endpoint_generator.cc`)
- Lightweight SST component
- Generates packets based on traffic pattern
- Simple destination calculation (local, random, hotspot)
- Injects packets into connected router port
- Collects latency statistics

**Step 3: Configuration Files** (`configs/`)
- `quick_test.yaml`: Minimal 2x2 mesh for validation
- `medium_mesh.yaml`: 8x8 mesh for moderate testing
- `large_fattree.yaml`: Fat-tree for scaling studies

**Step 4: Runner Scripts** (`run_benchmark.sh`)
- Execute benchmark with specified configuration
- Parse command-line arguments
- Handle output collection and analysis
- Support parameter sweeps

**Step 5: Documentation** (`README.md`)
- Setup instructions
- How to run benchmarks
- Parameter explanation
- Output interpretation

### Phase 2: Enhancement (Future)

- Add Merlin traffic generation plugins
- More sophisticated traffic patterns (synthetic workloads from Ember)
- Detailed per-link visualization
- Comparison utilities
- Automated scaling studies

### Phase 3: Integration (Future)

- Merge with Ember for realistic HPC communication patterns
- Add Firefly NICs as endpoints
- Create multi-benchmark studies

---

## Build & Execution Plan

### Build Structure

```
merlin-benchmark/
├── README.md                      # Benchmark documentation
├── DESIGN.md                      # This file
├── Makefile                       # Build configuration
├── src/
│   ├── endpoint_generator.cc      # Custom traffic endpoint component
│   ├── endpoint_generator.h
│   └── Makefile
├── lib/
│   └── (compiled libraries placed here)
├── configs/
│   ├── quick_test.json           # Fast validation config
│   ├── medium_mesh.json          # Medium 8x8 mesh
│   ├── large_fattree.json        # Large fat-tree
│   ├── weak_scaling_configs/     # Weak scaling study configs
│   ├── strong_scaling_configs/   # Strong scaling study configs
│   └── custom_template.json      # Template for custom configs
├── python/
│   ├── benchmark.py              # Main SST configuration script
│   ├── topology_builder.py        # Topology instantiation helpers
│   └── traffic_patterns.py        # Traffic pattern generators
├── scripts/
│   ├── run_benchmark.sh          # Main runner script
│   ├── run_weak_scaling_study.sh # Weak scaling sweep
│   ├── run_strong_scaling_study.sh # Strong scaling sweep
│   └── analyze_results.py        # Result analysis utility
└── results/
    └── (output data placed here)
```

### Build Process

```bash
# 1. Build the endpoint_generator component
cd merlin-benchmark/
make clean      # Optional: clean previous builds
make

# 2. Verify library was created
ls -la lib/libendpoint_generator.so

# 3. Benchmark is ready to run
```

### Execution Process

```bash
# Run with quick test (validation)
./scripts/run_benchmark.sh configs/quick_test.json

# Run with configuration file
sst --lib-path=./lib python/benchmark.py configs/medium_mesh.json

# Run with command-line overrides
sst --lib-path=./lib python/benchmark.py configs/medium_mesh.json \
    topology.dimensions=[16,16] \
    traffic.injection_rate=0.5
```

### Output

```
# Statistics file: results/benchmark_<timestamp>.out

Simulation Complete
Total Cycles: 100000
Warmup Cycles: 10000

Network Statistics:
  Total Packets Injected:    1234567
  Total Packets Delivered:   1234500
  Packet Loss Rate:          0.005%
  
  Average Latency:           285.3 cycles
  Min Latency:               15 cycles
  Max Latency:               1245 cycles
  Median Latency:            250 cycles
  
Link Utilization:
  Average Link Utilization:  35.2%
  Max Link Utilization:      98.1% (Router_4-5)
  Min Link Utilization:      2.3%  (Router_15-19)

Router Statistics:
  [Per-router throughput, congestion, occupied slots]
  ...

Topology: mesh_2d [8x8]
Configuration: medium_mesh
Traffic Pattern: uniform_random
Injection Rate: 0.3
```

---

## Success Criteria

### Build Validation
- ✓ Makefile compiles endpoint_generator component without errors
- ✓ libendpoint_generator.so library is created in lib/ directory
- ✓ SST can load the library (no symbol errors)
- ✓ Builds reproducibly after `make clean`

### Behavioral Validation
- ✓ Merlin routers instantiate correctly for all topology types
- ✓ Endpoints inject and receive packets
- ✓ Multiple topology types functional (mesh, torus, fat-tree)
- ✓ Statistics collected and reported (latency, throughput, utilization)
- ✓ Output statistics are reasonable (non-zero, bounded values)
- ✓ Packet delivery rate > 99% at low injection rates
- ✓ Latency increases monotonically with injection rate
- ✓ Topology size scaling produces expected simulation time

### Performance Goals
- Quick test: 10 seconds to complete
- Medium test: 2-5 minutes to complete
- Large test: 10-30 minutes to complete

### Scaling Support
- ✓ Weak scaling: Multiple configs with increasing topology/load
- ✓ Strong scaling: Multiple configs with fixed topology, increasing load
- ✓ Runs on HPC system (SLURM/batch compatible)

### Documentation Goals
- Clear setup and build instructions
- Parameter explanations
- Example configurations for each scaling study
- Output interpretation guide
- How to run weak/strong scaling studies

---

## Known Challenges & Mitigation

| Challenge | Solution |
|-----------|----------|
| **Library Paths** | Use `--lib-path` and relative paths in scripts |
| **Merlin Python API** | Reference existing Merlin examples in sst-elements |
| **Endpoint Component** | Start simple (single flit packets), extend later |
| **Statistics Overhead** | Selective stat collection per configuration |
| **Scaling Simulation Time** | Quick configs for testing, large configs for results |

---

## Implementation Roadmap

### Phase 1: Build & Core Functionality (Primary Deliverable)

1. **Setup directory structure**
   - Create `src/`, `python/`, `configs/`, `scripts/`, `lib/` directories
   - Create Makefile skeleton in root and `src/` subdirectory

2. **Create Makefile** (`Makefile` and `src/Makefile`)
   - Configure build for endpoint_generator component
   - Link against SST core/elements libraries
   - Output library to `lib/libendpoint_generator.so`

3. **Implement endpoint_generator component** (`src/endpoint_generator.cc/.h`)
   - Define custom SST component class
   - Implement packet generation based on traffic pattern
   - Implement destination calculation (random, local, hotspot)
   - Collect latency statistics
   - Connect to Merlin router port

4. **Implement benchmark.py** (`python/benchmark.py`)
   - Import Merlin topology modules
    - Parse JSON configuration
   - Bash wrapper for consistent execution
   - Parse command-line arguments
   - Call `sst --lib-path=./lib python/benchmark.py <config>`
   - Output to `results/` directory

### Phase 1 Validation

8. **Build Validation**
   - `make clean && make` succeeds
   - `lib/libendpoint_generator.so` created and loadable

9. **Behavioral Validation** (using quick_test.json)
   - Simulation completes successfully
   - Output statistics are reasonable
   - Packet delivery rate > 99%

### Phase 2: Scaling & Comprehensive Testing

10. **Add remaining configurations**
    - `configs/medium_mesh.json`: 8x8 mesh
    - `configs/large_fattree.json`: Fat-tree
    - `configs/weak_scaling_configs/`: Weak scaling study set
    - `configs/strong_scaling_configs/`: Strong scaling study set

11. **Create scaling study runners**
    - `scripts/run_weak_scaling_study.sh`
    - `scripts/run_strong_scaling_study.sh`

12. **Create result analysis tools** (`scripts/analyze_results.py`)
    - Parse output files
    - Extract key metrics
    - Generate comparison tables

13. **Documentation** (`README.md`)
    - Setup and build instructions
    - Configuration parameter reference
    - How to run individual benchmarks
    - How to run scaling studies
    - Output interpretation guide

---

## Design Decisions - Confirmed

1. **Endpoint Generator**: Custom SST component
   - *Decision*: Define custom `endpoint_generator` component
   - *Rationale*: Practice integrating existing components (Merlin) with custom-defined ones
   - *Benefit*: Full control over traffic generation and measurement

2. **Configuration Format**: JSON
    - *Decision*: Use JSON-based configuration files
    - *Rationale*: Native JSON support in Python, human-readable, lightweight
   - *Location*: `configs/` directory with named profiles

3. **Scaling Studies**: Both Weak and Strong Scaling
   - *Decision*: Support both via separate configuration sets
   - *Weak Scaling*: Increase problem size with processor count (configs/weak_scaling_configs/)
     - Topology size scales, load per node stays constant
   - *Strong Scaling*: Fixed problem size, increase processor count (configs/strong_scaling_configs/)
     - Topology size scales, load per node decreases
   - *Implementation*: Multiple config files for each scaling point

4. **Validation Strategy**: Build and Behavioral
   - *Decision*: Validate both build success AND benchmark behavior
   - *Build Validation*: Ensure compilation succeeds and library links correctly
   - *Behavioral Validation*: Verify benchmark produces expected output and reasonable statistics
   - *Test Approach*: quick_test.yaml provides fast validation (seconds, not minutes)

---

## References & Related Work

- SST Elements Merlin Documentation: http://sst-simulator.org/sst-docs/docs/elements/merlin/intro
- SST Benchmark Suite: https://github.com/sstsimulator/sst-benchmarks
- Previous SST Merlin Examples: `sst-elements/src/sst/elements/merlin/tests/`

