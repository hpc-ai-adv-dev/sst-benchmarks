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

echo "=== Running baseline phold simulation ==="
sst phold_dist.py -- --verbose 1 2>&1 | tee phold_sim.out

echo "=== Running AHP phold simulation ==="
sst phold_dist_ahp.py -- --verbose 1 2>&1 | tee phold_ahp_sim.out

echo "=== Comparing recvCount output between baseline and AHP ==="
grep -E '^[0-9]+,[0-9]+:[0-9]+$' phold_sim.out > phold_recvcounts.out
grep -E '^[0-9]+,[0-9]+:[0-9]+$' phold_ahp_sim.out > phold_ahp_recvcounts.out
diff phold_recvcounts.out phold_ahp_recvcounts.out
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

echo "=== Running baseline phold simulation ==="
sst phold_dist.py -- --verbose 1 2>&1 | tee phold_sim.out

echo "=== Running AHP phold simulation ==="
sst phold_dist_ahp.py -- --verbose 1 2>&1 | tee phold_ahp_sim.out

echo "=== Comparing recvCount output between baseline and AHP ==="
grep -E '^[0-9]+,[0-9]+:[0-9]+$' phold_sim.out > phold_recvcounts.out
grep -E '^[0-9]+,[0-9]+:[0-9]+$' phold_ahp_sim.out > phold_ahp_recvcounts.out
diff phold_recvcounts.out phold_ahp_recvcounts.out
