# Calibration bands

`bands.json` declares expected overall-score ranges (and optional kind/provenance constraints) for labeled specimens.

```bash
python3 scripts/fakegreg_calibrate.py
# or
make calibrate
```

When rescoring specimens, keep them inside their bands or update the bands deliberately with a compare note.
