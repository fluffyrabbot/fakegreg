---
name: greg-ui-enhance
description: >
  Iteratively refine any UI toward Greg-2 (greg.crof.ai) sensibilities using analysis + targeted improvements.
  Use for multi-pass enhancement after direct-repro or analyze. Triggers: "enhance with greg", "make this more greg", "iterate this ui greg style", "greg polish pass", "improve toward meridian".
  Slash: /greg-ui-enhance
version: 0.1.0
author: fakegreg
---

# Greg UI Iterative Enhancer

Multi-pass refinement loop that pushes any UI toward the quality level of the Greg-2 Meridian winner.

## Core Loop (follow every time)
1. **Load references**:
   - SENSIBILITIES.md
   - meridian-greg.html (the target)
2. Understand the current candidate (code or description or previous output).
3. Run an internal "greg-ui-analyze" pass (use the exact rubric and output format from the analyzer skill).
4. Produce one **focused, high-signal refinement pass**:
   - Fix the 1-3 highest-impact issues from the critique.
   - Apply specific Greg patterns (kickers, better copy, stronger visual treatment, improved code presentation, precise metrics, geometric icons, etc.).
   - Keep the output fully runnable / complete.
5. Optionally offer a second pass note or full re-output if the delta is large.
6. End with a short "Greg delta" summary:
   - What changed and why (tie back to sensibilities or Meridian).

## Rules
- Prefer surgical, high-leverage changes over full rewrites unless the base is very weak.
- Always preserve working functionality while elevating taste and polish.
- When adding visuals: prefer canvas + HUD + rings over generic divs when it fits "network / global / distributed" stories.
- Improve copy in parallel with layout (Greg is excellent at both).
- If user provides a screenshot or image path, describe what visual upgrades to make (more layers, better hierarchy, stronger contrast, etc.).
- Output the full improved code (or diff + full if large) so it is immediately usable.
- Stop after 1-2 strong passes unless user asks for more.

## Recommended Workflow (with the other skills)
1. Start with `/greg-direct-repro` (or raw generation).
2. `/greg-ui-analyze` the result.
3. `/greg-ui-enhance` the result (or the analysis output).
4. (Optional) Analyze again → one more enhance pass.
5. Curate the final into `data/examples/` or references/.

## Usage Examples
- `/greg-ui-enhance [paste mediocre landing page code] Make it Greg`
- "Take the dashboard I generated and run greg enhancement passes"
- "Iterate this toward the Meridian level of polish using greg-ui-enhance"

## Output Shape
- Full improved code block (runnable preferred).
- Short Greg Delta section.
- Suggestion for next use of analyzer if more passes desired.

This skill is the "refiner" in the sequence. Combine with direct repro for best results.
