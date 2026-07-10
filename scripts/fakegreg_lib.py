#!/usr/bin/env python3

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPECIMENS_DIR = ROOT / "data" / "specimens"

REQUIRED_MANIFEST_KEYS = {
    "id",
    "title",
    "kind",
    "surface",
    "prompt_path",
    "generator",
    "artifacts",
    "scores",
    "acceptance",
    "tags",
}

REQUIRED_SCORE_KEYS = {
    "overall",
    "design_quality",
    "visual_polish",
    "narrative_copy",
    "implementation",
    "greg_fidelity",
}

ANALYSIS_PATTERNS = {
    "greg_ui_analysis_v1": [
        r"\*\*Overall Greg Score: \d+/100\*\*",
        r"## Breakdown",
        r"## Strengths",
        r"## Greg-Style Improvement Opportunities",
        r"## Suggested Next Prompt",
        r"Verdict:",
    ]
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def discover_specimens() -> dict[str, tuple[Path, dict[str, Any]]]:
    specimens: dict[str, tuple[Path, dict[str, Any]]] = {}
    for manifest_path in sorted(SPECIMENS_DIR.glob("*/manifest.json")):
        manifest = load_json(manifest_path)
        specimens[manifest["id"]] = (manifest_path.parent, manifest)
    return specimens


def count_kickers(text: str) -> int:
    return len(re.findall(r"// [a-zA-Z]", text))


def has_hero(text: str) -> bool:
    return bool(re.search(r"<header|class(Name)?=\"[^\"]*hero|<h1", text))


def has_features(text: str) -> bool:
    headings = re.findall(r"<h3|<article|class(Name)?=\"[^\"]*(feat|card)", text)
    return len(headings) >= 3


def has_code_block(text: str) -> bool:
    return "<pre" in text or "<code" in text


def has_metrics(text: str) -> bool:
    if re.search(r"class(Name)?=\"[^\"]*(num|stat|metric|big)", text):
        return True
    numeric_tokens = re.findall(r"\b\d+(?:\.\d+)?(?:[TMBK])?(?:ms|%| regions| countries| / day| / month)?\b", text)
    return len(numeric_tokens) >= 3


def has_cta(text: str) -> bool:
    return bool(
        re.search(
            r"Request access|Get access|Get started|Open quickstart|Open regional drilldown|Talk to the team|Book a demo|Start",
            text,
        )
    )


def has_canvas_or_svg(text: str) -> bool:
    return "<canvas" in text or "<svg" in text


SECTION_CHECKS = {
    "hero": has_hero,
    "features": has_features,
    "code_block": has_code_block,
    "metrics": has_metrics,
    "cta": has_cta,
}

VISUAL_CHECKS = {
    "canvas_or_svg": has_canvas_or_svg,
}


def validate_analysis_shape(analysis_text: str, shape_name: str) -> list[str]:
    patterns = ANALYSIS_PATTERNS.get(shape_name, [])
    failures = []
    for pattern in patterns:
        if not re.search(pattern, analysis_text, re.MULTILINE):
            failures.append(f"analysis missing pattern: {pattern}")
    return failures


def choose_rendered_artifact(specimen_dir: Path, manifest: dict[str, Any]) -> Path:
    artifacts = manifest["artifacts"]
    rendered = artifacts.get("rendered_output_path")
    raw = artifacts["raw_output_path"]
    return specimen_dir / (rendered or raw)


def run_acceptance(specimen_dir: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "id": manifest.get("id"),
        "passed": True,
        "errors": [],
        "checks": {},
    }

    missing_keys = sorted(REQUIRED_MANIFEST_KEYS - set(manifest.keys()))
    if missing_keys:
        result["errors"].append(f"manifest missing keys: {', '.join(missing_keys)}")

    score_keys = set(manifest.get("scores", {}).keys())
    missing_score_keys = sorted(REQUIRED_SCORE_KEYS - score_keys)
    if missing_score_keys:
        result["errors"].append(f"scores missing keys: {', '.join(missing_score_keys)}")

    artifacts = manifest.get("artifacts", {})
    prompt_path = specimen_dir / manifest.get("prompt_path", "")
    raw_output_path = specimen_dir / artifacts.get("raw_output_path", "")
    analysis_path = specimen_dir / artifacts.get("analysis_path", "")
    notes_path = specimen_dir / artifacts.get("notes_path", "")
    screenshot_path = specimen_dir / artifacts.get("screenshot_path", "")
    rendered_path = choose_rendered_artifact(specimen_dir, manifest)

    for label, path in {
        "prompt": prompt_path,
        "raw_output": raw_output_path,
        "rendered_output": rendered_path,
        "analysis": analysis_path,
        "notes": notes_path,
        "screenshot": screenshot_path,
    }.items():
        exists = path.exists()
        result["checks"][f"{label}_exists"] = exists
        if not exists:
            result["errors"].append(f"missing {label}: {path.relative_to(ROOT)}")

    if result["errors"]:
        result["passed"] = False
        return result

    rendered_text = rendered_path.read_text(encoding="utf-8")
    analysis_text = analysis_path.read_text(encoding="utf-8")
    acceptance = manifest["acceptance"]

    for section in acceptance.get("required_sections", []):
        checker = SECTION_CHECKS.get(section)
        passed = bool(checker and checker(rendered_text))
        result["checks"][f"section:{section}"] = passed
        if not passed:
            result["errors"].append(f"missing required section: {section}")

    for visual in acceptance.get("required_visuals", []):
        checker = VISUAL_CHECKS.get(visual)
        passed = bool(checker and checker(rendered_text))
        result["checks"][f"visual:{visual}"] = passed
        if not passed:
            result["errors"].append(f"missing required visual: {visual}")

    kickers = count_kickers(rendered_text)
    min_kickers = acceptance.get("minimum_kickers", 0)
    result["checks"]["minimum_kickers"] = kickers >= min_kickers
    result["checks"]["kicker_count"] = kickers
    if kickers < min_kickers:
        result["errors"].append(f"expected at least {min_kickers} kickers, found {kickers}")

    analysis_failures = validate_analysis_shape(analysis_text, acceptance.get("analysis_shape", ""))
    result["checks"]["analysis_shape"] = not analysis_failures
    result["errors"].extend(analysis_failures)

    score = float(manifest["scores"]["overall"])
    min_score = acceptance.get("minimum_score", 0)
    max_score = acceptance.get("maximum_score")
    result["checks"]["minimum_score"] = score >= min_score
    if score < min_score:
        result["errors"].append(f"score {score} below minimum {min_score}")

    if max_score is not None:
        result["checks"]["maximum_score"] = score <= max_score
        if score > max_score:
            result["errors"].append(f"score {score} above maximum {max_score}")

    result["passed"] = not result["errors"]
    result["score"] = score
    result["surface"] = manifest.get("surface")
    result["analysis_path"] = str(analysis_path.relative_to(ROOT))
    result["output_path"] = str(rendered_path.relative_to(ROOT))
    return result
