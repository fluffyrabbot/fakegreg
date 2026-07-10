# Greg UI Data Builder Notes

## Goal
Curate high-quality specimen bundles that improve the reproduction and enhancement skills over time and can be regression-tested.

## Recommended Process
1. Use real Greg (greg-2-ultra or super) via the CrofAI API for new generations.
2. Use prompts modeled on the gallery (same prompt for fair comparisons, or targeted landing/dashboard prompts).
3. Save a full specimen bundle under `data/specimens/<id>/`:
   - `prompt.md`
   - raw HTML/TSX output
   - rendered artifact if the raw output is framework code
   - screenshot (use browse or local render)
   - `analysis.md`
   - `notes.md`
   - `manifest.json` (must validate against `schemas/specimen.schema.json`)
4. Set honest provenance on the manifest:
   - `generator.provenance`: `real_api` | `gallery_extract` | `skill_reproduction` | `synthetic_seed`
   - `generator.notes`: short free-text caveat
   - `score_meta.scorer`: `human` | `skill` | `script`
   - `score_meta.scored_at` and optional `method`
5. Directory name must equal `manifest.id`. Artifact paths must be relative and stay inside the specimen dir.
6. Promote only the strongest canonical references into `references/`.
7. Periodically distill new patterns back into `references/SENSIBILITIES.md`, `references/STYLE_PRIMITIVES.md`, and the skill prompts.
8. Run `make accept` and `make report` after adding specimens.

## Example Prompt Template (for real Greg)
"Create a beautiful, complete, self-contained modern landing page for [PRODUCT DESCRIPTION]. 
Use the exact same visual and narrative quality as the Meridian demo:
- Strong hero with kicker and interactive visual (canvas globe or mesh)
- // section kickers
- Geometric unicode feature icons + tags
- One beautifully styled code quickstart block
- Impressive real-feeling production metrics
- Final CTA card
Make it fully runnable in a single file."

## Quick API Call Example
```bash
curl https://crof.ai/v1/chat/completions \
  -H "Authorization: Bearer $CROF_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "greg-2-ultra",
    "messages": [{"role":"user","content":"...prompt above..."}]
  }'
```

## Built Tooling
- `make accept` — schema, path safety, structure, score floors.
- `make calibrate` — score bands + pairwise preference consistency.
- `make report` — baseline pointer + timestamped history under `data/evals/runs/`.
- `make screenshot` — Chrome headless screenshots for HTML specimens.
- `python3 scripts/fakegreg_collect.py api` — real Greg API → specimen bundles (`provenance: real_api`).
- `python3 scripts/fakegreg_collect.py gallery` — live greg.crof.ai page → specimen (`gallery_extract`).
- `python3 scripts/fakegreg_eval.py compare --base ... --head ...` — score/pass regressions.
- `python3 scripts/fakegreg_eval.py run` — OpenAI-compatible API execution of the core prompt set.
- `make test` / `make ci` — unit tests + full local CI mirror.

## Collect examples

```bash
export CROF_API_KEY=...
python3 scripts/fakegreg_collect.py api --prompt-set data/prompt_sets/collect.json --model greg-2-super
python3 scripts/fakegreg_collect.py gallery --url https://greg.crof.ai/greg-2-super --id nexus-super-gold --kind reference
make accept && make calibrate && make report
```

Start with the canonical bundle shape, then automate more collection over time.
