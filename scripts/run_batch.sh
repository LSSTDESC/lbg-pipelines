#!/bin/bash
# Submit a pipeline as a Slurm batch job.
#
# Unlike run_interactive.sh and run_debug.sh, which require you to be present
# at a terminal, this script queues the job and runs it whenever a node
# becomes available — you can log out and come back later to check the results.
#
# Usage:
#   bash scripts/run_batch.sh <run> [--qos Q] [--time T] [--nodes N] [ceci-args...]
#
# The --qos, --time, and --nodes flags override the defaults below.
# Any remaining arguments are passed through to ceci.
#
# Examples:
#   bash scripts/run_batch.sh my_run
#   bash scripts/run_batch.sh my_run --qos debug --time 0:20:00
#   bash scripts/run_batch.sh my_run --time 8:00:00 --nodes 2
#
# Slurm log files are written to the log_dir specified in the run config
# (e.g. configs/runs/<run>.yaml), with filenames slurm-<jobid>.out/err.

# ---- Default Slurm options ----
# These are the defaults used when the corresponding flag is not supplied.
# You can also change them here permanently if your runs consistently need
# different values.

# Project account to charge.
#SBATCH -A m1727

# Request CPU nodes on Perlmutter (as opposed to GPU nodes).
#SBATCH -C cpu

# Queue to submit to (override with --qos):
#   regular  — standard queue; jobs can run for up to 24 hours.
#   debug    — highest priority, but limited to 30 minutes and 2 nodes. Good
#              for a quick check that the job launches correctly.
#   premium  — higher priority than regular; costs more allocation units.
#   low      — lowest priority; use when you can afford to wait.
#SBATCH -q regular

# Maximum wall-clock time (override with --time). The job is killed if it runs
# longer than this. Format: hours:minutes:seconds.
#SBATCH -t 2:00:00

# Number of compute nodes (override with --nodes). Each Perlmutter CPU node
# has 128 cores. Independent pipeline stages run in parallel — one per core —
# so a single node is enough for most pipelines.
#SBATCH -N 1

# Fallback log paths — only used if the self-submission block below cannot
# read log_dir from the run config. %j is replaced by Slurm with the job ID.
# The self-submission block overrides these with --output/--error flags.
#SBATCH -o outputs/logs/slurm-%j.out
#SBATCH -e outputs/logs/slurm-%j.err
# Append rather than truncate if a log file already exists (e.g. on resume).
#SBATCH --open-mode=append

# ---- Self-submission ----
# When run outside a Slurm job, parse any --qos/--time/--nodes flags, then
# re-submit this script via sbatch. This means you never need to prefix the
# command with sbatch yourself.

# SLURM_JOB_ID is only set inside a running Slurm job. When it's absent we
# know we're on a login node and need to submit rather than execute.
if [[ -z "${SLURM_JOB_ID:-}" ]]; then
    RUN=${1:?Usage: run_batch.sh <run> [--qos Q] [--time T] [--nodes N] [ceci-args...]}
    SBATCH_OVERRIDES=()   # flags to pass to sbatch itself (--qos, --time, --nodes)
    PASS_ARGS=("$1")      # args to re-pass to this script when it runs inside Slurm
    shift                 # consume the run name; remaining args are flags or ceci args
    # Sort remaining args: Slurm overrides go into SBATCH_OVERRIDES; everything
    # else (ceci pass-through args) stays in PASS_ARGS.
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --qos)     SBATCH_OVERRIDES+=(--qos="$2");    shift 2 ;;
            --qos=*)   SBATCH_OVERRIDES+=("$1");           shift   ;;
            --time)    SBATCH_OVERRIDES+=(--time="$2");   shift 2 ;;
            --time=*)  SBATCH_OVERRIDES+=("$1");           shift   ;;
            --nodes)   SBATCH_OVERRIDES+=(--nodes="$2");  shift 2 ;;
            --nodes=*) SBATCH_OVERRIDES+=("$1");           shift   ;;
            *)         PASS_ARGS+=("$1");                  shift   ;;
        esac
    done
    # Resolve the repo root from the script's own location so --chdir works
    # regardless of which directory the user invokes this script from.
    REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
    # Read log_dir from the run config YAML and expand any env vars (e.g. $LBG_DIR).
    # Falls back to outputs/logs if log_dir is not set.
    LOG_DIR=$(python3 -c "
import yaml, os, sys
with open('$REPO_ROOT/configs/runs/$RUN.yaml') as f:
    d = yaml.safe_load(f)
print(os.path.expandvars(d.get('log_dir', 'outputs/logs')))
")
    mkdir -p "$LOG_DIR"
    # --chdir sets the working directory for the job to the repo root.
    # --output/--error override the #SBATCH -o/-e defaults above so logs land
    # in the run-specific directory. exec replaces this shell with sbatch so
    # the exit code comes directly from sbatch.
    exec sbatch --chdir="$REPO_ROOT" \
        --output="$LOG_DIR/slurm-%j.out" \
        --error="$LOG_DIR/slurm-%j.err" \
        "${SBATCH_OVERRIDES[@]}" "$0" "${PASS_ARGS[@]}"
fi

# ---- Pipeline execution (runs inside the Slurm job) ----
# sbatch copies this script to a Slurm temp dir, so dirname "$0" would not
# point to the repo. Source _common.sh by CWD-relative path (safe because
# --chdir set CWD to the repo root) and pass --no-cd to skip the cd step.
# shellcheck source=_common.sh
source "scripts/_common.sh" --no-cd "$@"

MERGED=$(python3 scripts/merge_configs.py "$RUN_YAML" configs/sites/nersc.yaml)
ceci "$MERGED" "${@:2}"
