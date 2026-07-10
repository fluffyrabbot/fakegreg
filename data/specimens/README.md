# Canonical specimen bundles

Each specimen is a strict bundle with:

- `prompt.md`
- raw output (`output.html` or `output.tsx`)
- optional rendered artifact for framework specimens
- `screenshot.png`
- `analysis.md`
- `notes.md`
- `manifest.json`

The manifest shape is documented in `schemas/specimen.schema.json`.

## Required honesty fields

```json
"generator": {
  "provenance": "real_api | gallery_extract | skill_reproduction | synthetic_seed",
  "notes": "free-text caveats"
},
"score_meta": {
  "scorer": "human | skill | script",
  "scored_at": "YYYY-MM-DD or ISO datetime",
  "method": "optional"
}
```

Do **not** label skill reproductions or synthetic seeds as `real_api`. Acceptance enforces the enum and path safety.

This turns examples into portable, testable dataset entries instead of loose artifacts.
