---
name: greg-ui-landing
description: >
  Specialized direct reproduction for Greg-2 style product marketing landing pages (hero + interactive viz + // kickers + features + metrics + CTA) that win gallery comparisons.
  Use for "landing page", "marketing site", "product page like Meridian", global-tech or AI infrastructure demos.
  Slash: /greg-ui-landing
version: 0.1.0
author: fakegreg
---

# Greg UI Landing / Product Page Specialist

This variant is tuned specifically for the gallery-winning style: high-signal product landing pages like the Meridian (greg-2-ultra) demo.

## When to Prefer This Over greg-direct-repro
- The request is explicitly for a landing / marketing / "front page" for a technical product.
- You want the exact structure that performs well in same-prompt gallery comparisons (hero + globe/viz + stats + // sections + code block + impact + CTA).

## Fixed Patterns (internalize from Meridian)
- Kicker in hero + // kickers for major sections.
- Left text / right strong visual (canvas globe or equivalent viz) in hero.
- Precise feature grid with geometric icons + `.tag`.
- Dedicated beautiful code/API quickstart window.
- Big stat/impact numbers.
- Final centered CTA card.
- Frosted sticky nav with primary CTA.

## Instructions
1. Load references (meridian-greg.html + SENSIBILITIES.md) — same as direct.
2. Map the user's product description onto the Meridian template closely.
3. Generate a **complete single-file landing page**.
4. Include at minimum:
   - Hero with interactive or rich visual treatment.
   - 4 high-quality feature cards.
   - One styled code example section.
   - Production/impact metrics.
   - Strong final CTA.
5. Use Greg copy heuristics heavily (specific, credible, no English tax style claims).
6. After generation, recommend running greg-ui-analyze and then greg-ui-enhance.

## Quickstart Usage
`/greg-ui-landing A new privacy-first global sync database called "MeshDB"`

## Output
Full runnable HTML (or framework equivalent) + note "This follows the Meridian/Greg landing template".

## Variants Inside This Family (future)
- Mobile-first landing
- Dashboard + landing hybrid
- With pricing table

Start here for the core gallery-style pages.
