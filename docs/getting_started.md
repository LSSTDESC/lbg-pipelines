# Getting Started

## Environment setup

First create a subdirectory for yourself in the LBG users space:
```bash
mkdir /global/cfs/cdirs/lsst/groups/WLSS/LBG/users/$USER
```

Next setup the `lbg-env` tool by adding the following to your `~/.bashrc.ext` (or `~/.zshrc.ext`):

```bash
source /global/common/software/m1727/groups/WLSS/LBG/lbg-env/scripts/setup_lbg_env.sh
```

Then either start a new shell or re-source your `~/.bashrc.ext`/`~/.zshrc.ext` to pick up the change.

You now have access to the `lbg-env` tool.
This tool provides a number of useful abilities, which you can read about by either running `lbg-env help` or going to the [lbg-env docs](https://github.com/LSSTDESC/lbg-env).
For most people, however, typical usage will likely be

```bash
lbgu        # go to your LBG user directory
lbg-env     # activate the latest LBG python environment
```

You may also wish to run `lbg-env setup-jupyter` to install a Jupyter kernel for the activated environment which you can use in the online portal.

## Repository setup

Go to your subdirectory in the LBG users space and clone this repo:

```bash
lbgu
git clone git@github.com:LSSTDESC/lbg-pipelines.git
```

Finally you can install the pre-commit hooks:

```bash
pre-commit install
```

Now you're ready to work!

## Running a pipeline

The simplest way to run a pipeline is with `run_debug.sh`, which requests a
short debug allocation automatically and runs the pipeline inside it:

```bash
bash scripts/run_debug.sh <run>
```

where `<run>` is the name of a file (without the `.yaml` extension) under `configs/runs/`.
The pipeline(s) to execute are specified by the `pipelines:` key inside that run config.
See [Stages, Pipelines, and Runs](stages_pipelines_runs.md) for more info.

## Contributing

To contribute to this project, see the instructions in [Contributing](contributing.md)
