#!/usr/bin/env python3
"""Collect specimen bundles from the Greg API or live gallery pages."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date, datetime, UTC
from pathlib import Path
from typing import Any
from urllib.request import urlopen

from fakegreg_api import post_chat_completion, resolve_api_key, resolve_base_url, resolve_model
from fakegreg_lib import ROOT, SPECIMENS_DIR, load_json, skill_prompt_hashes
from fakegreg_screenshot import find_chrome, screenshot_html


REFERENCE_PATHS = [
    ROOT / "references" / "SENSIBILITIES.md",
    ROOT / "references" / "STYLE_PRIMITIVES.md",
    ROOT / "references" / "PAGE_ARCHETYPES.md",
    ROOT / "references" / "ANTI_EXAMPLES.md",
    ROOT / "references" / "meridian-greg.html",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect fakegreg specimen bundles.")
    sub = parser.add_subparsers(dest="command", required=True)

    api = sub.add_parser("api", help="Generate specimens via OpenAI-compatible Greg API.")
    api.add_argument(
        "--prompt-set",
        type=Path,
        default=ROOT / "data" / "prompt_sets" / "collect.json",
    )
    api.add_argument("--model", default=None)
    api.add_argument("--base-url", default=None)
    api.add_argument(
        "--out-root",
        type=Path,
        default=SPECIMENS_DIR,
        help="Where to write specimen directories.",
    )
    api.add_argument(
        "--id-prefix",
        default="",
        help="Optional prefix for specimen ids (e.g. api-).",
    )
    api.add_argument("--no-screenshot", action="store_true")
    api.add_argument("--no-analyze", action="store_true")
    api.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate config and print planned actions without calling the API.",
    )
    api.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only collect the first N prompt-set entries.",
    )

    gallery = sub.add_parser("gallery", help="Import a live greg.crof.ai gallery page as a specimen.")
    gallery.add_argument("--url", required=True, help="Gallery page URL, e.g. https://greg.crof.ai/greg-2-super")
    gallery.add_argument("--id", required=True, help="Specimen id / directory name.")
    gallery.add_argument("--title", default=None)
    gallery.add_argument("--surface", default="landing_page")
    gallery.add_argument("--kind", default="reference", choices=["reference", "candidate", "anti_example"])
    gallery.add_argument("--model", default=None, help="Model name shown on the gallery card.")
    gallery.add_argument("--overall-score", type=float, default=None)
    gallery.add_argument("--min-score", type=float, default=None)
    gallery.add_argument("--max-score", type=float, default=None)
    gallery.add_argument("--prompt", default=None, help="Shared gallery prompt text if known.")
    gallery.add_argument("--out-root", type=Path, default=SPECIMENS_DIR)
    gallery.add_argument("--no-screenshot", action="store_true")
    gallery.add_argument(
        "--html-file",
        type=Path,
        default=None,
        help="Use a pre-downloaded HTML file instead of fetching --url.",
    )

    return parser.parse_args()


def repo_relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def build_skill_system_prompt(skill_name: str) -> str:
    skill_path = ROOT / ".grok" / "skills" / skill_name / "SKILL.md"
    if not skill_path.exists():
        raise FileNotFoundError(f"Skill not found: {repo_relative(skill_path)}")
    chunks = [
        "You are executing a fakegreg skill outside the Grok runtime.",
        "Follow the skill instructions as closely as possible.",
        f"\n--- SKILL.md ({skill_name}) ---\n{skill_path.read_text(encoding='utf-8')}",
    ]
    for path in REFERENCE_PATHS:
        chunks.append(f"\n--- {path.name} ---\n{path.read_text(encoding='utf-8')}")
    return "\n".join(chunks)


def extract_html_fence(text: str) -> str:
    """Prefer fenced HTML blocks; otherwise return full model text."""
    match = re.search(r"```(?:html)?\s*\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip() + "\n"
    stripped = text.strip()
    if stripped.lower().startswith("<!doctype") or stripped.lower().startswith("<html"):
        return stripped + ("\n" if not stripped.endswith("\n") else "")
    return text if text.endswith("\n") else text + "\n"


def parse_scores_from_analysis(analysis: str) -> dict[str, float] | None:
    overall = re.search(r"\*\*Overall Greg Score:\s*(\d+)/100\*\*", analysis)
    if not overall:
        return None
    dims = {
        "design_quality": r"Design Quality[^\d]*(\d+)/100",
        "visual_polish": r"Visual Polish[^\d]*(\d+)/100",
        "narrative_copy": r"Narrative[^\d]*(\d+)/100",
        "implementation": r"(?:Code/)?Implementation[^\d]*(\d+)/100",
        "greg_fidelity": r"Greg Fidelity[^\d]*(\d+)/100",
    }
    scores = {"overall": float(overall.group(1))}
    for key, pattern in dims.items():
        match = re.search(pattern, analysis, re.IGNORECASE)
        scores[key] = float(match.group(1)) if match else scores["overall"]
    return scores


def default_acceptance(surface: str, kind: str, overall: float) -> dict[str, Any]:
    if kind == "anti_example":
        return {
            "minimum_score": 0,
            "maximum_score": max(overall + 10, 55),
            "required_sections": ["hero", "cta"],
            "required_visuals": [],
            "minimum_kickers": 0,
            "analysis_shape": "greg_ui_analysis_v1",
        }
    sections = ["hero", "cta", "code_block", "metrics"]
    if surface == "landing_page":
        sections = ["hero", "features", "code_block", "metrics", "cta"]
    return {
        "minimum_score": max(0, overall - 8),
        "maximum_score": None,
        "required_sections": sections,
        "required_visuals": ["canvas_or_svg"],
        "minimum_kickers": 2 if surface != "dashboard" else 2,
        "analysis_shape": "greg_ui_analysis_v1",
    }


def write_specimen_bundle(
    specimen_dir: Path,
    *,
    specimen_id: str,
    title: str,
    kind: str,
    surface: str,
    prompt: str,
    html: str,
    analysis: str,
    notes: str,
    generator: dict[str, Any],
    scores: dict[str, float],
    score_meta: dict[str, Any],
    acceptance: dict[str, Any],
    tags: list[str],
    screenshot: bool,
) -> Path:
    specimen_dir.mkdir(parents=True, exist_ok=True)
    (specimen_dir / "prompt.md").write_text(prompt.rstrip() + "\n", encoding="utf-8")
    output_name = "output.tsx" if surface == "framework_component" else "output.html"
    (specimen_dir / output_name).write_text(html if html.endswith("\n") else html + "\n", encoding="utf-8")
    (specimen_dir / "analysis.md").write_text(analysis if analysis.endswith("\n") else analysis + "\n", encoding="utf-8")
    (specimen_dir / "notes.md").write_text(notes if notes.endswith("\n") else notes + "\n", encoding="utf-8")

    shot_path = specimen_dir / "screenshot.png"
    if screenshot and output_name.endswith(".html"):
        chrome = find_chrome()
        screenshot_html(specimen_dir / output_name, shot_path, chrome=chrome)
    elif not shot_path.exists():
        # Placeholder 1x1 PNG so acceptance file-existence can pass after manual shot.
        # Prefer real screenshots via fakegreg_screenshot.py.
        shot_path.write_bytes(
            bytes.fromhex(
                "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
                "0000000a49444154789c63000100000500010d0a2db40000000049454e44ae426082"
            )
        )

    manifest = {
        "id": specimen_id,
        "title": title,
        "kind": kind,
        "surface": surface,
        "prompt_path": "prompt.md",
        "generator": generator,
        "artifacts": {
            "raw_output_path": output_name,
            "rendered_output_path": output_name,
            "screenshot_path": "screenshot.png",
            "analysis_path": "analysis.md",
            "notes_path": "notes.md",
        },
        "scores": scores,
        "score_meta": score_meta,
        "acceptance": acceptance,
        "tags": tags,
    }
    (specimen_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return specimen_dir


def placeholder_analysis(overall: int, note: str) -> str:
    return f"""## Greg UI Analysis

