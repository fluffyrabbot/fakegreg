.PHONY: accept report compare test ci help

help:
	@echo "Targets:"
	@echo "  make accept   - validate specimen corpus shape + thresholds"
	@echo "  make report   - write baseline.json + timestamped eval history"
	@echo "  make compare  - compare two eval JSON files (BASE= HEAD=)"
	@echo "  make test     - unit tests for acceptance/eval helpers"
	@echo "  make ci       - accept + test + report (no history write)"

accept:
	python3 scripts/fakegreg_acceptance.py

report:
	python3 scripts/fakegreg_eval.py report

compare:
	@test -n "$(BASE)" || (echo "Set BASE=path/to/base.json"; exit 1)
	@test -n "$(HEAD)" || (echo "Set HEAD=path/to/head.json"; exit 1)
	python3 scripts/fakegreg_eval.py compare --base "$(BASE)" --head "$(HEAD)" --fail-on-regression

test:
	python3 -m unittest discover -s tests -p 'test_*.py' -v

ci: test accept
	python3 scripts/fakegreg_eval.py report --no-history --out /tmp/fakegreg-baseline.json
	python3 scripts/fakegreg_eval.py compare --base data/evals/baseline.json --head /tmp/fakegreg-baseline.json --fail-on-regression
