#!/usr/bin/env bash

set -euo pipefail

experiment_path="$1"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$experiment_path"

echo "=== Registering phold component ==="
sst-register phold phold_LIBDIR=$(pwd)
echo "=== Running phold simulation ==="
sst phold_dist.py -- --verbose 1 2>&1 | tee phold_sim.out
echo "=== Comparing output with expected results ==="
diff "$script_dir/phold.good" ./phold_sim.out
