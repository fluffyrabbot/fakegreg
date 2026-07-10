#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

from fakegreg_lib import ROOT, discover_specimens, load_json, run_acceptance


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run fakegreg evals or emit baseline reports.")
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
        default=os.environ.get("FAKEGREG_MODEL", os.environ.get("CROF_MODEL", "greg-2-super")),
    )
    run.add_argument(
        "--base-url",
        default=os.environ.get("FAKEGREG_BASE_URL", os.environ.get("CROF_BASE_URL", "https://crof.ai/v1")),
    )
    return parser.parse_args()


def repo_relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


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


def post_chat_completion(base_url: str, model: str, system_prompt: str, user_prompt: str) -> str:
    api_key = os.environ.get("FAKEGREG_API_KEY") or os.environ.get("CROF_API_KEY")
    if not api_key:
        raise RuntimeError("Set FAKEGREG_API_KEY or CROF_API_KEY before using the run command.")

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"API request failed: {error.code} {detail}") from error

    return body["choices"][0]["message"]["content"]


def parse_overall_score(analysis_text: str) -> int | None:
    match = re.search(r"\*\*Overall Greg Score: (\d+)/100\*\*", analysis_text)
    if not match:
        return None
    return int(match.group(1))


def command_report(prompt_set_path: Path, out_path: Path) -> int:
    prompt_set = load_json(prompt_set_path)
    specimens = discover_specimens()
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
                "overall_score": manifest["scores"]["overall"],
                "acceptance_passed": acceptance["passed"],
                "analysis_path": acceptance.get("analysis_path"),
                "output_path": acceptance.get("output_path"),
            }
        )

    payload = {
        "prompt_set": prompt_set["id"],
        "created_at": datetime.now(UTC).isoformat(),
        "mode": "report",
        "results": results,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {repo_relative(out_path)}")
    for result in results:
        status = "PASS" if result["acceptance_passed"] else "FAIL"
        print(f"{status} {result['prompt_id']} score={result['overall_score']}")
    return 0


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
            content = post_chat_completion(base_url, model, system_prompt, entry["prompt"])
            output_path.write_text(content, encoding="utf-8")
            analysis_content = post_chat_completion(
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
                "overall_score": parsed_score,
                "acceptance_passed": False if entry["skill"] is None else (
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

    result_path = run_dir / "result.json"
    result_path.write_text(
        json.dumps(
            {
                "prompt_set": prompt_set["id"],
                "created_at": datetime.now(UTC).isoformat(),
                "mode": "run",
                "results": manifest_entries,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {repo_relative(result_path)}")
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "report":
        return command_report(args.prompt_set, args.out)
    if args.command == "run":
        return command_run(args.prompt_set, args.out_dir, args.model, args.base_url)
    raise AssertionError("unreachable")


if __name__ == "__main__":
    sys.exit(main())
