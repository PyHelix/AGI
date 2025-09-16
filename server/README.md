# Server scripts

This folder contains example files for running a BOINC-based training project. Copy its contents into the project directory created by `make_project`.

- `apps/` contains subdirectories for each skill. Put the quantized model file and `train_local.py` runner in each.
- `wu_template.xml` and `result_template.xml` describe the input and output files for a work unit.
- `validator.py` checks returned results.
- `fed_avg.py` aggregates accepted weight deltas.
- `setup_project.sh` demonstrates how to generate work units.

## Generating work units from the repository root

The helper script can be called directly from the repository root. It first looks for
bundled weight files under `server/apps/` and falls back to a legacy `apps/` directory if
you have already copied the project assets elsewhere.

```bash
python server/generate_wu.py \
  --skill language \
  --data /path/to/chunk.jsonl \
  --out work_units/language
```
