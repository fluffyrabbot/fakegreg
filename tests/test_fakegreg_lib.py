#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from fakegreg_lib import (  # noqa: E402
    compare_eval_results,
    count_kickers,
    is_safe_relative_path,
    pairwise_consistency,
    resolve_under,
    run_acceptance,
    summarize_results,
    validate_calibration_bands,
    validate_manifest_schema,
)


def valid_manifest(**overrides):
    base = {
        "id": "example",
        "title": "Example",
        "kind": "candidate",
        "surface": "landing_page",
        "prompt_path": "prompt.md",
        "generator": {
            "source": "test",
            "model": "test",
            "skill": "greg-direct-repro",
            "generated_at": "2026-06-22",
            "provenance": "synthetic_seed",
            "notes": "unit test fixture",
        },
        "artifacts": {
            "raw_output_path": "output.html",
            "rendered_output_path": "output.html",
            "screenshot_path": "screenshot.png",
            "analysis_path": "analysis.md",
            "notes_path": "notes.md",
        },
        "scores": {
            "overall": 85,
            "design_quality": 85,
            "visual_polish": 85,
            "narrative_copy": 85,
            "implementation": 85,
            "greg_fidelity": 85,
        },
        "score_meta": {
            "scorer": "human",
            "scored_at": "2026-06-22",
            "method": "unit test",
        },
        "acceptance": {
            "minimum_score": 80,
            "maximum_score": None,
            "required_sections": ["hero", "cta"],
            "required_visuals": [],
            "minimum_kickers": 0,
            "analysis_shape": "greg_ui_analysis_v1",
        },
        "tags": ["test"],
    }
    base.update(overrides)
    return base


class PathSafetyTests(unittest.TestCase):
    def test_safe_relative_paths(self):
        self.assertTrue(is_safe_relative_path("output.html"))
        self.assertTrue(is_safe_relative_path("nested/file.md"))
        self.assertFalse(is_safe_relative_path("../escape.html"))
        self.assertFalse(is_safe_relative_path("/abs/path"))
        self.assertFalse(is_safe_relative_path(""))

    def test_resolve_under_blocks_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            self.assertIsNotNone(resolve_under(base, "ok.html"))
            self.assertIsNone(resolve_under(base, "../outside.html"))


class SchemaValidationTests(unittest.TestCase):
    def test_valid_manifest_has_no_errors(self):
        self.assertEqual(validate_manifest_schema(valid_manifest()), [])

    def test_rejects_free_text_provenance(self):
        manifest = valid_manifest()
        manifest["generator"]["provenance"] = "Cleaned and reconstructed from Meridian"
        errors = validate_manifest_schema(manifest)
        self.assertTrue(any("generator.provenance" in e for e in errors))

    def test_requires_score_meta(self):
        manifest = valid_manifest()
        del manifest["score_meta"]
        errors = validate_manifest_schema(manifest)
        self.assertTrue(any("score_meta" in e for e in errors))

    def test_rejects_unknown_section(self):
        manifest = valid_manifest()
        manifest["acceptance"]["required_sections"] = ["hero", "not_a_section"]
        errors = validate_manifest_schema(manifest)
        self.assertTrue(any("required_sections" in e for e in errors))


class HeuristicTests(unittest.TestCase):
    def test_count_kickers(self):
        text = "// the model\n// the mesh\n//not\n// x"
        self.assertEqual(count_kickers(text), 3)


