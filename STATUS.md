# fakegreg Status — 2026-07-09

## Completed

1. **Research foundation** — Meridian reference, Greg sensibilities, benchmark framing, and skill strategy.
2. **Core skill stack** — direct repro, analyzer, enhancer, and landing specialist in `.grok/skills/`.
3. **Canonical reference pack** — shared `references/` directory with sensibilities, style primitives, page archetypes, anti-examples, and the Meridian seed.
4. **Strict specimen corpus** — every canonical example lives as a bundle in `data/specimens/` with prompt, output, screenshot, analysis, notes, and manifest.
5. **Honest provenance + score metadata** — manifests require `generator.provenance` enums and `score_meta.scorer` / `scored_at`.
6. **Schema-backed acceptance** — path safety, schema contract, structure checks, and score floors via `scripts/fakegreg_acceptance.py`.
7. **Eval history + compare** — `report` writes timestamped runs; `compare` detects score/pass regressions.
8. **CI + unit tests** — GitHub Actions + `make ci` run tests, acceptance, and baseline compare.

## Current Skills

- /greg-direct-repro
- /greg-ui-analyze
- /greg-ui-enhance
- /greg-ui-landing

## Key Files

- `references/`
- `data/specimens/`
- `data/prompt_sets/core.json`
- `data/evals/baseline.json`
- `scripts/fakegreg_acceptance.py`
- `scripts/fakegreg_eval.py`
- `schemas/specimen.schema.json`
- `Makefile`
- `.github/workflows/ci.yml`

## Current Baseline

- `meridian-gold` is the reference ceiling (`gallery_extract`).
- `forgenet-direct` / `forgenet-enhanced` are `skill_reproduction` anchors for the landing loop.
- `relay-ops-dashboard`, `vectordocs-home`, and `meshdb-pricing-react` are `synthetic_seed` surface expanders.
- `generic-cloud-anti` is the negative control.
- All current scores are `score_meta.scorer: human` until skill/script scoring is automated.

## Next Promising Steps

- Add real Greg API generations (`provenance: real_api`) into the structured corpus.
- Automate screenshot capture on collect.
- Expand analyzer calibration with pairwise preferences.
- Grow anti-examples and non-landing surfaces once measurement stays green in CI.
