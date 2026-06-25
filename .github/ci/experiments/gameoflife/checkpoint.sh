#!/usr/bin/env bash

set -euo pipefail

experiment_path="$1"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$experiment_path"

echo "=== Registering gameoflife component ==="
sst-register gol gol_LIBDIR=$(pwd)
echo "=== Running gameoflife simulation with checkpointing ==="
sst --checkpoint-sim-period=1.5s gol.py -- --verbose --seed 42 2>&1 | grep -v "Real CPU time" | tee gol_checkpoint.out
echo "=== Comparing checkpoint output with expected results ==="
diff "$script_dir/gol_checkpoint.good" ./gol_checkpoint.out
