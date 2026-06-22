# Greg UI Sensibilities (Distilled from greg.crof.ai Gallery + Examples)

## Context
Greg 2 (especially ultra) is positioned as "radically better at UI design" per crofbench 1.0 (78% vs opus-4.8 73%). The gallery uses the **same prompt** to generate comparable product landing pages for a global-edge AI model. The Meridian example (greg-2-ultra) is the clear winner in visual polish, code correctness, and design quality.

Source artifacts:
- https://greg.crof.ai/ (marketing + gallery)
- https://greg.crof.ai/greg-2-ultra → "Meridian" full demo (primary seed)
- Contrasts: opus-4.8 (Nexus), sonnet-4.6 (similar NexusAI), etc.

## Core Sensibilities (Reproducible Patterns)

### 1. Narrative & Copy
- Strong, aspirational but credible product positioning from the first line.
- Punchy headlines with strategic emphasis (`<em>` or spans for key phrases like "without borders").
- Short, powerful subcopy that mixes vision + concrete specs (142 regions, sub-30ms, etc.).
- **Comment-style kickers**: `// the model`, `// the network`, `// in production` — gives technical/authentic feel.
- Feature descriptions are precise, benefit-oriented, avoid fluff. Use "No English tax", "0 fallback tiers".
- Production metrics feel real and impressive (big numbers with units, "already running the world's work").

### 2. Visual Structure & Hierarchy
- Generous top-level padding + tight internal spacing.
- `.wrap` container pattern (centered, max ~1200px).
- Clear section dividers, often with subtle borders.
- Hero grid: text (left) + strong visual (right, globe/canvas).
- Feature grids (auto-fit or 2-col) with icon + h3 + p + small tag.
- Stats/impact rows with large `.num` / `.big` typography.
- Progressive "reveal" classes for polish (subtle animations implied).

### 3. Visual / Interactive Polish
- Canvas-based interactive elements: globe (with rings/glow/HUD overlays), starfield backgrounds.
- HUD-style overlays (monospace, semi-transparent, live indicators).
- Layered decorative rings/glows around interactive viz.
- Drag hints and live status badges.
- Code demo blocks that are *styled beautifully* (window chrome, copy button, syntax highlights, realistic curl example).
- Unicode geometric symbols for icons (◇ ◈ ◍ ▲) — distinctive, lightweight, no external assets.
- Subtle gradients, good contrast, modern sans.

### 4. Components & Implementation
- Buttons: `.btn-primary` (solid high-contrast), `.btn-ghost` (outline).
- Nav: sticky, frosted, minimal links + prominent CTA.
- Code windows with bar (dots + filename + copy).
- Responsive hints (hide-sm classes).
- Self-contained single-file demos: full HTML + inline or minimal CSS + canvas JS.
- Semantic sections + good heading levels.
- Numbers that feel animated or live (connCount etc.).

### 5. What Makes It "Greg" vs Opus-like in Gallery
- **More refined microcopy and tags** — specific, memorable ("FEDERATED · PRIVACY-PRESERVING").
- **Richer visual language** without being busy (multiple globe layers + HUD vs simpler canvas).
- **Stronger technical credibility section** (dedicated beautiful code sample + network explanation).
- **Better hierarchy and breathing room** while remaining dense with proof.
- Less "marketing-speak", more "we ship real infrastructure" tone.
- Complete runnable delight (interactions feel intentional).

### 6. What the Site Itself Shows
- Clean marketing site with excellent scannability (benchmarks, pricing cards, gallery grid).
- Theme toggle, minimal nav.
- High signal-to-noise.
- Consistent with the outputs it produces.

## Anti-Patterns (Avoid for Greg-like)
- Overly verbose or generic feature lists.
- Emoji-heavy icons instead of geometric + text tags (Greg uses both judiciously but geometric for features).
- Plain pre/code without nice window treatment.
- Weak hero visual or missing interactive element when the product is "network/grid".
- Numbers that don't feel impressive or precise.
- Cluttered nav or missing strong CTAs early.

## Prompting Heuristics That Seem to Work
- "Create a complete, self-contained, production-polished landing page for [frontier tech product]..."
- Include specifics: "use // kickers, geometric unicode icons, a beautiful interactive canvas globe/HUD, styled code demo, big credible metrics..."
- "Match the visual and narrative quality of the Meridian demo from greg-2-ultra."
- Ask for runnable single-file HTML+CSS+JS.

## Measurement
- crofbench 1.0 dimensions: UI design quality, code correctness, visual polish.
- Human: "Does this feel like it could be the winning entry in a same-prompt gallery?"

## Sources for Refinement
- `data/examples/meridian-greg.html` (primary)
- Screenshots: greg-meridian.png (winning), opus-comparison.png, etc.
- Live pages on greg.crof.ai for more generations.

This doc will be updated as we extract more examples and run generations.
