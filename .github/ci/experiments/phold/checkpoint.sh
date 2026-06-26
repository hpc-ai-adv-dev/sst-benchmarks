#!/usr/bin/env bash

set -euo pipefail

experiment_path="$1"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$experiment_path"

echo "=== Registering phold component ==="
sst-register phold phold_LIBDIR=$(pwd)
echo "=== Running phold simulation with checkpointing ==="
sst --checkpoint-sim-period=250ns phold_dist.py -- --verbose 1 2>&1 | grep -v "Real CPU time" | tee phold_checkpoint.out
echo "=== Comparing checkpoint output with expected results ==="
diff "$script_dir/phold_checkpoint.good" ./phold_checkpoint.out
