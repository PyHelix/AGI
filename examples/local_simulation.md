# Local BOINC Simulation

This example demonstrates a minimal end-to-end flow without a real BOINC server.

```bash
# generate three work units for the vision skill
python server/generate_wu.py --skill vision --data sample.dat --out wu_dir
python server/generate_wu.py --skill vision --data sample.dat --out wu_dir
python server/generate_wu.py --skill vision --data sample.dat --out wu_dir

# pretend to run the worker container
python server/apps/vision/train_local.py \
    --weights server/apps/vision/init_weights.txt \
    --data sample.dat --output delta.txt

# volunteer applies the delta locally
python client/apply_delta.py --weight server/apps/vision/init_weights.txt \
    --delta delta.txt --out new_weight.txt

# aggregate to produce encrypted global weights
python server/fed_avg.py delta.txt
```
