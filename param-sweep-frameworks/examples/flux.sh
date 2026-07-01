#!/usr/bin/env bash

set -euo pipefail

HERE="$(dirname $(realpath -L ${0}))"
PKG_ROOT="$(dirname ${HERE})"
REPO_ROOT="$(dirname ${PKG_ROOT})"

sweep                                                   \
    --launch-method flux-py-api                         \
    --simulation "${REPO_ROOT}/phold/phold_dist.py"     \
    product                                             \
        --node-count-values 1 2 4 8                     \ 
        --ranks-per-node-values 1 2 4 8                 \
        --threads-per-rank-values 8                     \
        --width-values 10                               \
        --height-values 10                              \
        --event-density-values 0.1                      \
        --time-to-run-values 1000                       \
        --ring-size-values 1                            \
        --small-payload-values 8                        \
        --large-payload-values 1024                     \
        --large-event-fraction-values 0                 \
        --imbalance-factor-values 0                     \
        --component-size-values 0

