import subprocess
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).parent.parent


def test_smoke_test_pipeline(tmp_path):
    """Run the smoke_test pipeline end-to-end and check the output."""
    outputs = tmp_path / "outputs"
    logs = tmp_path / "logs"

    result = subprocess.run(
        [
            "bash",
            "scripts/run_interactive.sh",
            "smoke_test",
            f"output_dir={outputs}",
            f"log_dir={logs}",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Pipeline failed:\n"
        f"--- stdout ---\n{result.stdout}\n"
        f"--- stderr ---\n{result.stderr}"
    )

    final = outputs / "smoke_final.pq"
    assert final.exists(), "smoke_final.pq was not written"

    df = pd.read_parquet(final)
    assert len(df) > 0, "Output catalog is empty"
    assert "i" in df.columns, "Missing i-band column"
    assert (df["i"] <= 25.3).all(), "Depth cut was not applied correctly"
