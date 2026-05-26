# Stages, Pipelines, and Runs

[List of Stages](api.md){ .md-button }
[List of Pipelines](list_of_pipelines.md){ .md-button }
[List of Runs](list_of_runs.md){ .md-button }

Our analyses are organized in terms of "runs" that connect different input data to "pipelines" that assemble many "stages" that each perform a small part of the analysis.
I.e.,

- **Stages** perform a relatively small, self-contained piece of a larger analysis
- **Pipelines** connect many stages together into a coherent analysis
- **Runs** execute a specific pipeline on a specific set of input data

For example, a pipeline that estimates photometric redshifts for a catalog might be composed of individual stages:

- **Stage 1:** Split input spectroscopic catalog into training and test sets
- **Stage 2:** Train photo-z estimator on training set
- **Stage 3:** Estimate photo-z's for the test set
- **Stage 4:** Evaluate photo-z performance on the test set
- **Stage 5:** Estimate photo-z's for the target photometric catalog

Note that stages 3 and 5 that perform photo-$z$ estimation might really be the same underlying stage, just applied to different input catalogs (the spectroscopic test set and the target photometric catalog).

We might then use this pipeline in two different runs:

- **Run 1:** Execute the pipeline on simulated data
- **Run 2:** Execute the pipeline on real data

## Stages

Stages perform a relatively small, self-contained piece of a larger analysis.

Custom stages for our LBG analyses are defined in the `lbg_stages/` directory.
Each is a [`ceci`](https://github.com/LSSTDESC/ceci) pipeline stage.
But we can also use a large library of pre-defined stages from the `TXPipe` and `RAIL` packages.

[`TXPipe`](https://txpipe.readthedocs.io/en/latest/) contains lots of stages for large-scale structure analyses, but is largely focused on cosmic shear analyses, which is not relevant to our LBG work.
For this reason, we may define custom LBG stages that inherit from or are very similar to existing `TXPipe` stages, but we should always check first whether a stage in `TXPipe` already meets our needs.
When in doubt, you can ask in the `#desc-lbg` and `#desc-txpipe` Slack channels.

[`RAIL`](https://rail-hub.readthedocs.io/en/latest/index.html#) contains lots of stages for simulating catalogs, performing photo-$z$ estimation, and evaluating the results.
It is likely that any photo-$z$ related stages can be used directly from `RAIL`, but it may be possible that we need to define some custom stages on our side.
When in doubt, you can ask in the `#desc-lbg` and `#desc-pz-rail` Slack channels.

Note that custom stages we prototype here in the `lbg-pipelines` repo might eventually be migrated into `TXPipe` and `RAIL` if they are deemed widely useful outside the needs of the LBG TT.

## Pipelines

Pipelines connect many stages together into a coherent analysis.

Pipelines are defined via `yaml` files in the `configs/pipelines/` directory.
Each new pipeline receives its own subdirectory which contains a `pipeline.yaml` file and a `config.yaml` file.

The `pipeline.yaml` file lists the stages that comprise the pipeline.
`ceci` will read this file, determine the inputs/outputs of each stage, and build a directed acyclic graph (DAG) for the pipeline that determines what order to run all the stages in and how to connect the relevant inputs and outputs.

Here is a template `pipeline.yaml`:

```yaml
--8<-- "configs/pipelines/template/pipeline.yaml"
```

The `config.yaml` sets configuration parameters for each stage in the pipeline.

Here is a template `config.yaml`:
```yaml
--8<-- "configs/pipelines/template/config.yaml"
```

The pipeline config files (both `pipeline.yaml` and `config.yaml`) are meant to be as agnostic as possible to the specific catalogs being analyzed so that the same pipelines can be run on different inputs simply by writing a new *run* config.

## Runs

Runs are defined via `yaml` files in the `configs/runs/` directory, with each run receiving a `yaml` file named `<pipeline>_<catalog>`.

Here is a template run config:
```yaml
--8<-- "configs/runs/template.yaml"
```

Runs can be executed using the scripts provided in the `scripts/` directory.
Each takes a run name as its first argument; the pipeline(s) to execute are read from the `pipelines:` key in the run config.
Any additional arguments are forwarded directly to `ceci`.

**Quick test** (requests a 2-node debug allocation automatically):

```bash
bash scripts/run_debug.sh <run> [ceci-args...]
```

**Interactive** (use when you already have an `salloc` allocation):

```bash
bash scripts/run_interactive.sh <run> [ceci-args...]
```

**Batch job** (queues a Slurm job; you do not need to stay logged in):

```bash
sbatch scripts/run_batch.sh <run> [ceci-args...]
```

In all cases `<run>` is the name of a `.yaml` file (without the extension) under `configs/runs/`.
