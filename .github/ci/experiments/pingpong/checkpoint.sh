#!/usr/bin/env bash

set -euo pipefail

experiment_path="$1"
sst_version_tag="$2"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

case "$sst_version_tag" in
    15.1.2)
        expected_file="$script_dir/pingpong_checkpoint_interleaved.good"
        ;;
    16.0.0|master)
        expected_file="$script_dir/pingpong_checkpoint_master.good"
        ;;
    *)
        echo "Unsupported SST version tag for pingpong checkpoint: $sst_version_tag"
        exit 1
        ;;
esac

cd "$experiment_path"

echo "=== Registering pingpong component ==="
sst-register pingpong pingpong_LIBDIR=$(pwd)
echo "=== Running pingpong simulation with checkpointing ==="
sst --checkpoint-sim-period=50ps pingpong.py -- --corners --verbose 2>&1 | grep -v "Real CPU time" | tee pingpong_checkpoint.out
echo "=== Comparing checkpoint output with expected results ==="
diff "$expected_file" ./pingpong_checkpoint.out
