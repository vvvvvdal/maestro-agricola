from __future__ import annotations

import copy
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from train_intent_model import (  # noqa: E402
    ARTIFACT_FLOAT_TOLERANCE,
    artifacts_equal,
)


class IntentModelArtifactComparisonTest(unittest.TestCase):
    def setUp(self) -> None:
        self.artifact = {
            "schema_version": "1.0",
            "labels": ["CANCEL", "CONFIRM", "SPRAY", "UNKNOWN"],
            "weights": {"CONFIRM": {"u:confirmar": 1.25}},
        }

    def test_accepts_platform_float_noise(self) -> None:
        current = copy.deepcopy(self.artifact)
        current["weights"]["CONFIRM"]["u:confirmar"] += ARTIFACT_FLOAT_TOLERANCE / 10

        self.assertTrue(artifacts_equal(current, self.artifact))

    def test_rejects_relevant_model_change(self) -> None:
        current = copy.deepcopy(self.artifact)
        current["weights"]["CONFIRM"]["u:confirmar"] += ARTIFACT_FLOAT_TOLERANCE * 10

        self.assertFalse(artifacts_equal(current, self.artifact))

    def test_rejects_structural_change(self) -> None:
        current = copy.deepcopy(self.artifact)
        current["labels"].remove("UNKNOWN")

        self.assertFalse(artifacts_equal(current, self.artifact))


if __name__ == "__main__":
    unittest.main()
