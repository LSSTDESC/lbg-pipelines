# Scripts

This page documents the scripts in the `scripts/` directory.

## Background: how pipeline jobs work at NERSC

NERSC is a shared supercomputer facility.
The machine you log into (the *login node*) is a shared gateway — it is not for heavy computation.
Actual computation happens on *compute nodes*, which are powerful dedicated machines you request through a job scheduler called **Slurm**.

There are two ways to get compute nodes:

- **Interactive allocation (`salloc`)** — Slurm reserves nodes for you immediately and gives you a shell on them.
You can run commands, watch output live, and rerun things quickly.
The nodes are released when you exit the shell or your time limit expires.
This is good for development and debugging.

- **Batch job (`sbatch`)** — You write a script describing what to run, and Slurm queues it.
The job runs whenever nodes become available — you do not need to be logged in.
Results appear in log files when it finishes.
This is the right approach for production runs that take hours.

When submitting a batch job, you choose a **queue** (also called a QOS — Quality of Service) that controls priority and limits:

| Queue | Priority | Max time | Max nodes | When to use |
|---|---|---|---|---|
| `debug` | Highest | 30 min | 2 | Testing that a job launches correctly |
| `regular` | Normal | 24 hours | many | Standard production runs |
| `premium` | High | 24 hours | many | When turnaround time matters; costs extra |
| `low` | Low | 24 hours | many | When you can afford to wait; cheapest |

Once a pipeline is running on compute nodes, it is managed by **ceci**, which reads the pipeline definition and executes stages in dependency order.
Stages with no dependencies between them run **in parallel** — each as a separate process on its own CPU core, up to 128 at a time on a single Perlmutter node.

---

## Run scripts

There are three scripts for launching pipelines, each targeting a different workflow:

| Script | How nodes are obtained | Good for |
|---|---|---|
| `run_debug.sh` | Requests a debug allocation automatically | Quick smoke tests during development |
| `run_interactive.sh` | Uses an allocation you already have | Active development and debugging; rerunning quickly |
| `run_batch.sh` | Submits to the queue via `sbatch` | Production runs; no need to stay logged in |

All three require the `lbg-env` environment to be active in your current shell:

```bash
lbg-env
```

Then pass the name of a run config (the filename without `.yaml` under `configs/runs/`):

```bash
bash scripts/run_debug.sh <run>
bash scripts/run_interactive.sh <run>
bash scripts/run_batch.sh <run>
```

---

### `run_debug.sh` — quick test runs

**Use this when:** you want to test that a pipeline runs correctly without manually requesting nodes.

This script calls `salloc` for you, requesting a 2-node debug allocation (up to 30 minutes), runs the pipeline, and releases the nodes automatically when it finishes.
The debug queue is high-priority, so you typically get nodes within a minute or two.

```bash
bash scripts/run_debug.sh <run>
```

**Limitations:** 30-minute wall-clock limit; maximum 2 nodes.
Not suitable for long production runs.

---

### `run_interactive.sh` — development with an existing allocation

**Use this when:** you already have a Slurm allocation (via `salloc`) and want to run or rerun a pipeline inside it.

Because you already have the nodes, there is no queuing delay between runs.
This makes it convenient when you are iterating — fixing a bug, rerunning with `resume: True`, or testing different configurations.

To get an allocation first:
```bash
salloc --nodes 1 --time 02:00:00 --account m1727 --qos interactive --constraint cpu
```

Then, inside that shell:
```bash
bash scripts/run_interactive.sh <run>
```

**Limitations:** you must stay logged in; the nodes are released when your session ends.

---

### `run_batch.sh` — production runs

**Use this when:** the pipeline will take a long time, or you do not want to stay logged in while it runs.

Run the script directly — it submits itself to the queue automatically:

```bash
bash scripts/run_batch.sh <run>
```

Slurm runs the job on one compute node when resources are available, and writes all output to log files under `outputs/logs/`.
You can check on the job with `squeue -u $USER` and cancel it with `scancel <jobid>`.

**Overriding defaults on the command line:**

The queue, time limit, and node count can be set with flags.
Anything else is passed through to ceci.

```bash
bash scripts/run_batch.sh <run> --qos debug --time 0:20:00   # quick test
bash scripts/run_batch.sh <run> --time 8:00:00               # longer time limit
bash scripts/run_batch.sh <run> --nodes 2                    # two nodes
```

| Flag | Default | What it controls |
|---|---|---|
| `--qos` | `regular` | Queue — see the table above |
| `--time` | `4:00:00` | Wall-clock time limit (hours:minutes:seconds) |
| `--nodes` | `1` | Number of compute nodes |

**How parallelism works:** the pipeline runner looks at the stage dependency graph and launches all stages whose inputs are ready at the same time, each as a separate process on its own CPU core.
A single Perlmutter CPU node has 128 cores, so up to 128 independent stages can run simultaneously.
For most pipelines — which have far fewer than 128 independent stages — one node is sufficient.

**Limitations:** you cannot watch output live (check the log files instead); the job may wait in the queue before starting.

---

## Utility scripts

### `create_pipeline_dag.py`

Renders the pipeline stage dependency graph (DAG) as a PNG or Graphviz `.dot` file.
Useful for visualizing which stages run in parallel and how data flows between them.

```bash
python scripts/create_pipeline_dag.py <run>
python scripts/create_pipeline_dag.py <run> results/<run>/dag.png
python scripts/create_pipeline_dag.py <run> results/<run>/dag.dot  # Graphviz source
```

### `generate_test_certificate.sh`

Runs the full test suite (`pytest`) and prints a signed certificate confirming all tests passed.
Run this before opening a pull request.

```bash
bash scripts/generate_test_certificate.sh
```

### `merge_configs.py`

Merges a run config, one or more pipeline configs, and a site config into a single temporary YAML file for ceci.
The run scripts call this automatically; you should not normally need to run it directly.
