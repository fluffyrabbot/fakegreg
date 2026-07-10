# Tests and acceptance suite

## Acceptance suite

```bash
make accept
# or
python3 scripts/fakegreg_acceptance.py --suite tests/acceptance-suite.json
```

Validates:
- specimen schema contract (provenance enum, score_meta, enums, ranges)
- directory name matches `manifest.id`
- relative artifact paths stay inside the specimen directory
- required artifacts exist (non-empty screenshot)
- structural page checks
- analyzer output shape
- score floors for gold/candidates and ceilings for anti-examples

## Unit tests

```bash
make test
# or
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

## Full local CI mirror

```bash
make ci
```
