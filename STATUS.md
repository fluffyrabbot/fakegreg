# fakegreg Status — 2026-06-22

## Completed

1. **Research foundation** — Meridian reference, Greg sensibilities, benchmark framing, and skill strategy.
2. **Core skill stack** — direct repro, analyzer, enhancer, and landing specialist in `.grok/skills/`.
3. **Canonical reference pack** — shared `references/` directory with sensibilities, style primitives, page archetypes, anti-examples, and the Meridian seed.
4. **Strict specimen corpus** — every canonical example now lives as a bundle in `data/specimens/` with prompt, output, screenshot, analysis, notes, and manifest.
5. **Tiny eval harness** — `scripts/fakegreg_eval.py` emits baseline reports and can run prompt sets through an OpenAI-compatible API.
6. **Acceptance checks** — `scripts/fakegreg_acceptance.py` validates corpus shape, required sections, required visuals, analyzer output structure, and score floors.
7. **Broader corpus** — landing, dashboard, docs, pricing/framework, and anti-example surfaces are now represented.

## Current Skills

- /greg-direct-repro
- /greg-ui-analyze
- /greg-ui-enhance
- /greg-ui-landing

## Key Files

- `references/`
- `data/specimens/`
- `data/prompt_sets/core.json`
- `scripts/fakegreg_acceptance.py`
- `scripts/fakegreg_eval.py`
- `docs/data-builder.md`

## Current Baseline

- `meridian-gold` is the reference ceiling.
- `forgenet-direct` and `forgenet-enhanced` anchor the landing-page loop.
- `relay-ops-dashboard`, `vectordocs-home`, and `meshdb-pricing-react` prevent overfitting to one archetype.
- `generic-cloud-anti` is the negative control.

## Next Promising Steps

- Add real Greg API generations into the structured corpus.
- Save eval snapshots over time for regression comparison.
- Expand the non-landing corpus with richer dashboards and docs variants.
- Improve analyzer rigor with additional anti-examples and pairwise comparisons.
