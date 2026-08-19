from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from export_intent_parity import build_fixture, validate_fixture  # noqa: E402


class IntentParityFixtureTest(unittest.TestCase):
    def test_fixture_matches_canonical_model_and_semantic_labels(self):
        fixture_path = ROOT / "shared" / "ai" / "parity_cases.json"
        current = json.loads(fixture_path.read_text(encoding="utf-8"))
        validate_fixture(current, build_fixture())

    def test_fixture_rejects_confidence_outside_tolerance(self):
        expected = build_fixture()
        current = json.loads(json.dumps(expected))
        current["cases"][0]["expected_confidence"] += expected["confidence_tolerance"] * 2

        with self.assertRaisesRegex(RuntimeError, "diverge na confiança"):
            validate_fixture(current, expected)

    def test_fixture_has_unique_case_ids(self):
        payload = json.loads((ROOT / "shared" / "ai" / "parity_cases.json").read_text(encoding="utf-8"))
        case_ids = [item["id"] for item in payload["cases"]]
        self.assertEqual(len(case_ids), len(set(case_ids)))


if __name__ == "__main__":
    unittest.main()
