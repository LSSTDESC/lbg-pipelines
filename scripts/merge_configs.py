#!/usr/bin/env python3
"""Merge run, pipeline(s), and site YAML configs into a single ceci input file.

The run config must contain a ``pipelines`` key giving the pipeline name(s) to
load from ``configs/pipelines/<name>/pipeline.yaml``.  When multiple pipelines
are listed their ``modules``, ``stages``, and per-stage configs are merged.

Usage
-----
    python scripts/merge_configs.py <run_yaml> <site_yaml>

Writes
------
    results/<run>/pipeline.yaml   merged config passed to ceci
    results/<run>/config.yaml     merged per-stage config file

Prints the path to the merged YAML so callers can do:
    MERGED=$(python scripts/merge_configs.py ...)
    ceci "$MERGED"
"""

import os
import sys
from pathlib import Path

import yaml


def load_yaml(path):
    with open(path) as fh:
        return yaml.safe_load(os.path.expandvars(fh.read())) or {}


def merge_pipelines(pipeline_names, pipelines_dir):
    """Load and merge one or more pipeline YAMLs and their stage config files.

    Returns
    -------
    pipeline_data : dict
        Merged ``modules`` (space-separated str) and ``stages`` (list).
    stage_configs : dict
        Merged per-stage config dicts, keyed by stage name.
    """
    all_modules = []
    all_stages = []
    all_stage_configs = {}

    for name in pipeline_names:
        pipeline_path = pipelines_dir / name / "pipeline.yaml"
        if not pipeline_path.exists():
            print(f"error: pipeline config not found: {pipeline_path}", file=sys.stderr)
            sys.exit(1)

        pipeline = load_yaml(pipeline_path)

        for module in pipeline.get("modules", "").split():
            if module not in all_modules:
                all_modules.append(module)

        for stage in pipeline.get("stages", []):
            stage_name = stage.get("name", stage)
            if stage_name in {s.get("name", s) for s in all_stages}:
                print(
                    f"error: stage '{stage_name}' appears in multiple pipelines",
                    file=sys.stderr,
                )
                sys.exit(1)
            all_stages.append(stage)

        config_path = pipeline.get("config")
        if config_path:
            all_stage_configs.update(load_yaml(config_path))

    return {"modules": " ".join(all_modules), "stages": all_stages}, all_stage_configs


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    run_yaml, site_yaml = sys.argv[1], sys.argv[2]

    run_data = load_yaml(run_yaml)

    raw_pipelines = run_data.pop("pipelines", None)
    if raw_pipelines is None:
        print("error: run config must contain a 'pipelines' key", file=sys.stderr)
        sys.exit(1)
    pipeline_names = (
        [raw_pipelines] if isinstance(raw_pipelines, str) else list(raw_pipelines)
    )

    pipelines_dir = Path("configs/pipelines")
    pipeline_data, stage_configs = merge_pipelines(pipeline_names, pipelines_dir)

    # Pipeline data first, then run data overrides it, then site data overrides that.
    merged = {}
    merged.update(pipeline_data)
    merged.update(run_data)
    merged.update(load_yaml(site_yaml))

    output_dir = Path(merged.get("output_dir", "results/output"))
    run_dir = output_dir.parent
    run_dir.mkdir(parents=True, exist_ok=True)

    config_path = run_dir / "config.yaml"
    with open(config_path, "w") as fh:
        yaml.dump(stage_configs, fh, default_flow_style=False, sort_keys=False)
    merged["config"] = str(config_path)

    merged_path = run_dir / "pipeline.yaml"
    with open(merged_path, "w") as fh:
        yaml.dump(merged, fh, default_flow_style=False, sort_keys=False)

    print(merged_path)


if __name__ == "__main__":
    main()
