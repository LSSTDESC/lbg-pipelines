# API Reference

Custom stages for the LBG pipelines are defined in the `lbg_stages` package.
Each stage is a `ceci` `PipelineStage` subclass; configuration keys are set in
the pipeline config YAML.
Note that many of our stages are not defined here but are instead imported from [`TXPipe`](https://txpipe.readthedocs.io/en/latest/) and [`RAIL`](https://rail-hub.readthedocs.io/en/latest/index.html#).

::: lbg_stages.FlagshipReducer
    options:
      members:
        - run
