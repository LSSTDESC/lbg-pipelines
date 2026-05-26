import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
RUNS_DIR = REPO_ROOT / "configs" / "runs"


def _run_names():
    """Find all run yamls, excluding the template"""
    return [p.stem for p in sorted(RUNS_DIR.glob("*.yaml")) if p.stem != "template"]


@pytest.mark.parametrize("run", _run_names())
def test_dry_run(run):
    """Test that dry run of all run yamls succeed."""
    result = subprocess.run(
        ["bash", "scripts/run_interactive.sh", run, "--dry-run"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Dry run failed for '{run}':\n"
        f"--- stdout ---\n{result.stdout}\n"
        f"--- stderr ---\n{result.stderr}"
    )
