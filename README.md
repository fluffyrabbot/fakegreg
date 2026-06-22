# fakegreg

Research + skill scaffolding for capturing **Greg 2** (greg.crof.ai) UI design sensibilities and reproducing / iterating on them.

**Why**: Greg 2 leads crofbench 1.0 (UI design quality + code correctness + visual polish) at 78% vs Opus-like models. Outputs are notably more polished, narrative-driven, and visually delightful (see Meridian example). Patterns are **not deeply recorded publicly** yet — perfect opportunity to encode them into reusable Grok skills.

## Research Summary (as of 2026-06-21)
- **Greg 2 ultra/super**: Frontier-ish, 229k context, strong reasoning/tools + **explicit UI leadership**.
- **Pricing win**: 40-67% cheaper than equivalent Opus/Sonnet while claiming same speed.
- **Gallery**: Same prompt → side-by-side rendered landing pages. Greg wins on polish.
- **Key exemplar**: "Meridian" (greg-2-ultra) — global edge AI product site with interactive globe + HUD, // kickers, geometric icons, beautiful code block, big metrics, tight credible copy.
- **Community recording**: Mostly the marketing site itself. Sparse external deep analysis (model is ~4 days old).
- **Viability**: Excellent. Concrete artifacts (HTML + screenshots + contrasts). Real model is cheap and OpenAI-compatible for data generation.

Full details in previous analysis + `SENSIBILITIES.md`.

## Recommended Sequence (followed here)
1. **Direct reproduction** (`greg-direct-repro`) — few-shot + style prompt that tries to match Meridian/Greg output directly.
2. **Analyzer / Critic** — score outputs on Greg dimensions + suggest improvements.
3. **Iterative enhancer** — generate → analyze → refine loop.
4. **Variants** (domain + framework specific).
5. **Infrastructure** (data builder using real Greg if API key, eval harness approximating crofbench, dataset curation).
6. **Refine** across the board with more examples + testing.

## Current Artifacts
- `data/examples/meridian-greg.html` — cleaned primary few-shot seed from winning output.
- Screenshots: `greg-meridian.png` (winning render), `opus-comparison.png`, etc.
- `SENSIBILITIES.md` — distilled patterns, heuristics, anti-patterns.
- `.grok/skills/...` — the actual invocable skills (project-scoped).

**Live skills created in sequence:**
- `/greg-direct-repro` — core direct reproduction
- `/greg-ui-analyze` — scoring + critique against crofbench-style dimensions
- `/greg-ui-enhance` — iterative refinement loop
- `/greg-ui-landing` — specialized variant for gallery-style product landing pages

## Refinement Example (in tests/)
- `tests/test-forge-net-greg.html` — direct generation following the Meridian template (ForgeNet mesh)
- `tests/forge-net-analysis.md` — analyzer output (87/100) with concrete Greg improvements

## Using the Skills
Once skills are created:
- `/greg-direct-repro "Build a landing page for a new vector database with global sync"`
- Or via TUI menu.
- Skills reload automatically.

**To use real Greg for ground truth / data** (highly recommended):
- Get CROF_API_KEY from crof.ai
- Base URL: `https://crof.ai/v1` or `https://ai.nahcrof.com/v1`
- Model: `greg-2-ultra` or `greg-2-super`

## Quick Loop Example
1. `/greg-direct-repro` or `/greg-ui-landing "new product description"`
2. `/greg-ui-analyze` the output
3. `/greg-ui-enhance` the output + analysis
4. Save winners to `data/generated/` and `references/`

## Next / How to Contribute
- Run generations with real Greg and add more examples to `data/examples/`.
- Update `SENSIBILITIES.md` with new observations.
- Test skills and refine prompts in SKILL.md files.
- Expand to React/Tailwind variants, dashboard patterns, etc.

## Screenshots Reference
See `greg-meridian.png` for the visual target.

This is a living project to turn Greg's taste into portable, improvable skills.
