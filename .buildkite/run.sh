#!/usr/bin/env bash
set -euo pipefail
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/fakegreg_acceptance.py
python3 scripts/fakegreg_calibrate.py
python3 scripts/fakegreg_eval.py report --no-history --out /tmp/fakegreg-baseline.json
python3 scripts/fakegreg_eval.py compare --base data/evals/baseline.json --head /tmp/fakegreg-baseline.json --fail-on-regression
