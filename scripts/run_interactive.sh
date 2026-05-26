#!/bin/bash
# Run a pipeline inside an existing interactive allocation.
# Useful for development — you can watch the output live and rerun quickly.
#
# Usage:
#   bash scripts/run_interactive.sh <run> [ceci-args...]
#
# You must already have an allocation. To get one:
#   salloc --nodes 4 --time 02:00:00 --account m1727 --qos interactive --constraint cpu

# shellcheck source=_common.sh
source "$(dirname "$0")/_common.sh"

MERGED=$(python3 scripts/merge_configs.py "$RUN_YAML" configs/sites/nersc.yaml)
ceci "$MERGED" "${@:2}"
