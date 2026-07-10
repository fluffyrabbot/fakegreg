# Acceptance checks

This directory now defines the lightweight acceptance suite instead of holding ad hoc HTML examples.

Run:

```bash
python3 scripts/fakegreg_acceptance.py --suite tests/acceptance-suite.json
```

The suite validates:
- canonical specimen shape
- required artifacts
- structural page checks
- analyzer output shape
- score floors for gold and candidate specimens
- expected low score ceilings for anti-examples
