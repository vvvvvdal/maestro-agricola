from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from jev_intent_metrics import calculate_metrics  # noqa: E402


class JevIntentMetricsTest(unittest.TestCase):
    def test_calculates_operational_safety_and_calibration_metrics(self) -> None:
        metrics = calculate_metrics(report())
        local = metrics["backends"]["local"]
        jev = metrics["backends"]["jev"]

        self.assertEqual(4, local["examples"])
        self.assertEqual(6, len(local["confusion_matrix"]))
        self.assertEqual(1.0, local["probability_coverage"])
        self.assertIsNotNone(local["calibration"]["brier_multiclass"])
        self.assertEqual(10, len(local["calibration"]["reliability_bins"]))
        self.assertEqual(2.0, local["latency_ms"]["p50"])
        self.assertEqual(4.0, local["latency_ms"]["p95"])

        self.assertEqual("case-002", jev["unsafe_accepts"][0]["id"])
        self.assertEqual([{"id": "case-004", "code": "TIMEOUT"}], jev["failures"])
        self.assertEqual(0.75, jev["probability_coverage"])
        self.assertEqual(0.004, jev["cost_usd"]["total"])
        self.assertEqual(["jev-1.13.0"], jev["models"])

    def test_excludes_error_case_with_inconsistent_answer_from_calibration(self) -> None:
        payload = report()
        payload["results"][3]["jev"]["answer"] = {
            "choice": "DOCK",
            "probabilities": probabilities("DOCK"),
            "confidence": 1.0,
        }

        metrics = calculate_metrics(payload)

        self.assertEqual(0.75, metrics["backends"]["jev"]["probability_coverage"])


def report() -> dict:
    cases = [
        pair("case-001", "SPRAY", "SPRAY", "SPRAY", 1.0, 1.0, 0.001),
        pair("case-002", "UNKNOWN", "UNKNOWN", "SPRAY", 2.0, 2.0, 0.001),
        pair("case-003", "CANCEL", "DOCK", "CANCEL", 3.0, 3.0, 0.002),
        failed_pair("case-004", "DOCK", "DOCK"),
    ]
    return {
        "schema_version": "1.1",
        "dataset": {"sha256": "dataset", "cases": len(cases)},
        "local_model_sha256": "local",
        "jev_fixture_sha256": "fixture",
        "results": cases,
    }


def pair(case_id: str, gold: str, local_label: str, jev_label: str, local_latency: float, jev_latency: float, cost: float) -> dict:
    return {
        "id": case_id,
        "gold_label": gold,
        "category": "test",
        "local": local(local_label, local_latency),
        "jev": jev(jev_label, jev_latency, cost),
    }


def failed_pair(case_id: str, gold: str, local_label: str) -> dict:
    return {
        "id": case_id,
        "gold_label": gold,
        "category": "test",
        "local": local(local_label, 4.0),
        "jev": {
            "requested_model": "jev-1.13.0",
            "response_model": None,
            "answer": None,
            "latency_ms": None,
            "cost_usd": None,
            "error": {"code": "TIMEOUT"},
            "prediction": prediction("UNKNOWN"),
        },
    }


def local(label: str, latency_ms: float) -> dict:
    return {"prediction": prediction(label), "probabilities": probabilities(label), "latency_ms": latency_ms}


def jev(label: str, latency_ms: float, cost_usd: float) -> dict:
    return {
        "requested_model": "jev-1.13.0",
        "response_model": "jev-1.13.0",
        "answer": {"choice": label, "probabilities": probabilities(label), "confidence": 1.0},
        "latency_ms": latency_ms,
        "cost_usd": cost_usd,
        "error": None,
        "prediction": prediction(label),
    }


def prediction(label: str) -> dict:
    return {"label": label, "confidence": 1.0, "source": "TEST"}


def probabilities(label: str) -> dict:
    values = {name: 0.0 for name in ("CANCEL", "CONFIRM", "DOCK", "SPRAY", "UNDOCK", "UNKNOWN")}
    values[label] = 1.0
    return values


if __name__ == "__main__":
    unittest.main()
