---
name: greg-ui-analyze
description: >
  Analyze any UI (HTML/TSX/code, description, or screenshot path) against Greg-2 sensibilities from greg.crof.ai.
  Score on crofbench-style dimensions and give concrete improvement suggestions. Use after greg-direct-repro or on any candidate UI.
  Triggers: "analyze like greg", "greg critique", "score this ui greg", "crofbench", "greg polish check", "greg review".
  Slash: /greg-ui-analyze
version: 0.1.0
author: fakegreg
---

# Greg UI Analyzer / Critic Skill

Compare any UI artifact against the observed strengths of Greg 2 (crofbench 1.0 leader).

## How to Use
1. Load repo-root references first:
   - `references/SENSIBILITIES.md`
   - `references/STYLE_PRIMITIVES.md`
   - `references/PAGE_ARCHETYPES.md`
   - `references/ANTI_EXAMPLES.md`
   - `references/meridian-greg.html` (the target standard)
   - Any provided screenshot or candidate code.

2. The user will give you:
   - HTML/TSX/React code
   - Or a description
   - Or path to screenshot / image reference
   - (Optional) the original prompt used

3. Perform a structured critique:

## Scoring Rubric (inspired by crofbench 1.0)
Rate 0-100 overall and break down:

- **Design Quality / Hierarchy** (25): Narrative clarity, section flow, heading strength, kicker usage, visual breathing room.
- **Visual Polish & Delight** (25): Micro-details, icons (geometric preference), canvas/interactivity, code presentation, metrics display, button treatments, subtle layers (rings, HUD, glow).
- **Narrative & Copy Strength** (20): Positioning power, specificity of claims, absence of fluff, use of // kickers and tags.
- **Implementation / Code Correctness implied** (15): Clean structure, semantic HTML, self-contained runnable feel, reasonable responsiveness, no obvious anti-patterns.
- **Greg Fidelity** (15): How closely it matches Meridian-level taste vs generic or Opus-like outputs.

Overall: weighted average or holistic 0-100 "Would this win the gallery?"

## Output Format (always use)
```markdown
## Greg UI Analysis

**Overall Greg Score: XX/100**

### Breakdown
- Design Quality/Hierarchy: XX/100 — ...
- Visual Polish & Delight: XX/100 — ...
- Narrative & Copy: XX/100 — ...
- Code/Implementation: XX/100 — ...
- Greg Fidelity: XX/100 — ...

### Strengths (Greg-like)
- bullet list of what already feels Meridian/Greg

### Greg-Style Improvement Opportunities
1. Specific actionable change + why (reference Meridian or sensibilities)
2. ...
3. Prioritize 1-2 highest impact.

### Suggested Next Prompt (for greg-direct-repro or enhancer)
"..."
```

## Calibration bands
When scoring corpus specimens, stay honest to the calibration ranges in `data/calibration/bands.json`:
- Meridian-class gold references should land in the high 90s.
- Strong candidates typically 80–92.
- Anti-examples must stay low (generally ≤55 synthetic, ≤70 non-Greg gallery peers).
If your score would break a known band for a labeled specimen, re-check whether you over-weighted polish without proof density (or under-weighted a true Meridian-level page).

## Pairwise mode (forced choice)
When the user asks to compare two UIs, or provides A/B candidates:
1. Do **not** only emit two independent absolute scores.
2. Make a forced choice: which is more Greg-like?
3. Use this output block:

```markdown
## Pairwise Greg Preference

**Winner:** A|B
**Confidence:** high|medium|low
**Margin (qualitative):** clear|slight

### Why winner is more Greg-like
- proof density / narrative conviction
- visual anchor quality
- micro-detail and non-generic texture
- hierarchy and section rhythm

### What the loser still does well
- ...

### Absolute scores (secondary)
- A: XX/100
- B: XX/100
```

Prefer the candidate with stronger proof, sharper thesis, better visual anchor, and less template-generic copy — even if the loser is “prettier” in a bland way.

Corpus pairs for regression live in `data/pairwise/core.json` and are checked by `python3 scripts/fakegreg_calibrate.py`.

## Additional Rules
- Be precise and cite patterns from SENSIBILITIES.md or the Meridian example.
- When a screenshot is referenced, describe observed visual differences.
- If comparing to another model (Opus etc.), note the difference in taste.
- End with a single-sentence verdict: "This is already strong Greg territory" / "Close but needs X" / "Needs major Greg treatment".
- Prefer constructive over harsh.
- When writing scores into specimen manifests, set `score_meta.scorer` to `skill` (or `human` if you are only drafting for a human to confirm).

## Example Triggers
- `/greg-ui-analyze [paste some generated HTML or path to image]`
- "Score this landing page against greg sensibilities"
- "Run crofbench-style review on the code I just generated"

## Integration with Sequence
- Best used immediately after greg-direct-repro output.
- Feed suggestions into the iterative enhancer skill.
- Use to curate high-quality new seeds for the direct skill.

Always load the references before scoring.
