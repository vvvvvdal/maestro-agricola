from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from jev_intent_harness import load_jev_fixture  # noqa: E402
from jev_remote_recovery_final import (  # noqa: E402
    MAX_RECOVERY_ATTEMPTS,
    RECOVERY_CASES,
    RECOVERY_COST_CAP_USD,
    RECOVERY_DATASET_SHA256,
    ensure_recovery_fixture_absent,
    load_recovery_cases,
    reserve_recovery_evaluation,
    run_recovery_final,
    sha256,
)
from jev_remote_smoke import LABELS, MODEL, HttpResponse, worst_case_cost_usd  # noqa: E402


class JevRemoteRecoveryFinalTest(unittest.TestCase):
    def test_recovery_corpus_is_independent_frozen_and_harness_compatible(self) -> None:
        cases = load_recovery_cases()

        fixture = run_recovery_final(cases, "not-recorded", lambda _body, _key: ok_response("UNKNOWN"))

        self.assertEqual(RECOVERY_CASES, len(cases))
        self.assertEqual(RECOVERY_DATASET_SHA256, sha256(ROOT / "docs/study-groups/jev-rl-2026-10-01/corpus/final-recovery.tsv"))
        self.assertEqual(Counter({label: 10 for label in LABELS}), Counter(case.gold_label for case in cases))
        self.assertFalse(normalized_texts(cases) & normalized_texts_from_tsv("development.tsv"))
        self.assertFalse(normalized_texts(cases) & normalized_texts_from_tsv("final.tsv"))
        self.assertEqual(
            (MODEL, fixture["results"]),
            load_jev_fixture_from_result(fixture, {case.case_id for case in cases}),
        )
        serialized = json.dumps(fixture)
        self.assertTrue(all(case.text not in serialized for case in cases))
        self.assertNotIn("not-recorded", serialized)

    def test_rejects_changed_corpus_and_reserves_only_one_recovery_round(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            changed_corpus = root / "recovery.tsv"
            changed_corpus.write_text("id\ttext\tgold_label\tcategory\n", encoding="utf-8")
            existing_fixture = root / "fixture.json"
            existing_fixture.write_text("{}", encoding="utf-8")
            reservation = root / "reservation.json"

            with self.assertRaisesRegex(ValueError, "hash"):
                load_recovery_cases(changed_corpus)
            with self.assertRaisesRegex(FileExistsError, "second recovery"):
                ensure_recovery_fixture_absent(existing_fixture)
            reserve_recovery_evaluation(reservation)
            with self.assertRaisesRegex(FileExistsError, "second recovery"):
                reserve_recovery_evaluation(reservation)

    def test_retries_once_per_case_and_never_exceeds_global_limit(self) -> None:
        calls = 0

        def overloaded(_body: bytes, _key: str) -> HttpResponse:
            nonlocal calls
            calls += 1
            return HttpResponse(529, {}, b"")

        fixture = run_recovery_final(load_recovery_cases(), "key", overloaded, lambda _delay: None)

        self.assertEqual(MAX_RECOVERY_ATTEMPTS, calls)
        self.assertTrue(all(result["error"]["code"] == "OVERLOADED" for result in fixture["results"].values()))

    def test_timeout_does_not_retry_and_upper_bound_stays_in_subcap(self) -> None:
        calls = 0

        def timed_out(_body: bytes, _key: str) -> HttpResponse:
            nonlocal calls
            calls += 1
            raise TimeoutError

        fixture = run_recovery_final(load_recovery_cases(), "key", timed_out)

        self.assertEqual(RECOVERY_CASES, calls)
        self.assertTrue(all(result["error"]["code"] == "TIMEOUT" for result in fixture["results"].values()))
        self.assertLess(worst_case_cost_usd(MAX_RECOVERY_ATTEMPTS), RECOVERY_COST_CAP_USD)


def normalized_texts(cases: list) -> set[str]:
    return {" ".join(case.text.casefold().split()) for case in cases}


def normalized_texts_from_tsv(name: str) -> set[str]:
    path = ROOT / "docs/study-groups/jev-rl-2026-10-01/corpus" / name
    with path.open(encoding="utf-8", newline="") as source:
        return {" ".join(row["text"].casefold().split()) for row in csv.DictReader(source, delimiter="\t")}


def load_jev_fixture_from_result(fixture: dict, case_ids: set[str]) -> tuple[str, dict]:
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
