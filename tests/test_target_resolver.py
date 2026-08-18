from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from target_resolver import resolve_target  # noqa: E402


class TargetResolverTest(unittest.TestCase):
    def test_shared_cases(self):
        payload = json.loads(
            (ROOT / "shared" / "target" / "target_resolution_cases.json").read_text(encoding="utf-8")
        )
        allowed = set(payload["allowed_target_ids"])
        for item in payload["cases"]:
            with self.subTest(case=item["id"]):
                result = resolve_target(item["visual_target_id"], item["transcript"], allowed)
                self.assertEqual(item["expected_status"], result.status)
                self.assertEqual(item["expected_target_id"], result.target_id)
                self.assertEqual(item["expected_source"], result.source)


if __name__ == "__main__":
    unittest.main()
