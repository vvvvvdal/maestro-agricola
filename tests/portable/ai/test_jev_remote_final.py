from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from jev_intent_harness import load_jev_fixture  # noqa: E402
from jev_remote_final import (  # noqa: E402
    FINAL_CASES,
    FINAL_COST_CAP_USD,
    FINAL_DATASET_SHA256,
    MAX_FINAL_ATTEMPTS,
    ensure_final_fixture_absent,
    load_final_cases,
    reserve_final_evaluation,
    run_final,
    sha256,
)
from jev_remote_smoke import LABELS, MODEL, HttpResponse  # noqa: E402


class JevRemoteFinalTest(unittest.TestCase):
    def test_final_corpus_is_frozen_and_fixture_is_harness_compatible(self) -> None:
        cases = load_final_cases()

        fixture = run_final(cases, "not-recorded", lambda _body, _key: ok_response("UNKNOWN"))

        self.assertEqual(FINAL_CASES, len(cases))
        self.assertEqual(FINAL_DATASET_SHA256, sha256(ROOT / "docs/study-groups/jev-rl-2026-10-01/corpus/final.tsv"))
        self.assertEqual(
            (MODEL, fixture["results"]),
            load_jev_fixture_from_result(fixture, {case.case_id for case in cases}),
        )
        serialized = json.dumps(fixture)
        self.assertNotIn(cases[0].text, serialized)
        self.assertNotIn("not-recorded", serialized)

    def test_rejects_changed_corpus_or_existing_final_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            changed_corpus = root / "final.tsv"
            changed_corpus.write_text("id\ttext\tgold_label\tcategory\n", encoding="utf-8")
            existing_fixture = root / "fixture.json"
            existing_fixture.write_text("{}", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "hash"):
                load_final_cases(changed_corpus)
            with self.assertRaisesRegex(FileExistsError, "second final"):
                ensure_final_fixture_absent(existing_fixture)

    def test_atomic_reservation_blocks_a_second_or_interrupted_round(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            reservation = Path(directory) / "reservation.json"

            reserve_final_evaluation(reservation)

            payload = json.loads(reservation.read_text(encoding="utf-8"))
            self.assertEqual(MODEL, payload["model"])
            self.assertEqual(FINAL_DATASET_SHA256, payload["dataset_sha256"])
            with self.assertRaisesRegex(FileExistsError, "second final"):
                reserve_final_evaluation(reservation)

    def test_allows_one_retry_per_case_and_never_exceeds_global_limit(self) -> None:
        calls = 0

        def overloaded(_body: bytes, _key: str) -> HttpResponse:
            nonlocal calls
            calls += 1
            return HttpResponse(529, {}, b"")

        fixture = run_final(load_final_cases(), "key", overloaded, lambda _delay: None)

        self.assertEqual(MAX_FINAL_ATTEMPTS, calls)
        self.assertEqual(FINAL_CASES, len(fixture["results"]))
        self.assertTrue(all(result["error"]["code"] == "OVERLOADED" for result in fixture["results"].values()))

    def test_rejects_timeout_without_retry(self) -> None:
        calls = 0

        def timed_out(_body: bytes, _key: str) -> HttpResponse:
            nonlocal calls
            calls += 1
            raise TimeoutError

        fixture = run_final(load_final_cases(), "key", timed_out)

        self.assertEqual(FINAL_CASES, calls)
        self.assertTrue(all(result["error"]["code"] == "TIMEOUT" for result in fixture["results"].values()))

    def test_documented_upper_bound_stays_below_final_cap(self) -> None:
        from jev_remote_smoke import worst_case_cost_usd

        self.assertLess(worst_case_cost_usd(MAX_FINAL_ATTEMPTS), FINAL_COST_CAP_USD)


def load_jev_fixture_from_result(fixture: dict, case_ids: set[str]) -> tuple[str, dict]:
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", encoding="utf-8") as output:
        json.dump(fixture, output)
        output.flush()
        return load_jev_fixture(Path(output.name), case_ids)


def ok_response(label: str) -> HttpResponse:
    probabilities = {name: 0.0 for name in LABELS}
    probabilities[label] = 1.0
    return HttpResponse(200, {}, json.dumps({
        "model": MODEL,
        "answers": {"operational_intent": {
            "type": "choice",
            "choice": label,
            "probabilities": probabilities,
            "confidence": 1.0,
        }},
        "usage": {"input_tokens": 7, "output_tokens": 1},
    }).encode("utf-8"))


if __name__ == "__main__":
    unittest.main()
