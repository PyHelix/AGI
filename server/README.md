# Server scripts

This folder contains example files for running a BOINC-based training project. Copy its contents into the project directory created by `make_project`.

- `apps/` contains subdirectories for each skill. Put the quantized model file and `train_local.py` runner in each.
- `wu_template.xml` and `result_template.xml` describe the input and output files for a work unit.
- `validator.py` checks returned results.
- `fed_avg.py` aggregates accepted weight deltas.
- `setup_project.sh` demonstrates how to generate work units.
- `generate_wu.py` provides a `create_wu` helper to build work units.
- `scheduler.py` picks the highest scoring skill using `router.py` and calls
  `generate_wu`.
