# AGI

This repository demonstrates a minimal pipeline for decentralized model training using the [BOINC](https://boinc.berkeley.edu/) server tools. Volunteers download tasks, perform local fine‑tuning on small quantized models and send weight updates back to the server.

```
router.py -> generate_wu.py -> BOINC -> validator.py -> fed_avg.py
```

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
7. **Route tasks to the best skill** with `router.py`. This helper reads
   `scoreboard.csv` and selects the skill ID with the highest average reward so
   new work units target the most promising model.
8. **Validate returned work** using `validator.py`. Check hashes, run a quick evaluation and reject results that score below a threshold.
9. **Aggregate accepted updates** nightly with `fed_avg.py` which now uses the FedOpt algorithm with momentum and writes the encrypted global weights.
10. **Grant BOINC credit** only when a node’s update passed validation and log the result via `scoreboard.py`.
11. **Publish snapshots and metrics** using `nightly_snapshot.sh` so others can track progress.

The `server/` directory of this repository provides example scripts and templates to get started.
