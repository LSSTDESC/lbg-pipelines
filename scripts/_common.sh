# _common.sh — sourced by the run_*.sh scripts. Do not execute this file directly.
#
# Requires lbg-env to be configured in ~/.bashrc.ext or ~/.zshrc.ext (see README).
#
# Flags (must come before the run name):
#   --no-cd   Skip the cd-to-repo-root step. Use when the caller has already
#             set CWD to the repo root (e.g. run_batch.sh via sbatch --chdir).

# Fail immediately on errors, unset variables, or broken pipes.
set -euo pipefail

# Use the calling script's name in error messages rather than "_common.sh".
_SCRIPT=$(basename "${BASH_SOURCE[1]}")

_NO_CD=0
if [[ "${1:-}" == "--no-cd" ]]; then
    _NO_CD=1
    shift
fi

# One argument: run name.
RUN=${1:?Usage: $_SCRIPT <run>}

if [[ $_NO_CD -eq 0 ]]; then
    # ceci must be run from the repo root so that relative paths in the pipeline
    # YAML files resolve correctly.
    cd "$(cd "$(dirname "${BASH_SOURCE[1]}")" && pwd)/.."
fi

RUN_YAML=configs/runs/$RUN.yaml

[[ -f "$RUN_YAML" ]] || { echo "$_SCRIPT: run config not found: $RUN_YAML" >&2; exit 1; }
