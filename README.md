# AGI

This repository demonstrates a minimal pipeline for decentralized model training using the [BOINC](https://boinc.berkeley.edu/) server tools. Volunteers download tasks, perform local fine‑tuning on small quantized models and send weight updates back to the server.

```
router.py -> scheduler.py -> generate_wu.py -> BOINC -> volunteer.py -> validator.py -> fed_avg.py
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
7. **Automate generation** with `scheduler.py` which selects the best skill and creates the next work unit.
8. **Route tasks to the best skill** with `router.py`.
9. **Volunteers train locally** using `client/volunteer.py` which encrypts updates before upload.
10. **Validate returned work** using `validator.py`. Check hashes, run a quick evaluation and reject results that score below a threshold.
11. **Aggregate accepted updates** nightly with `fed_avg.py` which now uses the FedOpt algorithm with momentum and writes the encrypted global weights.
12. **Grant BOINC credit** only when a node’s update passed validation and log the result via `scoreboard.py`.
13. **Publish snapshots and metrics** using `nightly_snapshot.sh` so others can track progress.

The `server/` directory of this repository provides example scripts and templates to get started.

## Resource-aware sharding

Large community grids often have a mix of resource tiers.  Use `server/resource_sharder.py`
to describe the available volunteers and automatically generate work units tailored to each
shard.  The script reads a JSON file describing every host, divides the data into shards and
calls `generate_wu.py` with custom step counts, learning rates and shard identifiers so the
aggregator can keep track of which update came from which hardware tier.

Example `resources.json`:

```json
[
  {"id": "gpu-rig-01", "weight": 3.0, "max_tasks": 2, "resource_class": "gpu"},
  {"id": "edge-node-12", "weight": 1.0, "max_tasks": 1, "resource_class": "cpu"}
]
```

Generate sharded work units for the highest priority skill:

```bash
python server/resource_sharder.py \
  --skill vision \
  --data datasets/vision_prompts.jsonl \
  --resources resources.json \
  --out work_units/vision \
  --base-steps 200 \
  --base-lr 3e-4
```

Each generated `wu_*.xml` now includes the shard identifier and the resource class which are
propagated to the volunteers and the training logs, enabling decentralized aggregation and
auditing across the BOINC swarm.
