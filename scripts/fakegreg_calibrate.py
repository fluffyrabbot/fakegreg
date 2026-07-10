#!/usr/bin/env python3
"""Calibration checks: score bands + pairwise preference consistency."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from fakegreg_lib import (
    ROOT,
    discover_specimens,
    load_json,
    pairwise_consistency,
    validate_calibration_bands,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run fakegreg calibration checks.")
    parser.add_argument(
        "--bands",
        type=Path,
        default=ROOT / "data" / "calibration" / "bands.json",
    )
    parser.add_argument(
        "--pairwise",
        type=Path,
        default=ROOT / "data" / "pairwise" / "core.json",
    )
    parser.add_argument(
        "--skip-pairwise",
        action="store_true",
    )
    parser.add_argument(
        "--skip-bands",
        action="store_true",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    specimens = discover_specimens()
    failures: list[str] = []

    if not args.skip_bands:
        bands = load_json(args.bands)
        band_result = validate_calibration_bands(specimens, bands)
        print(f"Bands: {band_result['checked']} checked, {len(band_result['failures'])} failures")
        for item in band_result["results"]:
            status = "PASS" if item["passed"] else "FAIL"
            print(
                f"  {status} {item['id']}: overall={item['overall']} "
                f"band=[{item['min']},{item['max']}]"
            )
            for err in item["errors"]:
                print(f"    - {err}")
        failures.extend(band_result["failures"])

    if not args.skip_pairwise:
        pairwise = load_json(args.pairwise)
        pair_result = pairwise_consistency(specimens, pairwise)
        print(
            f"\nPairwise: {pair_result['checked']} checked, "
            f"{len(pair_result['failures'])} failures"
        )
        for item in pair_result["results"]:
            status = "PASS" if item["passed"] else "FAIL"
            print(
                f"  {status} {item['id']}: prefer {item['prefer']} over {item['over']} "
                f"(scores {item.get('prefer_score')} vs {item.get('over_score')})"
            )
            for err in item["errors"]:
                print(f"    - {err}")
        failures.extend(pair_result["failures"])

    if failures:
        print("\nCalibration failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("\nAll calibration checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
