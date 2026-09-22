from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from jev_presentation_evidence import load_metrics, write_artifacts  # noqa: E402


METRICS = ROOT / "docs/study-groups/jev-rl-2026-10-01/results/jev-final-recovery-metrics.json"


class JevPresentationEvidenceTest(unittest.TestCase):
    def test_renders_sanitized_report_matrices_and_reliability_svg(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = write_artifacts(METRICS, Path(directory))
            markdown = paths["markdown"].read_text(encoding="utf-8")
            payload = json.loads(paths["json"].read_text(encoding="utf-8"))
            svg = paths["svg"].read_text(encoding="utf-8")

        self.assertEqual(60, payload["backends"]["jev"]["examples"])
        self.assertEqual("recovery-045", payload["backends"]["jev"]["unsafe_accepts"][0]["id"])
        self.assertIn("| Ouro \\ Predicao |", markdown)
        self.assertIn("nao prova calibracao generalizavel", markdown)
        self.assertIn("CANCEL -> CONFIRM", markdown)
        self.assertIn("n=60, corpus sintetico pareado", svg)
        self.assertIn("Local", svg)
        self.assertIn("Jev remoto", svg)
        self.assertIn("n=", svg)
        self.assertNotIn("nao execute mais", markdown + svg + json.dumps(payload))
        self.assertNotIn("Authorization", markdown + svg + json.dumps(payload))
        self.assertNotIn("Bearer", markdown + svg + json.dumps(payload))
        self.assertNotIn("TYPESAFE_API_KEY", markdown + svg + json.dumps(payload))

    def test_rejects_metrics_with_invalid_schema_or_labels(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "metrics.json"
            path.write_text(json.dumps({"schema_version": "0.0", "backends": {}}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "schema"):
                load_metrics(path)

            payload = json.loads(METRICS.read_text(encoding="utf-8"))
            payload["backends"]["jev"]["confusion_matrix"].pop("CANCEL")
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "matrix rows"):
                load_metrics(path)


if __name__ == "__main__":
    unittest.main()
