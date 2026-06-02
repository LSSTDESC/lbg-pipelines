# List of runs

## `template`

A simple dummy template run

## `smoke_test`

Runs the `smoke_test` pipeline.
No external data required; outputs go to `results/smoke_test/`.
Expected runtime: a few seconds.
Use this as a quick sanity check after installing the environment.

## `reduce_flagship_catalog`

A run to reduce the Flagship simulation pixel files and reduce to a standard catalog of positions, magnitudes, and info required for the DESI spectroscopic selector
