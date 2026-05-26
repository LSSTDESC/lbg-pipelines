# Contributing


## Workflow

This describes the workflow for contributing new pipelines, stages, bugfixes, etc. to the LBG pipelines.
This workflow is designed to help us stay informed, collaborate, and ensure the high quality of our code and documentation.

1. **Open or choose an issue**.

      - If you have a new idea you would like to contribute to the pipelines, open a new issue.
      Make sure you give it a short, descriptive title, and that you describe the goal of the new work and your proposed implementation plan.
      Feel free to request feedback!

      - You can also choose an existing issue to work on.
      Issues labeled "Not Started" are particularly good options.
      If you're new to the LBG pipelines, we recommend you select an issue labeled "Good First Issue".
      If none exist, feel free to reach out to John Franklin Crenshaw and/or Tanveer Karim on Slack, and they will help you find a place to start.

2. **Create a branch** from `main` that contains the ticket number and a short description: `issue-#/short-description`.
   Once you create a branch for an issue and start working on it, please do the following in the sidebar on the issue's Github page:

      1. Assign yourself to the issue
      2. Apply the "In Progress" label
      3. Link your branch to the issue (near the bottom of the sidebar under the "development" heading). If you can't find your branch in the dropdown menu, it's likely you haven't yet pushed your branch to Github.

3. **Make your changes**.
See the sections below for conventions.
You should also read the page [Stages, Pipelines, Runs](stages_pipelines_runs.md).
If you add a new pipeline or run, please add a description to the [list of pipelines](https://github.com/LSSTDESC/lbg-pipelines/blob/main/configs/pipelines/README.md) and/or [list of runs](https://github.com/LSSTDESC/lbg-pipelines/blob/main/configs/runs/README.md).

4. **Open a pull request**.
Direct pushes to `main` are disabled, so all changes must go through a pull request (PR).

5. **Request a review**.
We require that all PRs receive a review before they are merged.
You can request a specific reviewer in the sidebar on the PR's Github page, or you can post a message in `#desc-lbg` on Slack to make a more general request.
You should always feel free to request a review from John Franklin!


## Code conventions

## Python code

We use [ruff](https://docs.astral.sh/ruff/) for linting and formatting (enforced by pre-commit):

```bash
ruff check --fix .   # lint
ruff format .        # format
```

## Notebook conventions

- Strip outputs before committing (handled by the `nbstripout` pre-commit hook).
- Name notebooks descriptively, e.g. `<topic>_<data_version>.ipynb`.

## Documentation

The docs site is built from the `docs/` directory with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/).
To preview locally:

```bash
lbg-env
conda activate docs
mkdocs serve
```

Updates to `docs/` on `main` are deployed automatically to GitHub Pages via the CI workflow.

## Questions

Post in the LBG topical team Slack channel (`#desc-lbg`) or open a GitHub issue.
