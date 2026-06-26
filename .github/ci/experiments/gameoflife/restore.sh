#!/usr/bin/env bash

set -euo pipefail

experiment_path="$1"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$experiment_path"

echo "=== Registering gameoflife component ==="
sst-register gol gol_LIBDIR=$(pwd)

checkpoint_file="$(find checkpoint -name "*.sstcpt" | sort | head -1)"
if [ -z "$checkpoint_file" ]; then
    echo "No checkpoint file found for gameoflife restore"
    exit 1
fi

echo "=== Restoring gameoflife from checkpoint: $checkpoint_file ==="
sst --load-checkpoint "$checkpoint_file" 2>&1 | tee gol_restore.out
echo "=== Comparing restore output with expected results ==="
diff "$script_dir/gol_restore.good" ./gol_restore.out
