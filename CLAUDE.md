# lbg-pipelines — Claude Code guidance

## What this repo is

Pipelines and analyses for the DESC LBG Topical Team, hosted at NERSC.
Framework: [ceci](https://ceci.readthedocs.io) / [TXPipe](https://txpipe.readthedocs.io) — pipelines are DAGs of stages defined in YAML.

## Environment

Activate the shared Python environment with:
```bash
lbg-env   # requires setup_lbg_env.sh sourced in ~/.bashrc.ext or ~/.zshrc.ext
```

The `lbg` command is a shortcut to the repo root.

## Running a pipeline

The run scripts require `lbg-env` to be activated in the **current shell** so the
environment (PATH, Python) is inherited by the compute node via `salloc`.
Always activate before running any script:

```bash
source /global/common/software/m1727/groups/WLSS/LBG/lbg-env/scripts/setup_lbg_env.sh
lbg-env
```

Then:

```bash
bash scripts/run_debug.sh    <run>   # quick test
bash scripts/run_interactive.sh <run> # inside salloc
sbatch scripts/run_batch.sh  <run>   # production
```

`<run>` = filename (no `.yaml`) under `configs/runs/`.
The pipeline(s) to run are specified by the `pipelines:` key inside the run config.
ceci must be invoked from the repo root (the scripts handle this).

## ceci version notes

The installed ceci version accepts only a **single** pipeline YAML (plus `key=value` overrides).
The run scripts work around this by merging all pipeline YAMLs, the run config, and the site config into a temp file before calling ceci.
`merge_configs.py` reads the `pipelines:` key from the run config, loads each named pipeline from `configs/pipelines/<name>/pipeline.yaml`, and merges their `modules`, `stages`, and per-stage configs.
Use `modules:` (space-separated, top-level key) to import stage modules — this is what registers stage classes with ceci.
`python_paths:` is not needed because ceci adds CWD to `sys.path` automatically.

## Adding a new pipeline checklist

1. `cp -r configs/pipelines/template configs/pipelines/<name>`
2. Edit `pipeline.yaml` (stages) and `config.yaml` (params).
3. Create `configs/runs/<run>.yaml`.
4. Add an entry to `configs/pipelines/README.md` and `configs/runs/README.md`.
5. Update `docs/list_of_pipelines.md` (auto-includes from `configs/pipelines/README.md`).
6. Verify with `bash scripts/generate_test_certificate.sh`.

## Git / contribution conventions

- Branch naming: `<yourname>/<topic>` (e.g. `jfcrenshaw/mock-desi`).
- No direct pushes to `main` — all changes via PR with ≥1 review.
- Open an issue before starting a new pipeline or analysis.
- Strip notebook outputs before committing (`nbstripout` pre-commit hook handles this).
- Linting: `ruff check --fix . && ruff format .` (line length 88, Python 3.11+).

## Slurm / NERSC

- CPU account: `m1727`; GPU account: `m1727_g`.
- Constraint: `cpu` (Perlmutter Milan nodes, 128 cores each).
- Outputs to `results/<run>/outputs`, logs to `results/<run>/logs` — neither tracked in git.
- Big I/O scratch: `$PSCRATCH`; persistent output: CFS under the shared LBG group directory.

## Pipelines in this repo

See `configs/pipelines/README.md`.
