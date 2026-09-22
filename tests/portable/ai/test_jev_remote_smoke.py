from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from jev_intent_harness import load_jev_fixture  # noqa: E402
from jev_remote_smoke import (  # noqa: E402
    LABELS,
    MAX_TOTAL_ATTEMPTS,
    MODEL,
    HttpResponse,
    SmokeCase,
    run_smoke,
    worst_case_cost_usd,
)


class JevRemoteSmokeTest(unittest.TestCase):
    def test_emits_harness_compatible_sanitized_fixture(self) -> None:
        seen_bodies: list[dict] = []

        def transport(body: bytes, _api_key: str) -> HttpResponse:
            seen_bodies.append(json.loads(body))
            return ok_response("SPRAY")

        fixture = run_smoke([case("case-001", "SPRAY")], "not-recorded", transport)

        self.assertEqual(MODEL, fixture["model"])
        self.assertEqual("choice", seen_bodies[0]["questions"]["operational_intent"]["type"])
        self.assertEqual(set(LABELS), set(seen_bodies[0]["questions"]["operational_intent"]["criteria"]))
        result = fixture["results"]["case-001"]
        self.assertEqual("SPRAY", result["answer"]["choice"])
        self.assertNotIn("text", result)
        self.assertNotIn("not-recorded", json.dumps(fixture))
        self.assertGreaterEqual(result["cost_usd"], 0.0)
        self.assertEqual(
            (MODEL, fixture["results"]),
            load_jev_fixture_from_result(fixture, {"case-001"}),
        )

    def test_retries_rate_limit_once_when_retry_after_is_bounded(self) -> None:
        responses = iter([HttpResponse(429, {"Retry-After": "0.5"}, b""), ok_response("DOCK")])
        delays: list[float] = []

        fixture = run_smoke([case("case-001", "DOCK")], "key", lambda *_: next(responses), delays.append)

        self.assertEqual([0.5], delays)
        self.assertEqual("DOCK", fixture["results"]["case-001"]["answer"]["choice"])

    def test_does_not_retry_late_rate_limit_or_unauthorized_or_timeout(self) -> None:
        late = run_smoke(
            [case("case-001", "UNKNOWN")],
            "key",
            lambda *_: HttpResponse(429, {"Retry-After": "2"}, b""),
        )
        unauthorized = run_smoke(
            [case("case-001", "UNKNOWN")],
            "key",
            lambda *_: HttpResponse(401, {}, b""),
        )
        timed_out = run_smoke([case("case-001", "UNKNOWN")], "key", timeout_transport)

        self.assertEqual("RATE_LIMITED", late["results"]["case-001"]["error"]["code"])
        self.assertEqual("UNAUTHORIZED", unauthorized["results"]["case-001"]["error"]["code"])
        self.assertEqual("TIMEOUT", timed_out["results"]["case-001"]["error"]["code"])

    def test_rejects_response_without_choice_type_or_model(self) -> None:
        missing_model = json.loads(ok_response("SPRAY").body)
        missing_model.pop("model")
        wrong_type = json.loads(ok_response("SPRAY").body)
        wrong_type["answers"]["operational_intent"]["type"] = "boolean"

        missing_model_fixture = run_smoke(
            [case("case-001", "SPRAY")],
            "key",
            lambda *_: HttpResponse(200, {}, json.dumps(missing_model).encode("utf-8")),
        )
        wrong_type_fixture = run_smoke(
            [case("case-001", "SPRAY")],
            "key",
            lambda *_: HttpResponse(200, {}, json.dumps(wrong_type).encode("utf-8")),
        )

        self.assertEqual("INVALID_RESPONSE", missing_model_fixture["results"]["case-001"]["error"]["code"])
        self.assertEqual("INVALID_RESPONSE", wrong_type_fixture["results"]["case-001"]["error"]["code"])

    def test_stops_at_global_attempt_limit(self) -> None:
        calls = 0

        def overloaded(*_args: object) -> HttpResponse:
            nonlocal calls
            calls += 1
            return HttpResponse(529, {}, b"")

        cases = [case(f"case-{index:03d}", label) for index, label in enumerate(LABELS, start=1)]
        fixture = run_smoke(cases, "key", overloaded, lambda _delay: None)

        self.assertEqual(MAX_TOTAL_ATTEMPTS, calls)
        self.assertIn("ATTEMPT_LIMIT", {result["error"]["code"] for result in fixture["results"].values()})

    def test_documented_upper_bound_stays_below_approved_smoke_cap(self) -> None:
        self.assertLess(worst_case_cost_usd(), 0.50)


def load_jev_fixture_from_result(fixture: dict, case_ids: set[str]) -> tuple[str, dict]:
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", encoding="utf-8") as output:
        json.dump(fixture, output)
        output.flush()
        return load_jev_fixture(Path(output.name), case_ids)


def case(case_id: str, label: str) -> SmokeCase:
    return SmokeCase(case_id, "synthetic request", label, "test")


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


def timeout_transport(*_args: object) -> HttpResponse:
    raise TimeoutError


if __name__ == "__main__":
    unittest.main()