class AcceptanceFixtureTests(unittest.TestCase):
    def test_run_acceptance_on_minimal_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            specimen_dir = Path(tmp) / "example"
            specimen_dir.mkdir()
            (specimen_dir / "prompt.md").write_text("prompt\n", encoding="utf-8")
            (specimen_dir / "output.html").write_text(
                "<header><h1>Title</h1></header>"
                "<a>Get started</a>"
                "<pre><code>curl https://api.example</code></pre>",
                encoding="utf-8",
            )
            (specimen_dir / "analysis.md").write_text(
                "**Overall Greg Score: 85/100**\n\n"
                "## Breakdown\n\n"
                "## Strengths\n\n"
                "## Greg-Style Improvement Opportunities\n\n"
                "## Suggested Next Prompt\n\n"
                "Verdict: solid candidate\n",
                encoding="utf-8",
            )
            (specimen_dir / "notes.md").write_text("notes\n", encoding="utf-8")
            (specimen_dir / "screenshot.png").write_bytes(b"\x89PNG\r\n\x1a\nfake")

            result = run_acceptance(specimen_dir, valid_manifest())
            self.assertTrue(result["passed"], result["errors"])
            self.assertEqual(result["score"], 85)

    def test_run_acceptance_fails_path_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            specimen_dir = Path(tmp) / "example"
            specimen_dir.mkdir()
            manifest = valid_manifest()
            manifest["artifacts"]["raw_output_path"] = "../escape.html"
            result = run_acceptance(specimen_dir, manifest)
            self.assertFalse(result["passed"])
            self.assertTrue(any("unsafe" in e or "path" in e for e in result["errors"]))


class CompareTests(unittest.TestCase):
    def test_compare_detects_score_regression(self):
        base = {
            "created_at": "2026-01-01T00:00:00+00:00",
            "results": [
                {
                    "prompt_id": "a",
                    "specimen_id": "a",
                    "surface": "landing_page",
                    "overall_score": 90,
                    "acceptance_passed": True,
                }
            ],
        }
        head = {
            "created_at": "2026-01-02T00:00:00+00:00",
            "results": [
                {
                    "prompt_id": "a",
                    "specimen_id": "a",
                    "surface": "landing_page",
                    "overall_score": 80,
                    "acceptance_passed": True,
                }
            ],
        }
        comparison = compare_eval_results(base, head)
        self.assertEqual(comparison["mean_overall_delta"], -10.0)
        self.assertIn("a", comparison["regressions"])
        self.assertTrue(comparison["has_regressions"])

    def test_summarize_splits_reference_and_candidate(self):
        results = [
            {"overall_score": 96, "acceptance_passed": True, "kind": "reference"},
            {"overall_score": 80, "acceptance_passed": True, "kind": "candidate"},
            {"overall_score": 40, "acceptance_passed": True, "kind": "anti_example"},
        ]
        summary = summarize_results(results)
        self.assertEqual(summary["count"], 3)
        self.assertEqual(summary["mean_reference_score"], 96.0)
        self.assertEqual(summary["mean_candidate_score"], 80.0)
        self.assertEqual(summary["mean_overall_score"], 72.0)


class CorpusSmokeTests(unittest.TestCase):
    def test_all_committed_manifests_validate(self):
        specimens_dir = ROOT / "data" / "specimens"
        for manifest_path in sorted(specimens_dir.glob("*/manifest.json")):
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            errors = validate_manifest_schema(manifest)
            self.assertEqual(errors, [], msg=f"{manifest_path}: {errors}")


class CalibrationTests(unittest.TestCase):
    def test_bands_and_pairwise_on_corpus(self):
        from fakegreg_lib import discover_specimens, load_json

        specimens = discover_specimens()
        bands = load_json(ROOT / "data" / "calibration" / "bands.json")
        pairwise = load_json(ROOT / "data" / "pairwise" / "core.json")
        band_result = validate_calibration_bands(specimens, bands)
        pair_result = pairwise_consistency(specimens, pairwise)
        self.assertTrue(band_result["passed"], band_result["failures"])
        self.assertTrue(pair_result["passed"], pair_result["failures"])

    def test_pairwise_detects_inversion(self):
        specimens = {
            "a": (Path("a"), {"scores": {"overall": 50}}),
            "b": (Path("b"), {"scores": {"overall": 90}}),
        }
        doc = {"pairs": [{"id": "bad", "prefer": "a", "over": "b", "min_margin": 5}]}
        result = pairwise_consistency(specimens, doc)
        self.assertFalse(result["passed"])


if __name__ == "__main__":
    unittest.main()
