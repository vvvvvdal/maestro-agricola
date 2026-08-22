from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from intent_model import Prediction  # noqa: E402
from train_intent_model import (  # noqa: E402
    ARTIFACT_FLOAT_TOLERANCE,
    artifacts_equal,
    evaluate,
    write_artifact_if_changed,
)


class FixedPredictionModel:
    def __init__(self, labels: tuple[str, ...], predicted_label: str) -> None:
        self.labels = labels
        self.predicted_label = predicted_label

    def predict(self, text: str) -> Prediction:
        del text
        scores = {
            label: float(label == self.predicted_label)
            for label in self.labels
        }
        return Prediction(self.predicted_label, 1.0, scores)

    def predict_with_threshold(
        self,
        text: str,
        threshold: float,
    ) -> Prediction:
        del threshold
        return self.predict(text)


class IntentModelArtifactComparisonTest(unittest.TestCase):
    def setUp(self) -> None:
        self.artifact = {
            "schema_version": "1.0",
            "labels": ["CANCEL", "CONFIRM", "SPRAY", "UNKNOWN"],
            "weights": {
                "CONFIRM": {
                    "u:confirmar": 1.25,
                }
            },
        }

    def test_accepts_platform_float_noise(self) -> None:
        current = copy.deepcopy(self.artifact)
        current["weights"]["CONFIRM"]["u:confirmar"] += (
            ARTIFACT_FLOAT_TOLERANCE / 10
        )

        self.assertTrue(artifacts_equal(current, self.artifact))

    def test_rejects_relevant_float_change(self) -> None:
        current = copy.deepcopy(self.artifact)
        current["weights"]["CONFIRM"]["u:confirmar"] += (
            ARTIFACT_FLOAT_TOLERANCE * 10
        )

        self.assertFalse(artifacts_equal(current, self.artifact))

    def test_rejects_structural_change(self) -> None:
        current = copy.deepcopy(self.artifact)
        current["labels"].remove("UNKNOWN")

        self.assertFalse(artifacts_equal(current, self.artifact))

    def test_preserves_equivalent_versioned_artifact_bytes(self) -> None:
        current = copy.deepcopy(self.artifact)
        current["weights"]["CONFIRM"]["u:confirmar"] += (
            ARTIFACT_FLOAT_TOLERANCE / 2
        )

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "artifact.json"
            original = json.dumps(current, separators=(",", ":")) + "\n"
            path.write_text(original, encoding="utf-8")

            changed = write_artifact_if_changed(path, self.artifact)

            self.assertFalse(changed)
            self.assertEqual(original, path.read_text(encoding="utf-8"))

    def test_rewrites_artifact_when_content_really_changes(self) -> None:
        current = copy.deepcopy(self.artifact)
        current["weights"]["CONFIRM"]["u:confirmar"] += (
            ARTIFACT_FLOAT_TOLERANCE * 2
        )

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "artifact.json"
            path.write_text(json.dumps(current), encoding="utf-8")

            changed = write_artifact_if_changed(path, self.artifact)

            self.assertTrue(changed)
            self.assertEqual(
                self.artifact,
                json.loads(path.read_text(encoding="utf-8")),
            )


class IntentModelEvaluationTest(unittest.TestCase):
    def test_macro_f1_ignores_labels_absent_from_corpus_and_predictions(self) -> None:
        model = FixedPredictionModel(
            labels=("DOCK", "SPRAY", "UNDOCK"),
            predicted_label="SPRAY",
        )

        report = evaluate(model, [("SPRAY", "pulverize o talhão")])

        self.assertEqual(1.0, report["macro_f1"])
        self.assertEqual({"SPRAY"}, set(report["per_label"]))

    def test_macro_f1_penalizes_unexpected_predicted_label(self) -> None:
        model = FixedPredictionModel(
            labels=("DOCK", "SPRAY", "UNDOCK"),
            predicted_label="DOCK",
        )

        report = evaluate(model, [("SPRAY", "pulverize o talhão")])

        self.assertEqual(0.0, report["macro_f1"])
        self.assertEqual({"DOCK", "SPRAY"}, set(report["per_label"]))
        self.assertEqual(1, report["confusion_matrix"]["SPRAY"]["DOCK"])


if __name__ == "__main__":
    unittest.main()
