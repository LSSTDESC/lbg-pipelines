## Summary

_Describe the change: what does this PR add or fix, and why?_

## Science context

_If relevant: which analysis step does this affect? Any caveats about data versions or pipeline runs?_

## Checklist

- [ ] Pipeline YAML is valid (`check-yaml` pre-commit hook passes)
- [ ] Any Python / notebook changes are linted (`ruff`) and notebook outputs are stripped (`nbstripout`)
- [ ] Docs updated if a new stage, pipeline, or run was added
- [ ] Attached a png of the DAG (created with `scripts/create_pipeline_dag.py`) for any new pipelines added
- [ ] Successful test certificate attached (run `scripts/generate_test_certificate.sh` and copy/paste outputs)
- [ ] Relevant team members are tagged as reviewers
