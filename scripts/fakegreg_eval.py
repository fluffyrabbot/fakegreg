#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

from fakegreg_api import post_chat_completion, resolve_base_url, resolve_model
from fakegreg_lib import (
    ROOT,
    compare_eval_results,
    discover_specimens,
    load_json,
    run_acceptance,
    skill_prompt_hashes,
    summarize_results,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run fakegreg evals, emit reports, or compare runs.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    report = subparsers.add_parser("report", help="Summarize the current corpus into an eval result file.")
    report.add_argument(
        "--prompt-set",
        type=Path,
        default=ROOT / "data" / "prompt_sets" / "core.json",
    )
    report.add_argument(
        "--out",
        type=Path,
        default=ROOT / "data" / "evals" / "baseline.json",
        help="Latest pointer path (also archived under data/evals/runs/<id>/).",
    )
    report.add_argument(
        "--runs-dir",
        type=Path,
        default=ROOT / "data" / "evals" / "runs",
        help="Directory for timestamped eval history.",
    )
    report.add_argument(
        "--no-history",
        action="store_true",
        help="Skip writing a timestamped copy under data/evals/runs/.",
    )

    run = subparsers.add_parser("run", help="Run a prompt set through the skill prompts with an OpenAI-compatible API.")
    run.add_argument(
        "--prompt-set",
        type=Path,
        default=ROOT / "data" / "prompt_sets" / "core.json",
    )
    run.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "data" / "evals" / "runs",
    )
    run.add_argument(
        "--model",
        default=resolve_model(),
    )
    run.add_argument(
        "--base-url",
        default=resolve_base_url(),
    )

    compare = subparsers.add_parser("compare", help="Compare two eval result JSON files.")
    compare.add_argument(
        "--base",
        type=Path,
        required=True,
        help="Baseline eval result JSON.",
    )
    compare.add_argument(
        "--head",
        type=Path,
        required=True,
        help="Candidate eval result JSON.",
    )
    compare.add_argument(
        "--fail-on-regression",
        action="store_true",
        help="Exit non-zero when acceptance regressions or score drops are found.",
    )
    compare.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Optional path to write the comparison JSON.",
    )
    return parser.parse_args()


def repo_relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def build_skill_prompt(skill_name: str) -> str:
    skill_path = ROOT / ".grok" / "skills" / skill_name / "SKILL.md"
    if not skill_path.exists():
        raise FileNotFoundError(f"Skill not found: {repo_relative(skill_path)}")

    reference_paths = [
        ROOT / "references" / "SENSIBILITIES.md",
        ROOT / "references" / "STYLE_PRIMITIVES.md",
        ROOT / "references" / "PAGE_ARCHETYPES.md",
        ROOT / "references" / "ANTI_EXAMPLES.md",
        ROOT / "references" / "meridian-greg.html",
    ]
    references = []
    for path in reference_paths:
        references.append(f"\n--- {path.name} ---\n{path.read_text(encoding='utf-8')}")

    return (
        "You are executing a fakegreg skill outside the Grok runtime. "
        "Follow the skill instructions as closely as possible.\n\n"
        f"--- SKILL.md ({skill_name}) ---\n{skill_path.read_text(encoding='utf-8')}\n"
        + "".join(references)
    )


def chat(base_url: str, model: str, system_prompt: str, user_prompt: str) -> str:
    return post_chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        model=model,
        base_url=base_url,
    )


