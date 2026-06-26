#!/usr/bin/env bash

set -euo pipefail

experiment_path="$1"
sst_version_tag="$2"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

case "$sst_version_tag" in
    15.1.2)
        expected_file="$script_dir/pingpong_interleaved.good"
        ;;
    16.0.0|master)
        expected_file="$script_dir/pingpong_master.good"
        ;;
    *)
        echo "Unsupported SST version tag for pingpong test: $sst_version_tag"
        exit 1
        ;;
esac

cd "$experiment_path"

echo "=== Registering pingpong component ==="
sst-register pingpong pingpong_LIBDIR=$(pwd)
echo "=== Running pingpong simulation ==="
sst pingpong.py -- --corners --verbose | tee pingpong_sim.out
echo "=== Comparing output with expected results ==="
diff "$expected_file" ./pingpong_sim.out
