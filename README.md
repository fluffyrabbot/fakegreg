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
| `scripts/fakegreg_acceptance.py` | Lightweight acceptance checks over the corpus |
| `scripts/fakegreg_eval.py` | Baseline reporting and optional API-backed eval runs |
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

Included surfaces now span:
- landing pages
- dashboards
- docs homes
- pricing/framework output
- anti-examples

## Acceptance checks and evals

Run the baseline checks:

```bash
python3 scripts/fakegreg_acceptance.py
```

Emit a baseline eval report from the current corpus:

```bash
python3 scripts/fakegreg_eval.py report
```

Run the prompt set through an OpenAI-compatible API using the skill prompts:

```bash
export CROF_API_KEY=...
python3 scripts/fakegreg_eval.py run --model greg-2-super
```

By default the run command targets `https://crof.ai/v1/chat/completions`, but it also supports `FAKEGREG_API_KEY`, `FAKEGREG_BASE_URL`, and `FAKEGREG_MODEL`.

## Workflow

1. Generate with `/greg-direct-repro` or `/greg-ui-landing`
2. Analyze with `/greg-ui-analyze`
3. Refine with `/greg-ui-enhance`
4. Save strong outputs as specimen bundles
5. Run acceptance + report to prevent taste drift

## Contribution direction

High-value next work:
- add more real Greg generations into `data/specimens/`
- keep `references/STYLE_PRIMITIVES.md` and `references/ANTI_EXAMPLES.md` sharp
- broaden non-landing surfaces further
- use the eval harness to compare prompt and skill revisions instead of eyeballing them

**GitHub**: https://github.com/fluffyrabbot/fakegreg
