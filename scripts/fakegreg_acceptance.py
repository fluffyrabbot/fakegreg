#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fakegreg_lib import ROOT, discover_specimens, load_json, run_acceptance


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run fakegreg specimen acceptance checks.")
    parser.add_argument(
        "--suite",
        type=Path,
        default=ROOT / "tests" / "acceptance-suite.json",
        help="Acceptance suite definition.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    suite = load_json(args.suite)
    specimens = discover_specimens()

    failures = []
    for entry in suite["specimens"]:
        specimen_id = entry["id"]
        if specimen_id not in specimens:
            failures.append(f"{specimen_id}: missing manifest")
            continue
        specimen_dir, manifest = specimens[specimen_id]
        result = run_acceptance(specimen_dir, manifest)
        prefix = "PASS" if result["passed"] else "FAIL"
        print(f"{prefix} {specimen_id} score={result.get('score', 'n/a')}")
        for error in result["errors"]:
            print(f"  - {error}")

        expected_pass = entry.get("expect_pass", True)
        if result["passed"] != expected_pass:
            failures.append(
                f"{specimen_id}: expected pass={expected_pass}, got pass={result['passed']}"
            )

    if failures:
        print("\nSuite failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("\nAll acceptance checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