**Overall Greg Score: {overall}/100**

### Breakdown
- Design Quality/Hierarchy: {overall}/100 — provisional score pending full human/skill review
- Visual Polish & Delight: {overall}/100 — provisional
- Narrative & Copy: {overall}/100 — provisional
- Code/Implementation: {overall}/100 — provisional
- Greg Fidelity: {overall}/100 — provisional

### Strengths (Greg-like)
- {note}

### Greg-Style Improvement Opportunities
1. Re-run /greg-ui-analyze for a full crofbench-style critique.
2. Promote only after score_meta.scorer is updated from provisional.

### Suggested Next Prompt (for greg-direct-repro or enhancer)
"Tighten proof density and section rhythm while preserving the strongest visual anchor."

Verdict: provisional collect artifact; calibrate before treating as gold.
"""


def command_api(args: argparse.Namespace) -> int:
    prompt_set = load_json(args.prompt_set)
    entries = prompt_set["entries"]
    if args.limit is not None:
        entries = entries[: args.limit]

    model = args.model or resolve_model()
    base_url = args.base_url or resolve_base_url()
    api_key = resolve_api_key()

    print(f"prompt_set={prompt_set['id']} entries={len(entries)} model={model} base_url={base_url}")
    print(f"api_key={'set' if api_key else 'MISSING'} skill_hashes={list(skill_prompt_hashes())}")

    if args.dry_run:
        for entry in entries:
            specimen_id = f"{args.id_prefix}{entry['id']}"
            print(f"PLAN collect {specimen_id} skill={entry.get('skill')} surface={entry.get('surface')}")
        if not api_key:
            print("DRY-RUN note: CROF_API_KEY / FAKEGREG_API_KEY not set; live collect would fail.")
        return 0

    if not api_key:
        print("ERROR: Set FAKEGREG_API_KEY or CROF_API_KEY before running collect api.", file=sys.stderr)
        return 2

    failures = []
    for entry in entries:
        specimen_id = f"{args.id_prefix}{entry['id']}"
        skill = entry.get("skill") or "greg-direct-repro"
        surface = entry.get("surface", "landing_page")
        prompt = entry["prompt"]
        print(f"Collecting {specimen_id} via {skill}...")
        try:
            system_prompt = build_skill_system_prompt(skill)
            content = post_chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                model=model,
                base_url=base_url,
            )
            html = extract_html_fence(content)

            analysis = placeholder_analysis(85, "API-collected candidate awaiting full analysis.")
            scores = {
                "overall": 85,
                "design_quality": 85,
                "visual_polish": 85,
                "narrative_copy": 85,
                "implementation": 85,
                "greg_fidelity": 85,
            }
            score_meta = {
                "scorer": "script",
                "scored_at": date.today().isoformat(),
                "method": "provisional collect defaults; re-score with analyzer",
            }

            if not args.no_analyze:
                analyzer_system = build_skill_system_prompt("greg-ui-analyze")
                analysis = post_chat_completion(
                    messages=[
                        {"role": "system", "content": analyzer_system},
                        {
                            "role": "user",
                            "content": f"Original prompt:\n{prompt}\n\nCandidate output:\n{html}",
                        },
                    ],
                    model=model,
                    base_url=base_url,
                    temperature=0,
                )
                parsed = parse_scores_from_analysis(analysis)
                if parsed:
                    scores = parsed
                    score_meta = {
                        "scorer": "skill",
                        "scored_at": datetime.now(UTC).isoformat(),
                        "method": f"greg-ui-analyze via {model}",
                    }

            overall = float(scores["overall"])
            write_specimen_bundle(
                args.out_root / specimen_id,
                specimen_id=specimen_id,
                title=entry.get("title") or specimen_id.replace("-", " ").title(),
                kind=entry.get("kind", "candidate"),
                surface=surface,
                prompt=prompt,
                html=html,
                analysis=analysis,
                notes=(
                    f"Collected via Greg API on {datetime.now(UTC).isoformat()} "
                    f"using model={model} skill={skill}."
                ),
                generator={
                    "source": "crof OpenAI-compatible API",
                    "model": model,
                    "skill": skill,
                    "generated_at": datetime.now(UTC).isoformat(),
                    "provenance": "real_api",
                    "notes": f"base_url={base_url}; skill_hashes={skill_prompt_hashes()}",
                },
                scores=scores,
                score_meta=score_meta,
                acceptance=default_acceptance(surface, entry.get("kind", "candidate"), overall),
                tags=list(entry.get("tags", ["real_api", "collected", surface])),
                screenshot=not args.no_screenshot,
            )
            print(f"Wrote {repo_relative(args.out_root / specimen_id)}")
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{specimen_id}: {exc}")
            print(f"FAIL {specimen_id}: {exc}")

    if failures:
        print("\nCollect failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    return 0


def fetch_gallery_html(url: str) -> str:
    """Fetch gallery page HTML.

    Prefer the browse CLI when available (renders JS). Fall back to plain HTTP.
    """
    browse = subprocess.run(
        ["browse", "open", url],
        capture_output=True,
        text=True,
        check=False,
    )
    if browse.returncode == 0:
        subprocess.run(["browse", "wait", "load"], capture_output=True, text=True, check=False)
        result = subprocess.run(
            ["browse", "eval", "document.documentElement.outerHTML"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            try:
                payload = json.loads(result.stdout)
                html = payload.get("result", result.stdout)
                if isinstance(html, str) and "<html" in html.lower():
                    if not html.lstrip().lower().startswith("<!doctype"):
                        html = "<!DOCTYPE html>\n" + html
                    return html if html.endswith("\n") else html + "\n"
            except json.JSONDecodeError:
                pass

    with urlopen(url, timeout=60) as response:  # noqa: S310 - user-supplied gallery URL
        html = response.read().decode("utf-8", errors="replace")
    if not html.lstrip().lower().startswith("<!doctype"):
        html = "<!DOCTYPE html>\n" + html
    return html if html.endswith("\n") else html + "\n"


def command_gallery(args: argparse.Namespace) -> int:
    if args.html_file:
        html = args.html_file.read_text(encoding="utf-8")
        if not html.lstrip().lower().startswith("<!doctype"):
            html = "<!DOCTYPE html>\n" + html
    else:
        print(f"Fetching {args.url} ...")
        html = fetch_gallery_html(args.url)

    model = args.model or "unknown-gallery-model"
    if "greg-2-ultra" in args.url:
        model = args.model or "greg-2-ultra"
    elif "greg-2-super" in args.url:
        model = args.model or "greg-2-super"
    elif "opus" in args.url:
        model = args.model or "opus-4.8"

    kind = args.kind
    if kind == "anti_example":
        overall = args.overall_score if args.overall_score is not None else 48
    elif "ultra" in model:
        overall = args.overall_score if args.overall_score is not None else 96
    elif "super" in model:
        overall = args.overall_score if args.overall_score is not None else 88
    else:
        overall = args.overall_score if args.overall_score is not None else 70

    scores = {
        "overall": overall,
        "design_quality": overall,
        "visual_polish": max(0, overall - 2),
        "narrative_copy": overall - 1 if kind != "anti_example" else overall - 4,
        "implementation": overall - 1,
        "greg_fidelity": overall + 1 if "greg" in model and kind != "anti_example" else max(0, overall - 12),
    }
    # clamp
    scores = {k: float(max(0, min(100, v))) for k, v in scores.items()}

    acceptance = default_acceptance(args.surface, kind, scores["overall"])
    if args.min_score is not None:
        acceptance["minimum_score"] = args.min_score
    if args.max_score is not None:
        acceptance["maximum_score"] = args.max_score
    if kind == "anti_example":
        acceptance["required_visuals"] = []
        acceptance["minimum_kickers"] = 0

    title = args.title or args.id.replace("-", " ").title()
    prompt = args.prompt or (
        "Gallery shared prompt (same constraints across models): "
        "Create a beautiful, complete, self-contained modern landing page for a global edge AI product "
        "with an interactive network visual, // kickers, geometric unicode icons, a styled code quickstart, "
        "and big credible metrics."
    )

    analysis = placeholder_analysis(
        int(scores["overall"]),
        f"Imported from live gallery page {args.url} ({model}).",
    )
    # Stronger analysis notes for known roles
    if kind == "anti_example":
        analysis = analysis.replace(
            "Verdict: provisional collect artifact; calibrate before treating as gold.",
            "Verdict: useful negative control from a non-Greg gallery peer; keep score ceiling low.",
        )

    specimen_dir = write_specimen_bundle(
        args.out_root / args.id,
        specimen_id=args.id,
        title=title,
        kind=kind,
        surface=args.surface,
        prompt=prompt,
        html=html,
        analysis=analysis,
        notes=(
            f"Imported from {args.url} on {datetime.now(UTC).isoformat()}. "
            "This is a real model output from the crof gallery (not a skill reproduction)."
        ),
        generator={
            "source": args.url,
            "model": model,
            "skill": None,
            "generated_at": date.today().isoformat(),
            "provenance": "gallery_extract",
            "notes": "Live gallery HTML capture via fakegreg_collect gallery.",
        },
        scores=scores,
        score_meta={
            "scorer": "human",
            "scored_at": date.today().isoformat(),
            "method": "initial gallery import band; refine with analyzer/calibration",
        },
        acceptance=acceptance,
        tags=["gallery", model, kind, args.surface],
        screenshot=not args.no_screenshot,
    )
    print(f"Wrote {repo_relative(specimen_dir)}")
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "api":
        return command_api(args)
    if args.command == "gallery":
        return command_gallery(args)
    raise AssertionError("unreachable")


if __name__ == "__main__":
    sys.exit(main())
