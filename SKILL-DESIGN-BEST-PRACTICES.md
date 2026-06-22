# Skill Design Best Practices (Synthesized Meta-Research)

This document captures distilled best practices for designing high-quality Grok skills (`.grok/skills/*/SKILL.md`), drawn from:

- Official Grok user guide (`~/.grok/docs/user-guide/08-skills.md`)
- High-quality bundled and community skills (check-work, code-review, create-skill, help, awesome-grok-build examples)
- Anthropic Agent Skills architecture and engineering guidance (Grok has strong compatibility with the format and patterns)
- Community discussions and starter kits (e.g. awesome-grok-build)

## Core Principles

1. **Specificity wins** — The `description` field is the single most important piece for auto-invocation and discoverability.
2. **Progressive disclosure** — Give the model just enough context up front (name + description in system prompt). Load full details + references only when relevant.
3. **Actionable & focused** — One skill = one clear workflow or expertise area. Concrete numbered steps > prose.
4. **Agent-perspective design** — Write instructions the agent can follow directly. Reference tools by exact name. Provide examples.
5. **Test-driven** — Skills should be invoked and verified in real sessions before relying on auto-triggering.
6. **Simplicity + composability** — Prefer many small focused skills over one giant one. Skills should compose well (e.g. direct-repro → analyze → enhance).
7. **Version & scope** — Project-scoped skills (`.grok/skills/`) belong in git. Add `version` and `author`.

## Frontmatter

```yaml
---
name: my-skill-name          # lowercase, hyphens, 2-64 chars. Directory name is fallback.
description: >
  Clear sentence of what it does.
  Include trigger phrases and use cases.
  "Use when the user wants X or asks for /my-skill"
metadata:
  short-description: "One-line for menus/inspect"
  # optional: version, author
version: 1.0.0
author: fakegreg
# disable-model-invocation: true   # Only allow explicit /slash
# allowed-tools: "run_terminal_command, search_replace, read_file"
# argument-hint: "the thing to operate on"
---
```

**Description formula** (highly recommended):
> [What the skill does in 1 sentence]. Use when [trigger scenarios]. Triggers: "phrase1", "phrase2", "/command".

Make it rich enough that the model can confidently decide to load the skill.

## Body Structure (Recommended Pattern)

- Short title / one-line purpose
- ## Usage (slash command + arguments)
- ## Steps or ## Workflow (numbered, imperative)
- ## Core Prompt / VERIFIER PROMPT (for complex or subagent skills)
- ## Example Prompts (copy-paste ready)
- ## Output Format (exact structure expected)
- ## Guardrails / Non-Negotiables
- ## References (point to files in `references/`)
- (Optional) Mode guidance (Plan Mode, subagents, etc.)

**Tone**: Imperative, verb-first ("Read the file...", "Run...", "Produce..."). Avoid "you should" when possible.

Keep the main `SKILL.md` lean (target ~400-1500 words of instructions). Offload heavy reference material, schemas, or long examples into `references/`.

## Progressive Disclosure & Supporting Files

- `SKILL.md` — Core instructions + frontmatter
- `references/` — Long docs, full exemplars (e.g. `meridian-greg.html`, `SENSIBILITIES.md`), few-shot material
- `scripts/` — Executable helpers (prefer existing CLI tools when possible)
- `examples/` or `data/` — Concrete before/after or test cases
- `tests/` — Verification harnesses

In the skill body, tell the agent exactly when and how to read these (e.g. "Always start by loading references/meridian-greg.html").

## Writing for Auto-Invocation vs Explicit Use

- For automatic loading: description must paint a clear picture of *when* the skill applies.
- For slash-only (expert or dangerous skills): set `disable-model-invocation: true` and document the slash command heavily.
- Many powerful skills (strict reviews, certain verifiers) use `disable-model-invocation`.

## Common High-Quality Patterns Observed

- **Verification skills** (check-work style): Full trace reconstruction + state verification + build/test execution + explicit `VERDICT: PASS/FAIL`.
- **Review skills** (code-review style): Ambitious structural goals + numbered non-negotiables + "code judo" framing + specific output expectations.
- **Creation skills** (create-skill): Step-by-step interactive process with verification at the end.
- **Domain specialists** (python-expert, greg-ui-xxx): Strong example prompts + guardrails + "when to prefer this vs general tools".
- Community skills often include explicit "Grok Build Mode" section (Plan Mode recommendation, subagent usage).

## Testing & Iteration

1. Create the skill.
2. `grok inspect` to confirm discovery.
3. Invoke explicitly (`/skill-name ...`) in fresh sessions.
4. Test the natural language triggers you put in the description.
5. Observe whether the model loads the right amount of context.
6. Iterate: Ask the model itself (using the skill) to improve the skill.
7. For UI/creative skills: maintain a small set of gold references and run analyzer-style checks.

## Specific Recommendations for This Repo (fakegreg / Greg UI Skills)

- Always load `references/SENSIBILITIES.md` + the primary exemplar HTML/image early.
- Make the "Greg Fidelity" dimension explicit in analyzer/enhance skills.
- Provide ready-to-paste example prompts for common gallery-style tasks (landing pages, dashboards, etc.).
- Prefer self-contained runnable HTML+CSS+JS outputs for demos unless the user specifies a framework.
- Document how to use with real Greg API (for ground-truth data generation).
- Keep the direct-repro skill "pure" (faithful reproduction) and use separate skills for enhancement/iteration/variants.

## Checklist Before Committing a Skill

- [ ] Specific, trigger-rich `description`
- [ ] `name` matches directory and is valid
- [ ] Concrete numbered steps or clear workflow
- [ ] Example prompts included
- [ ] Output format specified when it matters
- [ ] References to supporting files use relative paths the agent can actually read
- [ ] Guardrails / edge cases addressed
- [ ] Tested with explicit invocation
- [ ] Tested with natural language that should trigger it
- [ ] Version/author if intended to be shared
- [ ] Added to README or appropriate index if part of a collection

## Sources & Further Reading

- `~/.grok/docs/user-guide/08-skills.md` (official Grok best practices section)
- Bundled skills in `~/.grok/skills/`
- https://github.com/DominikTobureto/awesome-grok-build (excellent real examples)
- Anthropic Agent Skills docs + "Equipping agents for the real world with Agent Skills" engineering post (progressive disclosure is the key idea)
- Community discussions on description semantics and cross-tool portability (Grok vs Claude skill descriptions can differ subtly)

Update this file as we learn more from using and improving the skills in this repo.
