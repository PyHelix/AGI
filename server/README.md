# Server scripts

This folder contains example files for running a BOINC-based training project. Copy its contents into the project directory created by `make_project`.

- `apps/` contains subdirectories for each skill. Put the quantized model file and `train_local.py` runner in each.
- `wu_template.xml` and `result_template.xml` describe the input and output files for a work unit.
- `validator.py` checks returned results.
- `fed_avg.py` aggregates accepted weight deltas.
- `generate_wu.py` creates a single work unit from a data chunk and skill id.
- `scheduler.py` picks the best skill based on `scoreboard.csv` and calls `generate_wu.py`.
- `setup_project.sh` demonstrates how to generate work units.
