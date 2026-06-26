#!/usr/bin/env bash

set -euo pipefail

experiment_path="$1"
sst_version_tag="$2"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

case "$sst_version_tag" in
    15.1.2)
        expected_file="$script_dir/pingpong_restore_interleaved.good"
        ;;
    16.0.0|master)
        expected_file="$script_dir/pingpong_restore_master.good"
        ;;
    *)
        echo "Unsupported SST version tag for pingpong restore: $sst_version_tag"
        exit 1
        ;;
esac

cd "$experiment_path"

echo "=== Registering pingpong component ==="
sst-register pingpong pingpong_LIBDIR=$(pwd)

checkpoint_file="$(find checkpoint -name "*.sstcpt" | sort | head -1)"
if [ -z "$checkpoint_file" ]; then
    echo "No checkpoint file found for pingpong restore"
    exit 1
fi

echo "=== Restoring pingpong from checkpoint: $checkpoint_file ==="
sst --load-checkpoint "$checkpoint_file" 2>&1 | tee pingpong_restore.out
echo "=== Comparing restore output with expected results ==="
diff "$expected_file" ./pingpong_restore.out
