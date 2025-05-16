# AGI

This repository demonstrates a minimal pipeline for decentralized model training using the [BOINC](https://boinc.berkeley.edu/) server tools. Volunteers download tasks, perform local fine‑tuning on small quantized models and send weight updates back to the server.

## Steps in brief

1. **Install the BOINC server tools**
   ```bash
   sudo apt-get install boinc-server-maker boinc-server-binaries boinc-server-tools
   ```
   See the BOINC wiki for complete instructions.
2. **Create a project directory**
   ```bash
   make_project agiNet
   cd agiNet
   ```
3. **Add the skill apps** under `apps/`.
   Example subfolders:
   - `apps/vision`
   - `apps/language`
   - `apps/memory`
   - `apps/planner`
   Each folder should contain a small quantized model file and a `train_local.py` runner.
4. **Prepare the training script**.
   `train_local.py` loads the weights, fine‑tunes on the provided dataset and writes weight deltas and a reward score.
5. **Create work-unit templates** using `wu_template.xml` and `result_template.xml`. Each work unit contains the skill name, current weights, a mini dataset or prompts and the training script.
6. **Generate work units** with `sched_create_work` so volunteers can download tasks.
7. **Validate returned work** using `validator.py`. The example validator reads
   the `reward` value reported by each worker and only accepts updates that
   score at least `0.5`.
8. **Aggregate accepted updates** nightly with `fed_avg.py`. The aggregator
   performs a weighted average of the returned deltas using each worker’s
   reward as the weight and writes updated global weights. Bump `version_num` in
   `app_version.xml` so future tasks fetch the new weights.
9. **Grant BOINC credit** only when a node’s update passed validation to keep volunteers honest.
10. **Publish snapshots and metrics** so others can track progress.

The `server/` directory of this repository provides example scripts and templates to get started.
