# Canonical specimen bundles

Each specimen is a strict bundle with:

- `prompt.md`
- raw output (`output.html` or `output.tsx`)
- optional rendered artifact for framework specimens
- `screenshot.png`
- `analysis.md`
- `notes.md`
- `manifest.json`

The manifest shape is documented in `schemas/specimen.schema.json`.

This turns examples into portable, testable dataset entries instead of loose artifacts.
