from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from jev_intent_harness import load_jev_fixture, run_harness  # noqa: E402


class JevIntentHarnessTest(unittest.TestCase):
    def test_records_local_and_jev_once_per_sanitized_case(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dataset = root / "cases.tsv"
            fixture = root / "jev.json"
            dataset.write_text(
                "id\ttext\tgold_label\tcategory\n"
                "case-001\tpulverize o talhao <ALVO>\tSPRAY\tdirect_command\n"
                "case-002\ttalvez pulverize\tUNKNOWN\thesitation\n"
                "case-003\txyzzy quux\tUNKNOWN\tasr_noise\n",
                encoding="utf-8",
            )
            fixture.write_text(json.dumps({
                "schema_version": "1.0",
                "model": "jev-1.13.0",
                "results": {
                    "case-001": choice("SPRAY", {"SPRAY": 0.91, "UNKNOWN": 0.09}),
                    "case-002": choice(
                        "SPRAY",
                        {
                            "SPRAY": 0.23,
                            "DOCK": 0.20,
                            "UNDOCK": 0.15,
                            "CONFIRM": 0.15,
                            "CANCEL": 0.14,
                            "UNKNOWN": 0.13,
                        },
                    ),
                    "case-003": {
                        "error": {
                            "code": "TIMEOUT",
                            "detail": "operator said never record this text",
                        },
                        "raw_response": "secret response must not be recorded",
                    },
                },
            }), encoding="utf-8")

            report = run_harness(
                dataset,
                ROOT / "shared/ai/intent_model.json",
                fixture,
            )

        self.assertEqual("1.0", report["schema_version"])
        self.assertEqual(3, report["dataset"]["cases"])
        self.assertEqual(["case-001", "case-002", "case-003"], [
            result["id"] for result in report["results"]
        ])
        self.assertNotIn("text", report["results"][0])
        self.assertEqual("JEV", report["results"][0]["jev"]["prediction"]["source"])
        self.assertEqual("SPRAY", report["results"][0]["jev"]["prediction"]["label"])
        self.assertEqual("UNKNOWN", report["results"][1]["jev"]["prediction"]["label"])
        self.assertEqual(0.23, report["results"][1]["jev"]["prediction"]["confidence"])
        self.assertEqual("UNKNOWN", report["results"][2]["jev"]["prediction"]["label"])
        self.assertEqual(0.0, report["results"][2]["jev"]["prediction"]["confidence"])
        self.assertEqual({"code": "INVALID_RESPONSE"}, report["results"][2]["jev"]["error"])
        serialized = json.dumps(report)
        self.assertNotIn("operator said never record this text", serialized)
        self.assertNotIn("secret response must not be recorded", serialized)

    def test_rejects_fixture_with_missing_case_id(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory) / "jev.json"
            fixture.write_text(json.dumps({
                "schema_version": "1.0",
                "model": "jev-1.13.0",
                "results": {"case-001": {}},
            }), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "ids must match"):
                load_jev_fixture(fixture, {"case-001", "case-002"})


def choice(selected: str, probabilities: dict[str, float]) -> dict:
    values = {
        "SPRAY": 0.0,
        "DOCK": 0.0,
        "UNDOCK": 0.0,
        "CONFIRM": 0.0,
        "CANCEL": 0.0,
        "UNKNOWN": 0.0,
    }
    values.update(probabilities)
    return {
        "response_model": "jev-1.13.0",
        "answer": {
            "choice": selected,
            "probabilities": values,
            "confidence": values[selected],
        },
        "usage": {"input_tokens": 1, "output_tokens": 1},
        "latency_ms": 2.0,
        "cost_usd": 0.0,
    }


if __name__ == "__main__":
    unittest.main()
