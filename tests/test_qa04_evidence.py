from __future__ import annotations

import copy
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from check_qa04_evidence import load_matrix, validate_matrix  # noqa: E402


class Qa04EvidenceTest(unittest.TestCase):
    def test_current_matrix_is_valid(self) -> None:
        validate_matrix(load_matrix())

    def test_rejects_overall_pass_with_incomplete_checkpoint(self) -> None:
        matrix = copy.deepcopy(load_matrix())
        matrix["overall_status"] = "PASS"

        with self.assertRaisesRegex(ValueError, "overall_status"):
            validate_matrix(matrix)

    def test_rejects_missing_evidence_file(self) -> None:
        matrix = copy.deepcopy(load_matrix())
        matrix["checkpoints"][0]["evidence"][0]["path"] = "shared/evidence/missing.json"

        with self.assertRaisesRegex(ValueError, "arquivo não encontrado"):
            validate_matrix(matrix)

    def test_rejects_pass_with_pending_work(self) -> None:
        matrix = copy.deepcopy(load_matrix())
        checkpoint = matrix["checkpoints"][0]
        checkpoint["status"] = "PASS"

        with self.assertRaisesRegex(ValueError, "PASS não pode manter pendências"):
            validate_matrix(matrix)


if __name__ == "__main__":
    unittest.main()
