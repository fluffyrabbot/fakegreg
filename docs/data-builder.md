# Greg UI Data Builder Notes

## Goal
Curate high-quality (prompt → Greg output) pairs to improve the reproduction and enhancement skills over time.

## Recommended Process
1. Use real Greg (greg-2-ultra or super) via the CrofAI API for new generations.
2. Use prompts modeled on the gallery (same prompt for fair comparisons, or targeted landing/dashboard prompts).
3. Save:
   - The exact prompt used
   - The raw HTML/TSX output
   - A screenshot (use browse or local render)
   - Optional: analysis notes
4. Add the best ones to:
   - `data/examples/`
   - Skill `references/` folders (for few-shot loading)
5. Periodically distill new patterns back into `SENSIBILITIES.md` and the core skill prompts.

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

## Future Tooling Ideas
- Simple script that calls the API, saves HTML + screenshot.
- Eval harness that runs several prompts and produces average "greg score" using the analyzer.
- Visual diff against previous best seeds.

Start manually, then automate.
