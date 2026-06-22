---
name: greg-direct-repro
description: >
  Directly reproduce Greg-2 (greg.crof.ai) UI design sensibilities for polished, modern, narrative-driven product UIs and demos that win on crofbench.
  Use when you want a high-fidelity landing page, marketing site, or interactive demo in the style of the Meridian example. Triggers: "greg style", "like greg", "meridian style", "greg ui", "fakegreg", "crof ui", "polished like greg-2", "greg landing".
  Slash: /greg-direct-repro
version: 0.1.0
author: fakegreg
---

# Greg Direct Reproduction Skill

Reproduce the UI sensibilities that make Greg-2 (especially ultra) win on crofbench 1.0 for UI design quality, code correctness, and visual polish.

## Core Target Aesthetic (from Meridian + gallery wins)
- Clean modern tech branding with excellent hierarchy and breathing room.
- Strong product narrative: aspirational yet credible headlines, precise benefit-focused copy.
- Signature kickers: `// the model`, `// the network`, `// in production`.
- Geometric unicode icons (◇ ◈ ◍ ▲) + small `.tag` lines for features.
- Interactive canvas elements (globe with rings/glow/HUD, starfields) when they fit the product story.
- Beautifully styled self-contained code demos (window bar, syntax, copy button, realistic curl).
- Big impressive metrics presented cleanly.
- Self-contained runnable HTML (or clean component output) that feels premium out of the box.
- Sticky frosted nav, strong primary CTAs, ghost buttons, `.wrap` containers.

## Primary Seed Example
Use the Meridian demo as the gold standard reference:

```html
<!-- See references/meridian-greg.html for the full cleaned representative output -->
<!-- Key excerpts loaded in context or read the file when needed. -->
```

Key structural patterns from it (internalize):
- Hero with kicker + big h1 (with em) + sub + CTAs + note.
- Globe/HUD stage on the right.
- Stats row.
- Section with // kicker + h2 + prose + .feat-grid.
- Arch section with prose + beautiful .code-window.
- Impact grid with .big numbers.
- Final CTA card.
- Consistent footer.

## Instructions
1. **Always start by loading references**:
   - Read `references/meridian-greg.html` (primary seed)
   - Read `references/SENSIBILITIES.md` for full distilled patterns
   - View `references/greg-meridian.png` if available for visual target
2. Understand current task and map it to a similar high-signal product landing / demo page or UI surface.
3. Produce **complete, delightful, self-contained** output (prefer single-file HTML+Tailwind or vanilla CSS + JS for demos unless specified).
4. Apply these Greg heuristics:
   - Lead with powerful, specific positioning.
   - Use // kickers liberally in tech/product pages.
   - Add one strong visual/interactive moment (canvas preferred if it serves the story).
   - Include at least one beautifully presented code/API example when relevant.
   - Use precise numbers and tags.
   - Make every element feel intentional and polished (spacing, typography, micro-details).
5. If the user asks for a framework (React, Vue, TSX), translate the sensibilities while keeping the same taste level.
6. Output runnable code first, then a short note on how it captures Greg qualities.

## Usage Examples
- `/greg-direct-repro create a landing page for a new global vector database`
- "Build a dashboard for a distributed inference mesh using greg sensibilities"
- "Generate the UI for a privacy-first edge AI product like the Meridian example"

## Example Prompts (copy-paste)
```
/greg-direct-repro A new collaborative real-time code canvas called "LiveForge". Include interactive canvas, team presence, and clean code example.
```

```
/greg-direct-repro Build a beautiful landing page for "EdgeMesh" - sub-10ms global inference with a live network visualization.
```

## Iteration Notes
This is the *direct* repro skill. After using it:
- Feed results into the analyzer skill for scoring.
- Use enhancer for passes.
- Add new generations (especially from real greg-2 via API) to references/.

## When to call real Greg instead
If you have a CROF_API_KEY and want ground-truth outputs:
- Base: https://crof.ai/v1 (or ai.nahcrof.com/v1)
- Models: greg-2-ultra (max quality) or greg-2-super (faster/cheaper)
- Then bring the HTML back here for distillation.

Keep this skill focused on faithful reproduction of the observed Greg taste.
