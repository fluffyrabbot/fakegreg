#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPECIMENS_DIR = ROOT / "data" / "specimens"
SCHEMAS_DIR = ROOT / "schemas"
SKILLS_DIR = ROOT / ".grok" / "skills"
SPECIMEN_SCHEMA_PATH = SCHEMAS_DIR / "specimen.schema.json"

PROVENANCE_KINDS = {
    "real_api",
    "gallery_extract",
    "skill_reproduction",
    "synthetic_seed",
}

KIND_VALUES = {"reference", "candidate", "anti_example"}
SURFACE_VALUES = {
    "landing_page",
    "dashboard",
    "docs_home",
    "pricing_page",
    "framework_component",
}
SCORER_VALUES = {"human", "skill", "script"}
SECTION_VALUES = {"hero", "features", "code_block", "metrics", "cta"}
VISUAL_VALUES = {"canvas_or_svg"}
ANALYSIS_SHAPE_VALUES = {"greg_ui_analysis_v1"}

REQUIRED_MANIFEST_KEYS = {
    "id",
    "title",
    "kind",
    "surface",
    "prompt_path",
    "generator",
    "artifacts",
    "scores",
    "score_meta",
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

REQUIRED_GENERATOR_KEYS = {
    "source",
    "model",
    "skill",
    "provenance",
    "notes",
}

REQUIRED_ARTIFACT_KEYS = {
    "raw_output_path",
    "screenshot_path",
    "analysis_path",
    "notes_path",
}

REQUIRED_SCORE_META_KEYS = {
    "scorer",
    "scored_at",
}

REQUIRED_ACCEPTANCE_KEYS = {
    "minimum_score",
    "required_sections",
    "required_visuals",
    "minimum_kickers",
    "analysis_shape",
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


def path_display(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def discover_specimens() -> dict[str, tuple[Path, dict[str, Any]]]:
    specimens: dict[str, tuple[Path, dict[str, Any]]] = {}
    for manifest_path in sorted(SPECIMENS_DIR.glob("*/manifest.json")):
        manifest = load_json(manifest_path)
        specimens[manifest["id"]] = (manifest_path.parent, manifest)
    return specimens


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_text(path.read_text(encoding="utf-8"))


def skill_prompt_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    if not SKILLS_DIR.exists():
        return hashes
    for skill_dir in sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir()):
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            hashes[skill_dir.name] = sha256_file(skill_md)
    return hashes


def is_safe_relative_path(value: str) -> bool:
    if not value or value.startswith("/") or value.startswith("\\"):
        return False
    path = Path(value)
    if path.is_absolute():
        return False
    return ".." not in path.parts


def resolve_under(base: Path, relative: str) -> Path | None:
    if not is_safe_relative_path(relative):
        return None
    candidate = (base / relative).resolve()
    try:
        candidate.relative_to(base.resolve())
    except ValueError:
        return None
    return candidate


def _expect_type(errors: list[str], label: str, value: Any, expected: type | tuple[type, ...]) -> bool:
    if not isinstance(value, expected):
        type_name = (
            " | ".join(t.__name__ for t in expected)
            if isinstance(expected, tuple)
            else expected.__name__
        )
        errors.append(f"{label}: expected {type_name}, got {type(value).__name__}")
        return False
    return True


def _expect_number(errors: list[str], label: str, value: Any, *, minimum: float = 0, maximum: float = 100) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append(f"{label}: expected number, got {type(value).__name__}")
        return False
    if value < minimum or value > maximum:
        errors.append(f"{label}: {value} outside [{minimum}, {maximum}]")
        return False
    return True


def validate_manifest_schema(manifest: dict[str, Any]) -> list[str]:
    """Validate a specimen manifest against the repo schema contract (stdlib-only)."""
    errors: list[str] = []

    if not isinstance(manifest, dict):
        return ["manifest: expected object"]

    missing = sorted(REQUIRED_MANIFEST_KEYS - set(manifest.keys()))
    if missing:
        errors.append(f"manifest missing keys: {', '.join(missing)}")

    if "id" in manifest and _expect_type(errors, "id", manifest["id"], str) and not manifest["id"]:
        errors.append("id: must be non-empty")
    if "title" in manifest and _expect_type(errors, "title", manifest["title"], str) and not manifest["title"]:
        errors.append("title: must be non-empty")

    if "kind" in manifest and _expect_type(errors, "kind", manifest["kind"], str):
        if manifest["kind"] not in KIND_VALUES:
            errors.append(f"kind: invalid value {manifest['kind']!r}")

    if "surface" in manifest and _expect_type(errors, "surface", manifest["surface"], str):
        if manifest["surface"] not in SURFACE_VALUES:
            errors.append(f"surface: invalid value {manifest['surface']!r}")

    if "prompt_path" in manifest and _expect_type(errors, "prompt_path", manifest["prompt_path"], str):
        if not is_safe_relative_path(manifest["prompt_path"]):
            errors.append(f"prompt_path: unsafe relative path {manifest['prompt_path']!r}")

    generator = manifest.get("generator")
    if generator is not None and _expect_type(errors, "generator", generator, dict):
        missing_gen = sorted(REQUIRED_GENERATOR_KEYS - set(generator.keys()))
        if missing_gen:
            errors.append(f"generator missing keys: {', '.join(missing_gen)}")
        if "source" in generator and _expect_type(errors, "generator.source", generator["source"], str):
            if not generator["source"]:
                errors.append("generator.source: must be non-empty")
        if "model" in generator and _expect_type(errors, "generator.model", generator["model"], str):
            if not generator["model"]:
                errors.append("generator.model: must be non-empty")
        if "skill" in generator and generator["skill"] is not None:
            if not isinstance(generator["skill"], str) or not generator["skill"]:
                errors.append("generator.skill: must be string or null")
        if "generated_at" in generator and generator["generated_at"] is not None:
            if not isinstance(generator["generated_at"], str):
                errors.append("generator.generated_at: must be string or null")
        if "provenance" in generator and _expect_type(errors, "generator.provenance", generator["provenance"], str):
            if generator["provenance"] not in PROVENANCE_KINDS:
                errors.append(
                    f"generator.provenance: invalid value {generator['provenance']!r}; "
                    f"expected one of {sorted(PROVENANCE_KINDS)}"
                )
        if "notes" in generator and not _expect_type(errors, "generator.notes", generator["notes"], str):
            pass

    artifacts = manifest.get("artifacts")
    if artifacts is not None and _expect_type(errors, "artifacts", artifacts, dict):
        missing_art = sorted(REQUIRED_ARTIFACT_KEYS - set(artifacts.keys()))
        if missing_art:
            errors.append(f"artifacts missing keys: {', '.join(missing_art)}")
        for key in ("raw_output_path", "screenshot_path", "analysis_path", "notes_path", "rendered_output_path"):
            if key not in artifacts:
                continue
            value = artifacts[key]
            if key == "rendered_output_path" and value is None:
                continue
            if not isinstance(value, str) or not is_safe_relative_path(value):
                errors.append(f"artifacts.{key}: unsafe or invalid relative path {value!r}")

    scores = manifest.get("scores")
    if scores is not None and _expect_type(errors, "scores", scores, dict):
        missing_scores = sorted(REQUIRED_SCORE_KEYS - set(scores.keys()))
        if missing_scores:
            errors.append(f"scores missing keys: {', '.join(missing_scores)}")
        for key in REQUIRED_SCORE_KEYS:
            if key in scores:
                _expect_number(errors, f"scores.{key}", scores[key])

    score_meta = manifest.get("score_meta")
    if score_meta is not None and _expect_type(errors, "score_meta", score_meta, dict):
        missing_meta = sorted(REQUIRED_SCORE_META_KEYS - set(score_meta.keys()))
        if missing_meta:
            errors.append(f"score_meta missing keys: {', '.join(missing_meta)}")
        if "scorer" in score_meta and _expect_type(errors, "score_meta.scorer", score_meta["scorer"], str):
            if score_meta["scorer"] not in SCORER_VALUES:
                errors.append(f"score_meta.scorer: invalid value {score_meta['scorer']!r}")
        if "scored_at" in score_meta and _expect_type(errors, "score_meta.scored_at", score_meta["scored_at"], str):
            if not score_meta["scored_at"]:
                errors.append("score_meta.scored_at: must be non-empty")
        if "method" in score_meta and score_meta["method"] is not None:
            _expect_type(errors, "score_meta.method", score_meta["method"], str)

    acceptance = manifest.get("acceptance")
    if acceptance is not None and _expect_type(errors, "acceptance", acceptance, dict):
        missing_acc = sorted(REQUIRED_ACCEPTANCE_KEYS - set(acceptance.keys()))
        if missing_acc:
            errors.append(f"acceptance missing keys: {', '.join(missing_acc)}")
        if "minimum_score" in acceptance:
            _expect_number(errors, "acceptance.minimum_score", acceptance["minimum_score"])
        if "maximum_score" in acceptance and acceptance["maximum_score"] is not None:
            _expect_number(errors, "acceptance.maximum_score", acceptance["maximum_score"])
        if "minimum_kickers" in acceptance:
            value = acceptance["minimum_kickers"]
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                errors.append(f"acceptance.minimum_kickers: expected non-negative int, got {value!r}")
        if "required_sections" in acceptance and _expect_type(
            errors, "acceptance.required_sections", acceptance["required_sections"], list
        ):
            for section in acceptance["required_sections"]:
                if section not in SECTION_VALUES:
                    errors.append(f"acceptance.required_sections: unknown section {section!r}")
        if "required_visuals" in acceptance and _expect_type(
            errors, "acceptance.required_visuals", acceptance["required_visuals"], list
        ):
            for visual in acceptance["required_visuals"]:
                if visual not in VISUAL_VALUES:
                    errors.append(f"acceptance.required_visuals: unknown visual {visual!r}")
        if "analysis_shape" in acceptance and _expect_type(
            errors, "acceptance.analysis_shape", acceptance["analysis_shape"], str
        ):
            if acceptance["analysis_shape"] not in ANALYSIS_SHAPE_VALUES:
                errors.append(f"acceptance.analysis_shape: unknown shape {acceptance['analysis_shape']!r}")

    if "tags" in manifest and not _expect_type(errors, "tags", manifest["tags"], list):
        pass
    elif "tags" in manifest:
        for index, tag in enumerate(manifest["tags"]):
            if not isinstance(tag, str):
                errors.append(f"tags[{index}]: expected string")

    # Directory name should match id when present.
    return errors


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
    numeric_tokens = re.findall(
        r"\b\d+(?:\.\d+)?(?:[TMBK])?(?:ms|%| regions| countries| / day| / month)?\b",
        text,
    )
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

    schema_errors = validate_manifest_schema(manifest)
    result["checks"]["schema"] = not schema_errors
    result["errors"].extend(schema_errors)

    if manifest.get("id") and specimen_dir.name != manifest["id"]:
        result["errors"].append(
            f"directory name {specimen_dir.name!r} does not match manifest id {manifest['id']!r}"
        )
        result["checks"]["id_matches_dir"] = False
    else:
        result["checks"]["id_matches_dir"] = True

    artifacts = manifest.get("artifacts") or {}
    prompt_rel = manifest.get("prompt_path", "")
    paths: dict[str, Path | None] = {
        "prompt": resolve_under(specimen_dir, prompt_rel) if isinstance(prompt_rel, str) else None,
        "raw_output": resolve_under(specimen_dir, artifacts["raw_output_path"])
        if isinstance(artifacts.get("raw_output_path"), str)
        else None,
        "analysis": resolve_under(specimen_dir, artifacts["analysis_path"])
        if isinstance(artifacts.get("analysis_path"), str)
        else None,
        "notes": resolve_under(specimen_dir, artifacts["notes_path"])
        if isinstance(artifacts.get("notes_path"), str)
        else None,
        "screenshot": resolve_under(specimen_dir, artifacts["screenshot_path"])
        if isinstance(artifacts.get("screenshot_path"), str)
        else None,
    }

    rendered_rel = artifacts.get("rendered_output_path") or artifacts.get("raw_output_path")
    if isinstance(rendered_rel, str):
        paths["rendered_output"] = resolve_under(specimen_dir, rendered_rel)
    else:
        paths["rendered_output"] = None

    for label, path in paths.items():
        if path is None:
            result["checks"][f"{label}_path_safe"] = False
            result["errors"].append(f"unsafe or invalid {label} path")
            continue
        result["checks"][f"{label}_path_safe"] = True
        exists = path.exists()
        result["checks"][f"{label}_exists"] = exists
        if not exists:
            result["errors"].append(f"missing {label}: {path_display(path)}")
        elif label == "screenshot" and path.stat().st_size == 0:
            result["checks"]["screenshot_nonempty"] = False
            result["errors"].append("screenshot is empty")
        elif label == "screenshot":
            result["checks"]["screenshot_nonempty"] = True

    if result["errors"]:
        result["passed"] = False
        return result

    rendered_path = paths["rendered_output"]
    analysis_path = paths["analysis"]
    assert rendered_path is not None and analysis_path is not None

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
    result["kind"] = manifest.get("kind")
    result["provenance"] = manifest.get("generator", {}).get("provenance")
    result["scorer"] = manifest.get("score_meta", {}).get("scorer")
    result["analysis_path"] = path_display(analysis_path)
    result["output_path"] = path_display(rendered_path)
    return result


def summarize_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    if not results:
        return {
            "count": 0,
            "passed": 0,
            "failed": 0,
            "mean_overall_score": None,
            "mean_candidate_score": None,
            "mean_reference_score": None,
        }

    scores = [float(item["overall_score"]) for item in results]
    candidates = [float(item["overall_score"]) for item in results if item.get("kind") == "candidate"]
    references = [float(item["overall_score"]) for item in results if item.get("kind") == "reference"]
    passed = sum(1 for item in results if item.get("acceptance_passed"))

    def mean(values: list[float]) -> float | None:
        if not values:
            return None
        return round(sum(values) / len(values), 2)

    return {
        "count": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "mean_overall_score": mean(scores),
        "mean_candidate_score": mean(candidates),
        "mean_reference_score": mean(references),
    }


def compare_eval_results(base: dict[str, Any], head: dict[str, Any]) -> dict[str, Any]:
    base_by_id = {item["prompt_id"]: item for item in base.get("results", [])}
    head_by_id = {item["prompt_id"]: item for item in head.get("results", [])}
    all_ids = sorted(set(base_by_id) | set(head_by_id))

    deltas = []
    regressions = []
    improvements = []
    missing_in_head = []
    missing_in_base = []

    for prompt_id in all_ids:
        base_item = base_by_id.get(prompt_id)
        head_item = head_by_id.get(prompt_id)
        if base_item is None:
            missing_in_base.append(prompt_id)
            continue
        if head_item is None:
            missing_in_head.append(prompt_id)
            continue

        score_delta = float(head_item["overall_score"]) - float(base_item["overall_score"])
        pass_base = bool(base_item["acceptance_passed"])
        pass_head = bool(head_item["acceptance_passed"])
        entry = {
            "prompt_id": prompt_id,
            "specimen_id": head_item.get("specimen_id", base_item.get("specimen_id")),
            "base_score": base_item["overall_score"],
            "head_score": head_item["overall_score"],
            "score_delta": round(score_delta, 2),
            "base_passed": pass_base,
            "head_passed": pass_head,
            "pass_changed": pass_base != pass_head,
        }
        deltas.append(entry)
        if pass_base and not pass_head:
            regressions.append(prompt_id)
        if score_delta < 0 and (pass_base or pass_head):
            # score drop on scored prompts is also a soft regression signal
            if prompt_id not in regressions and score_delta <= -1:
                regressions.append(prompt_id)
        if score_delta > 0 or (not pass_base and pass_head):
            improvements.append(prompt_id)

    base_summary = base.get("summary") or summarize_results(base.get("results", []))
    head_summary = head.get("summary") or summarize_results(head.get("results", []))

    mean_base = base_summary.get("mean_overall_score")
    mean_head = head_summary.get("mean_overall_score")
    mean_delta = None
    if mean_base is not None and mean_head is not None:
        mean_delta = round(float(mean_head) - float(mean_base), 2)

    return {
        "base_created_at": base.get("created_at"),
        "head_created_at": head.get("created_at"),
        "mean_overall_delta": mean_delta,
        "regressions": regressions,
        "improvements": improvements,
        "missing_in_head": missing_in_head,
        "missing_in_base": missing_in_base,
        "deltas": deltas,
        "has_regressions": bool(regressions or missing_in_head),
    }
