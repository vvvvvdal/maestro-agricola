from __future__ import annotations

import copy
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from check_qa04_evidence import (  # noqa: E402
    load_matrix,
    validate_candidate_apk,
    validate_matrix,
)


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

    def test_rejects_candidate_model_hash_mismatch(self) -> None:
        matrix = copy.deepcopy(load_matrix())
        matrix["build_traceability"]["current_candidate_model_sha256"] = "0" * 64

        with self.assertRaisesRegex(ValueError, "modelo canônico"):
            validate_matrix(matrix)

    def test_rejects_benchmarked_hash_mismatch(self) -> None:
        matrix = copy.deepcopy(load_matrix())
        matrix["build_traceability"]["device_benchmarked_apk_sha256"] = "0" * 64

        with self.assertRaisesRegex(ValueError, "avaliação física"):
            validate_matrix(matrix)

    def test_rejects_completed_benchmark_for_divergent_artifacts(self) -> None:
        matrix = copy.deepcopy(load_matrix())
        matrix["build_traceability"]["current_candidate_apk_sha256"] = "0" * 64
        matrix["build_traceability"]["final_build_benchmark_pending"] = False

        with self.assertRaisesRegex(ValueError, "artefatos divergentes"):
            validate_matrix(matrix)

    def test_rejects_candidate_apk_hash_mismatch(self) -> None:
        matrix = copy.deepcopy(load_matrix())
        with tempfile.TemporaryDirectory() as directory:
            apk = Path(directory) / "candidate.apk"
            apk.write_bytes(b"not-the-recorded-apk")

            with self.assertRaisesRegex(ValueError, "APK informado"):
                validate_candidate_apk(matrix, apk)


if __name__ == "__main__":
    unittest.main()
