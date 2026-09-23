from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from jev_presentation_slides import load_evidence, write_slide_assets  # noqa: E402


EVIDENCE = ROOT / "docs/study-groups/jev-rl-2026-10-01/results/jev-final-recovery-presentation.json"
RESULTS = EVIDENCE.parent


class JevPresentationSlidesTest(unittest.TestCase):
    def test_renders_deterministic_slide_assets_with_required_limits(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory)
            first = write_slide_assets(EVIDENCE, output_dir)
            rendered = {name: path.read_text(encoding="utf-8") for name, path in first.items()}
            second = write_slide_assets(EVIDENCE, output_dir)
            repeated = {name: path.read_text(encoding="utf-8") for name, path in second.items()}

        self.assertEqual(rendered, repeated)
        versioned = {
            name: (RESULTS / path.name).read_text(encoding="utf-8")
            for name, path in first.items()
        }
        self.assertEqual(rendered, versioned)
        self.assertEqual({"comparison", "confusion", "reliability"}, set(rendered))
        joined = "\n".join(rendered.values())
        self.assertIn('width="1600" height="900"', joined)
        self.assertIn("54/60", rendered["comparison"])
        self.assertIn("0,9010", rendered["comparison"])
        self.assertIn("2.100,575 ms", rendered["comparison"])
        self.assertIn("US$0.001472394", rendered["comparison"])
        self.assertIn("CANCEL -&gt; CONFIRM (0,75)", joined)
        self.assertIn("linhas: ouro | colunas: predicao", rendered["confusion"])
        self.assertIn("n=60, corpus sintetico pareado", joined)
        self.assertIn("Decisao: HOLD", joined)
        self.assertNotIn("Authorization", joined)
        self.assertNotIn("Bearer", joined)
        self.assertNotIn("TYPESAFE_API_KEY", joined)

    def test_rejects_invalid_evidence_schema(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.json"
            path.write_text(json.dumps({"schema_version": "0.0", "backends": {}}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "schema"):
                load_evidence(path)


if __name__ == "__main__":
    unittest.main()