def parse_overall_score(analysis_text: str) -> int | None:
    match = re.search(r"\*\*Overall Greg Score: (\d+)/100\*\*", analysis_text)
    if not match:
        return None
    return int(match.group(1))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def build_report_payload(prompt_set: dict[str, Any], specimens: dict[str, tuple[Path, dict[str, Any]]]) -> dict[str, Any]:
    results = []
    for entry in prompt_set["entries"]:
        specimen_id = entry["specimen_id"]
        specimen_dir, manifest = specimens[specimen_id]
        acceptance = run_acceptance(specimen_dir, manifest)
        results.append(
            {
                "prompt_id": entry["id"],
                "specimen_id": specimen_id,
                "surface": entry["surface"],
                "kind": manifest.get("kind"),
                "provenance": manifest.get("generator", {}).get("provenance"),
                "scorer": manifest.get("score_meta", {}).get("scorer"),
                "overall_score": manifest["scores"]["overall"],
                "acceptance_passed": acceptance["passed"],
                "analysis_path": acceptance.get("analysis_path"),
                "output_path": acceptance.get("output_path"),
            }
        )

    created_at = datetime.now(UTC).isoformat()
    run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return {
        "prompt_set": prompt_set["id"],
        "created_at": created_at,
        "mode": "report",
        "run_id": run_id,
        "skill_hashes": skill_prompt_hashes(),
        "summary": summarize_results(results),
        "results": results,
    }


def command_report(prompt_set_path: Path, out_path: Path, runs_dir: Path, no_history: bool) -> int:
    prompt_set = load_json(prompt_set_path)
    specimens = discover_specimens()
    payload = build_report_payload(prompt_set, specimens)

    write_json(out_path, payload)
    print(f"Wrote {repo_relative(out_path)}")

    if not no_history:
        history_path = runs_dir / payload["run_id"] / "report.json"
        write_json(history_path, payload)
        print(f"Wrote {repo_relative(history_path)}")
        latest_path = runs_dir / "latest.json"
        write_json(
            latest_path,
            {
                "run_id": payload["run_id"],
                "created_at": payload["created_at"],
                "mode": payload["mode"],
                "path": repo_relative(history_path),
            },
        )
        print(f"Wrote {repo_relative(latest_path)}")

    for result in payload["results"]:
        status = "PASS" if result["acceptance_passed"] else "FAIL"
        print(
            f"{status} {result['prompt_id']} score={result['overall_score']} "
            f"provenance={result.get('provenance')} scorer={result.get('scorer')}"
        )
    summary = payload["summary"]
    print(
        f"summary count={summary['count']} passed={summary['passed']} "
        f"mean={summary['mean_overall_score']} candidate_mean={summary['mean_candidate_score']}"
    )
    return 0 if summary["failed"] == 0 else 1


