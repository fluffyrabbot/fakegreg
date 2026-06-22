# fakegreg Status — 2026-06-21

## Completed in Recommended Sequence

1. **Research** — Deep dive into greg.crof.ai, gallery, benchmarks, HTML extraction from Meridian (winning output), contrasts (Opus, Sonnet), pricing, community signals.
2. **Project setup** — README, SENSIBILITIES.md (distilled patterns), data/ + references/, screenshots.
3. **Direct reproduction** — `greg-direct-repro` skill scaffolded + refined (references + instructions to load Meridian + SENSIBILITIES).
4. **Analyzer** — `greg-ui-analyze` skill with crofbench-style rubric and structured output.
5. **Enhancer loop** — `greg-ui-enhance` skill implementing the generate → analyze → refine workflow.
6. **Variants + infra** — `greg-ui-landing` (specialized for the exact gallery style), data-builder.md guide, tests/ + data/generated/.
7. **Refinement + test** — Generated ForgeNet test page (direct style), ran analysis (87/100), applied one polish enhancement (glow layer), archived results.

## Current Skills (all live in .grok/skills/)
- /greg-direct-repro
- /greg-ui-analyze
- /greg-ui-enhance
- /greg-ui-landing

## Key Files
- SENSIBILITIES.md
- data/examples/meridian-greg.html (gold reference)
- tests/ and data/generated/ (loop demonstration)
- docs/data-builder.md

## Next Promising Steps
- Add more real Greg generations (API) for better few-shots.
- Implement a tiny eval script (prompt batch + analyzer scoring).
- Add a dashboard variant.
- Hook the skills more deeply with the browser skill for automated screenshot + analysis.

The foundation for recording and iterating on Greg's UI sensibilities is now in place and functional.
