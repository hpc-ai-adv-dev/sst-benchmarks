# TrafficGen generator statistical tests

`test_trafficgen_distributions.cpp` verifies (statistically) the output
distributions of the pattern generators in
[`../src/generators.h`](../src/generators.h): `UniformDist`, `NormalDist`,
`DiscreteDist`, `ExponentialDist`, and `NearestNeighbor`.

## Why this is an SST component, not a plain executable

The generators use SST core's RNG classes (e.g. `SST::RNG::MersenneRNG`) and
the serialization/ELI machinery. Those symbols only exist inside a running
SST simulation binary (`sstsim.x`) -- there is no standalone linkable SST core
library to link a plain `main()` test executable against. So the test is
packaged as its own tiny SST component, `merlin_benchmark_test.disttest`,
which runs all checks in its constructor, prints `[ OK ]`/`[FAIL]` per check,
and exits the process with status 1 if anything failed.

## Build & run

```sh
make test          # builds libmerlin_benchmark_test.so, registers it, and runs it via `sst`
```

or manually:

```sh
$(sst-config --CXX) $(sst-config --ELEMENT_CXXFLAGS) $(sst-config --ELEMENT_LDFLAGS) \
    -Isrc -o libmerlin_benchmark_test.so tests/test_trafficgen_distributions.cpp
sst-register merlin_benchmark_test merlin_benchmark_test_LIBDIR=$(pwd)
sst tests/test_trafficgen_distributions.py
```

Since the outputs are randomized, these are necessarily statistical checks:
each uses a fixed seed and a tolerance wide enough (given the sample size) to
make a spurious failure astronomically unlikely, but not impossible in
principle.

## Known quirks documented (not "fixed") by these tests

- `DiscreteDist` (used for `HotSpot` patterns) is tested against its intended
  semantics -- the `target` bin should get `targetProb` and all others should
  split the remainder evenly -- and **currently fails**: `SSTDiscreteDistribution`'s
  exclusive-prefix-sum lookup actually boosts bin `target + 1` instead of
  `target`, leaves bin `min` essentially unreachable, and can emit a value one
  past `max`. This is a real bug in `DiscreteDist`/`SSTDiscreteDistribution`,
  not a test artifact.
- `NormalDist` and `ExponentialDist` truncate their continuous sample to
  `int`, which biases the sample mean down; the tests account for this.
- `ExponentialDist`'s constructor takes an `int lambda` even though
  production code (`TrafficGen::buildGenerator`) passes it a `float` -- any
  `lambda < 1` truncates to `0`, which `SSTExponentialDistribution` can't
  handle. The test picks `lambda = 1` to avoid that pitfall.