def command_run(prompt_set_path: Path, out_dir: Path, model: str, base_url: str) -> int:
    prompt_set = load_json(prompt_set_path)
    specimens = discover_specimens()
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    run_dir = out_dir / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)
    analyzer_prompt = build_skill_prompt("greg-ui-analyze")

    manifest_entries: list[dict[str, Any]] = []
    for entry in prompt_set["entries"]:
        prompt_id = entry["id"]
        prompt_dir = run_dir / prompt_id
        prompt_dir.mkdir(parents=True, exist_ok=True)
        _, specimen_manifest = specimens[entry["specimen_id"]]
        acceptance = specimen_manifest["acceptance"]

        output_name = "output.tsx" if entry["surface"] == "framework_component" else "output.html"
        output_path = prompt_dir / output_name
        analysis_path = prompt_dir / "analysis.md"
        if entry["skill"] is None:
            output_path.write_text(
                "Control specimen; no skill execution performed.\n",
                encoding="utf-8",
            )
            content = "Control specimen; no skill execution performed."
            analysis_content = "Control specimen; no analyzer run performed."
            parsed_score = 0
        else:
            system_prompt = build_skill_prompt(entry["skill"])
            content = chat(base_url, model, system_prompt, entry["prompt"])
            output_path.write_text(content, encoding="utf-8")
            analysis_content = chat(
                base_url,
                model,
                analyzer_prompt,
                f"Original prompt:\n{entry['prompt']}\n\nCandidate output:\n{content}",
            )
            analysis_path.write_text(analysis_content, encoding="utf-8")
            parsed_score = parse_overall_score(analysis_content) or 0

        manifest_entries.append(
            {
                "prompt_id": prompt_id,
                "specimen_id": entry["specimen_id"],
                "surface": entry["surface"],
                "kind": specimen_manifest.get("kind"),
                "provenance": "real_api" if entry["skill"] is not None else specimen_manifest.get(
                    "generator", {}
                ).get("provenance"),
                "scorer": "skill" if entry["skill"] is not None else specimen_manifest.get("score_meta", {}).get(
                    "scorer"
                ),
                "overall_score": parsed_score,
                "acceptance_passed": False
                if entry["skill"] is None
                else (
                    parsed_score >= acceptance.get("minimum_score", 0)
                    and (
                        acceptance.get("maximum_score") is None
                        or parsed_score <= acceptance["maximum_score"]
                    )
                ),
                "analysis_path": None if entry["skill"] is None else repo_relative(analysis_path),
                "output_path": repo_relative(output_path),
            }
        )
        print(f"Wrote {repo_relative(output_path)} ({len(content)} chars)")
        if entry["skill"] is not None:
            print(f"Wrote {repo_relative(analysis_path)} score={parsed_score}")

    payload = {
        "prompt_set": prompt_set["id"],
        "created_at": datetime.now(UTC).isoformat(),
        "mode": "run",
        "run_id": timestamp,
        "skill_hashes": skill_prompt_hashes(),
        "summary": summarize_results(manifest_entries),
        "results": manifest_entries,
    }
    result_path = run_dir / "result.json"
    write_json(result_path, payload)
    write_json(
        out_dir / "latest.json",
        {
            "run_id": timestamp,
            "created_at": payload["created_at"],
            "mode": "run",
            "path": repo_relative(result_path),
        },
    )
    print(f"Wrote {repo_relative(result_path)}")
    return 0


def command_compare(base_path: Path, head_path: Path, fail_on_regression: bool, out_path: Path | None) -> int:
    base = load_json(base_path)
    head = load_json(head_path)
    comparison = compare_eval_results(base, head)
    comparison["base_path"] = repo_relative(base_path)
    comparison["head_path"] = repo_relative(head_path)

    if out_path is not None:
        write_json(out_path, comparison)
        print(f"Wrote {repo_relative(out_path)}")

    print(f"base={comparison['base_path']} ({comparison.get('base_created_at')})")
    print(f"head={comparison['head_path']} ({comparison.get('head_created_at')})")
    print(f"mean_overall_delta={comparison['mean_overall_delta']}")

    if comparison["deltas"]:
        print("\nPer-prompt deltas:")
        for item in comparison["deltas"]:
            pass_note = ""
            if item["pass_changed"]:
                pass_note = f" pass {item['base_passed']}->{item['head_passed']}"
            print(
                f"  {item['prompt_id']}: {item['base_score']} -> {item['head_score']} "
                f"({item['score_delta']:+}){pass_note}"
            )

    if comparison["regressions"]:
        print("\nRegressions:")
        for prompt_id in comparison["regressions"]:
            print(f"  - {prompt_id}")
    if comparison["missing_in_head"]:
        print("\nMissing in head:")
        for prompt_id in comparison["missing_in_head"]:
            print(f"  - {prompt_id}")
    if comparison["improvements"]:
        print("\nImprovements:")
        for prompt_id in comparison["improvements"]:
            print(f"  - {prompt_id}")

    if fail_on_regression and comparison["has_regressions"]:
        return 1
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "report":
        return command_report(args.prompt_set, args.out, args.runs_dir, args.no_history)
    if args.command == "run":
        return command_run(args.prompt_set, args.out_dir, args.model, args.base_url)
    if args.command == "compare":
        return command_compare(args.base, args.head, args.fail_on_regression, args.out)
    raise AssertionError("unreachable")


if __name__ == "__main__":
    sys.exit(main())
