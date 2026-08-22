from __future__ import annotations

import sys
import unittest
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from intent_model import IntentModel  # noqa: E402


class IntentModelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.model = IntentModel.load(ROOT / "shared" / "ai" / "intent_model.json")

    def assert_label(self, text: str, expected: str) -> None:
        prediction = self.model.predict(text)
        self.assertEqual(expected, prediction.label, (text, prediction))

    def test_operational_intents(self) -> None:
        cases = {
            "pulverize esse talhão": "SPRAY",
            "pode aplicar o defensivo aqui": "SPRAY",
            "sim, pode continuar": "CONFIRM",
            "confirmo a ordem": "CONFIRM",
            "não envie esse comando": "CANCEL",
            "cancele agora": "CANCEL",
            "qual é a cotação do dólar": "UNKNOWN",
            "conte uma história": "UNKNOWN",
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assert_label(text, expected)

    def test_probabilities_are_bounded(self) -> None:
        prediction = self.model.predict("pulverizar esta área")
        self.assertGreaterEqual(prediction.confidence, 0.0)
        self.assertLessEqual(prediction.confidence, 1.0)

    def test_low_confidence_becomes_unknown(self) -> None:
        prediction = self.model.predict_with_threshold("onde está meu celular", threshold=0.40)
        self.assertEqual("UNKNOWN", prediction.label)

    def test_adversarial_phrases_are_safe(self) -> None:
        cases = {
            "aplica no piquete três": "SPRAY",
            "isso mesmo": "CONFIRM",
            "manda ver": "CONFIRM",
            "deixa quieto": "CANCEL",
            "corta a operação": "CANCEL",
            "inspecione o talhão dois": "UNKNOWN",
            "pulverização é perigosa": "UNKNOWN",
            "o produto foi pulverizado ontem": "UNKNOWN",
            "não sei se devo pulverizar": "UNKNOWN",
            "sim mas espere": "UNKNOWN",
            "talhão três": "UNKNOWN",
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                prediction = self.model.predict_with_threshold(text)
                self.assertEqual(expected, prediction.label)

    def test_rules_report_their_origin(self) -> None:
        prediction = self.model.predict("não pulverize esse talhão")
        self.assertEqual("CANCEL", prediction.label)
        self.assertEqual("RULE", prediction.source)

    def test_versioned_evaluation_meets_safety_targets(self) -> None:
        report = json.loads((ROOT / "shared" / "ai" / "evaluation.json").read_text())
        self.assertGreaterEqual(report["examples"], 64)
        self.assertGreaterEqual(report["operational_accuracy"], 0.95)
        self.assertGreaterEqual(report["macro_f1"], 0.95)
        self.assertEqual([], report["unsafe_accepts"])
        self.assertLess((ROOT / "shared" / "ai" / "intent_model.json").stat().st_size, 1_000_000)


if __name__ == "__main__":
    unittest.main()
