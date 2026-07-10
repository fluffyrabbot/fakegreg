# fakegreg Status — 2026-07-09

## Completed

1. **Research foundation** — Meridian reference, Greg sensibilities, benchmark framing, and skill strategy.
2. **Core skill stack** — direct repro, analyzer, enhancer, and landing specialist in `.grok/skills/`.
3. **Canonical reference pack** — shared `references/` with sensibilities, primitives, archetypes, anti-examples, Meridian seed.
4. **Strict specimen corpus** — bundles under `data/specimens/` (prompt, output, screenshot, analysis, notes, manifest).
5. **Honest provenance + score metadata** — required enums + `score_meta`.
6. **Schema-backed acceptance** — path safety, structure, score floors.
7. **Eval history + compare** — timestamped reports and regression compare.
8. **Collect pipeline** — `fakegreg_collect.py` for Greg API (`real_api`) and live gallery import (`gallery_extract`).
9. **Screenshot automation** — Chrome headless via `fakegreg_screenshot.py`.
10. **Calibration + pairwise** — `data/calibration/bands.json`, `data/pairwise/core.json`, `fakegreg_calibrate.py`; analyzer skill documents pairwise mode.
11. **Gallery expansion** — `nexus-super-gold` (greg-2-super) and `opus-gallery-anti` (opus-4.8) imported from greg.crof.ai.

## Current Skills

- /greg-direct-repro
- /greg-ui-analyze
- /greg-ui-enhance
- /greg-ui-landing

## Key Files

- `references/`
- `data/specimens/`
- `data/prompt_sets/{core,collect}.json`
- `data/calibration/bands.json`
- `data/pairwise/core.json`
- `scripts/fakegreg_{acceptance,eval,collect,screenshot,calibrate,api,lib}.py`
- `Makefile`
- `.github/workflows/ci.yml`

## Current Baseline

| Specimen | Provenance | Role | Score |
|---|---|---|---|
| meridian-gold | gallery_extract | ceiling | 96 |
| nexus-super-gold | gallery_extract | Greg super reference | 89 |
| forgenet-enhanced | skill_reproduction | enhance loop | 87 |
| forgenet-direct | skill_reproduction | direct baseline | 82 |
| relay / vectordocs / meshdb | synthetic_seed | surface expanders | 84–88 |
| opus-gallery-anti | gallery_extract | non-Greg gallery control | 58 |
| generic-cloud-anti | synthetic_seed | synthetic control | 41 |

## Note on real_api

`python3 scripts/fakegreg_collect.py api` is ready and dry-runnable. This machine did not have `CROF_API_KEY` / `FAKEGREG_API_KEY` at collect time, so no `provenance: real_api` specimens were written yet. With a key:

```bash
export CROF_API_KEY=...
python3 scripts/fakegreg_collect.py api --model greg-2-super
```

## Next Promising Steps

- Run API collect with a real key and commit `real_api` specimens.
- Expand pairwise pairs for docs/dashboard surfaces.
- Optional Browserbase remote screenshots for CI without local Chrome.
