# Architecture

```
router.py -> generate_wu.py -> BOINC -> validator.py -> fed_avg.py
```

1. **router.py** picks the best skill from `scoreboard.csv`.
2. **generate_wu.py** creates a work unit with dataset chunk and model weights.
3. Volunteers train locally and submit deltas.
4. **validator.py** checks the update and scores it.
5. **fed_avg.py** aggregates accepted deltas into encrypted global weights.
