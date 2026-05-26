#!/usr/bin/env python3
"""Create and save a ceci pipeline DAG diagram for a given run.

Usage
-----
    python scripts/create_pipeline_dag.py <run> [output]

Arguments
---------
<run>
    Name of the run config (no .yaml suffix) under configs/runs/.
[output]
    Output file for the diagram. Default: results/<run>/pipeline_dag.png.
    Use a .dot extension to write a Graphviz dot file instead.

Options
-------
--site YAML
    Site config to use when merging (default: configs/sites/nersc.yaml).
"""

import argparse
import subprocess
import sys
from pathlib import Path

import ceci


def _find_run_yaml(runs_dir: Path, run: str) -> Path:
    p = runs_dir / f"{run}.yaml"
    if p.exists():
        return p
    print(f"error: run config not found for '{run}' in {runs_dir}", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("run", help="Run config name (no extension)")
    parser.add_argument(
        "output",
        nargs="?",
        help="Output file (default: results/<run>/pipeline_dag.png)",
    )
    parser.add_argument(
        "--site",
        default="configs/sites/nersc.yaml",
        help="Site YAML to use when merging configs",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    run_yaml = _find_run_yaml(repo_root / "configs" / "runs", args.run)
    site_yaml = repo_root / args.site

    print(f"Merging configs for run '{args.run}'...")
    result = subprocess.run(
        [
            sys.executable,
            str(repo_root / "scripts" / "merge_configs.py"),
            str(run_yaml),
            str(site_yaml),
        ],
        capture_output=True,
        text=True,
        cwd=str(repo_root),
    )
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)

    merged_yaml = Path(result.stdout.strip())

    output_file = (
        Path(args.output) if args.output else merged_yaml.parent / "pipeline_dag.png"
    )
    output_file.parent.mkdir(parents=True, exist_ok=True)

    print("Building pipeline DAG...")
    pipe_config = ceci.Pipeline.build_config(
        str(merged_yaml), flow_chart=str(output_file)
    )
    pipe = ceci.Pipeline.create(pipe_config)
    pipe.run_jobs()

    print(f"DAG saved to: {output_file}")


if __name__ == "__main__":
    main()
