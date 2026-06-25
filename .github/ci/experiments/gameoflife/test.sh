#!/usr/bin/env bash

set -euo pipefail

experiment_path="$1"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$experiment_path"

echo "=== Registering gameoflife component ==="
sst-register gol gol_LIBDIR=$(pwd)
echo "=== Running gameoflife simulation ==="
sst gol.py -- --verbose --seed 42 | tee gol_sim.out
echo "=== Comparing output with expected results ==="
diff "$script_dir/gol.good" ./gol_sim.out
