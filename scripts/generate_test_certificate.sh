#!/usr/bin/env bash
# Run the test suite and, on success, print a test certificate.
set -euo pipefail

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."

echo "Running tests..."
if ! python -m pytest tests/; then
    echo "" >&2
    echo "Tests failed — no certificate generated." >&2
    exit 1
fi

branch=$(git branch --show-current)
hash=$(git rev-parse --short HEAD)
timestamp=$(date -u "+%Y-%m-%d %H:%M UTC")

echo ""
echo "Test Certificate ${timestamp}"
echo "on branch: ${branch} ${hash}"
if [[ "${CONDA_DEFAULT_ENV:-}" == lbg-python-* ]]; then
    _lbg_version="${CONDA_DEFAULT_ENV#lbg-python-}"
else
    _lbg_version=$(cat "${LBG_ENV_DIR}/versions/CURRENT")
fi
cat "${LBG_ENV_DIR}/versions/${_lbg_version}/description"
