# Eval outputs

- `baseline.json` — latest committed corpus report (source of truth for CI compare).
- `runs/<run_id>/report.json` — timestamped history from `python3 scripts/fakegreg_eval.py report`.
- `runs/<run_id>/result.json` — API-backed runs from `python3 scripts/fakegreg_eval.py run`.
- `runs/latest.json` — pointer to the most recent history entry written on this machine.

Compare two runs:

```bash
python3 scripts/fakegreg_eval.py compare \
  --base data/evals/baseline.json \
  --head data/evals/runs/<run_id>/report.json \
  --fail-on-regression
```
