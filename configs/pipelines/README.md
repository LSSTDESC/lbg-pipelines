# List of pipelines

## `template`

A simple dummy template pipeline, with minimal `pipeline.yaml` and `config.yaml` files

## `smoke_test`

A self-contained smoke-test pipeline.
Generates a tiny synthetic galaxy catalog (no external data needed) and runs it
through LSST Y1 photometric errors and an i-band depth cut.
Use this to verify that the environment and pipeline machinery are installed
correctly.

## `reduce_flagship_catalog`

A simple pipeline that loads the Flagship simulation pixel files and reduces to a standard catalog of positions, magnitudes, and info required for the DESI spectroscopic selector

## `select_lbg_color_cuts`

A simple pipeline that loads the example `TXPipe` photometry catalog and applies color cuts to select LBGs, producing a file which labels each source according to the dropout sample to which they belong (if any)
