# fakegreg

Research, skill scaffolding, and evaluation infrastructure for capturing **Greg 2** UI sensibilities and reproducing them in reusable workflows.

## What this repo is now

fakegreg is no longer just a prompt collection. It now has three layers:

1. **Canonical references** in `references/`
2. **Invocable skills** in `.grok/skills/`
3. **A structured specimen corpus + eval harness** in `data/specimens/`, `data/prompt_sets/`, and `scripts/`

The goal is to turn “Greg taste” into something you can **generate, critique, refine, and regress-test** instead of remembering by feel.

## Why Greg

Greg 2 has been notable for:
- stronger UI polish than typical same-prompt peers
- sharper narrative + proof density
- unusually good single-file product demos and infrastructure pages

The Meridian example remains the repo’s quality ceiling, but the corpus now widens beyond that single landing-page archetype.

## Canonical layout

| Path | Purpose |
|---|---|
| `references/` | Shared source-of-truth references: Meridian, sensibilities, style primitives, page archetypes, anti-examples |
| `.grok/skills/` | Direct repro, analyzer, enhancer, and landing specialist skills |
| `data/specimens/` | Strict specimen bundles with prompt, output, screenshot, analysis, notes, and manifest |
| `data/prompt_sets/core.json` | Fixed baseline prompt set for eval/reporting |
| `scripts/fakegreg_acceptance.py` | Schema-backed acceptance checks over the corpus |
| `scripts/fakegreg_eval.py` | Baseline reports, run history, compare, and API evals |
| `data/evals/` | Committed baseline + timestamped eval history |
| `Makefile` | `accept` / `report` / `compare` / `test` / `ci` shortcuts |
| `data/generated/` | Scratch/ad hoc generated artifacts |

## Shared references

The repo-wide reference pack is:
- `references/SENSIBILITIES.md`
- `references/STYLE_PRIMITIVES.md`
- `references/PAGE_ARCHETYPES.md`
- `references/ANTI_EXAMPLES.md`
- `references/meridian-greg.html`
- `references/greg-meridian.png`

Skills should point here directly instead of carrying their own duplicate reference bundles.

## Live skills

- `/greg-direct-repro` — faithful Greg-style generation
- `/greg-ui-analyze` — crofbench-style critique and scoring
- `/greg-ui-enhance` — critique-driven refinement loop
- `/greg-ui-landing` — specialized landing-page variant

## Canonical specimen format

Every specimen now lives in its own directory under `data/specimens/<id>/` and includes:

- `prompt.md`
- raw output (`output.html` or `output.tsx`)
- optional rendered artifact for framework specimens
- `screenshot.png`
- `analysis.md`
- `notes.md`
- `manifest.json`

The schema lives in `schemas/specimen.schema.json`.

Every manifest must declare honest provenance and score metadata:

- `generator.provenance`: `real_api` | `gallery_extract` | `skill_reproduction` | `synthetic_seed`
- `generator.notes`: free-text caveats
- `score_meta.scorer`: `human` | `skill` | `script`
- `score_meta.scored_at` + optional `method`

Included surfaces now span:
- landing pages
- dashboards
- docs homes
- pricing/framework output
- anti-examples

## Acceptance checks and evals

Quick path:

```bash
make accept   # schema + path + structure + score floors
make test     # unit tests for helpers
make report   # data/evals/baseline.json + data/evals/runs/<id>/report.json
make ci       # local mirror of GitHub Actions
```

Or directly:

```bash
python3 scripts/fakegreg_acceptance.py
python3 scripts/fakegreg_eval.py report
python3 scripts/fakegreg_eval.py compare \
  --base data/evals/baseline.json \
  --head data/evals/runs/<run_id>/report.json \
  --fail-on-regression
```

Run the prompt set through an OpenAI-compatible API using the skill prompts:

```bash
export CROF_API_KEY=...
python3 scripts/fakegreg_eval.py run --model greg-2-super
```

By default the run command targets `https://crof.ai/v1/chat/completions`, but it also supports `FAKEGREG_API_KEY`, `FAKEGREG_BASE_URL`, and `FAKEGREG_MODEL`.

CI (`.github/workflows/ci.yml`) runs unit tests, acceptance, and a baseline compare on every push/PR.

## Workflow

1. Generate with `/greg-direct-repro` or `/greg-ui-landing`
2. Analyze with `/greg-ui-analyze`
3. Refine with `/greg-ui-enhance`
4. Save strong outputs as specimen bundles with honest `provenance` + `score_meta`
5. Run `make accept` and `make report` to prevent taste drift
6. Use `compare --fail-on-regression` when changing skills or rubric thresholds

## Contribution direction

High-value next work:
- add more **real Greg API** generations (`provenance: real_api`) into `data/specimens/`
- keep `references/STYLE_PRIMITIVES.md` and `references/ANTI_EXAMPLES.md` sharp
- broaden non-landing surfaces further
- use eval history + compare when revising skill prompts

**GitHub**: https://github.com/fluffyrabbot/fakegreg
