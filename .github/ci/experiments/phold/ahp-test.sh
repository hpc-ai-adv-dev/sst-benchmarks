#!/usr/bin/env bash

set -euo pipefail

experiment_path="$1"
sst_version="${2:-}"

if [[ -n "$sst_version" ]]; then
	:
fi

cd "$experiment_path"

echo "=== Registering phold component ==="
sst-register phold phold_LIBDIR=$(pwd)

echo "=== Running reproducible AHP correctness test (2 ranks max in CI) ==="
python3 verify_correctness_ahp.py --launcher mpirun --test base_8x8_1n_2r
