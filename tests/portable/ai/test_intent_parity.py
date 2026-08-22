from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from export_intent_parity import build_fixture, render_fixture  # noqa: E402


class IntentParityFixtureTest(unittest.TestCase):
    def test_fixture_matches_canonical_model_and_semantic_labels(self):
        fixture_path = ROOT / "shared" / "ai" / "parity_cases.json"
        current = fixture_path.read_text(encoding="utf-8")
        self.assertEqual(render_fixture(build_fixture()), current)

    def test_fixture_has_unique_case_ids(self):
        payload = json.loads((ROOT / "shared" / "ai" / "parity_cases.json").read_text(encoding="utf-8"))
        case_ids = [item["id"] for item in payload["cases"]]
        self.assertEqual(len(case_ids), len(set(case_ids)))


if __name__ == "__main__":
    unittest.main()
