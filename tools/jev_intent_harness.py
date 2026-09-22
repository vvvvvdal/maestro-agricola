#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from intent_model import IntentModel


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = ROOT / "docs/study-groups/jev-rl-2026-10-01/corpus/development.tsv"
DEFAULT_LOCAL_MODEL = ROOT / "shared/ai/intent_model.json"
LABELS = frozenset({"SPRAY", "DOCK", "UNDOCK", "CONFIRM", "CANCEL", "UNKNOWN"})
ERROR_CODES = frozenset({
    "TIMEOUT",
    "RATE_LIMITED",
    "OVERLOADED",
    "UNAUTHORIZED",
    "INVALID_REQUEST",
    "INVALID_RESPONSE",
    "TRANSPORT",
    "HTTP_ERROR",
})
THRESHOLD = 0.40
PROBABILITY_TOLERANCE = 0.001


@dataclass(frozen=True)
class CorpusCase:
    case_id: str
    text: str
    gold_label: str
    category: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Executa LocalIntentClassifier e uma fixture Jev no mesmo corpus."
    )
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--jev-fixture", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--local-model", type=Path, default=DEFAULT_LOCAL_MODEL)
    return parser.parse_args()


def load_cases(path: Path) -> list[CorpusCase]:
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        if reader.fieldnames != ["id", "text", "gold_label", "category"]:
            raise ValueError("corpus TSV must have id, text, gold_label, category columns")
        cases = [
            CorpusCase(
                case_id=row["id"].strip(),
                text=row["text"].strip(),
                gold_label=row["gold_label"].strip(),
                category=row["category"].strip(),
            )
            for row in reader
            if any(row.values())
        ]

    if not cases or any(not all(case.__dict__.values()) for case in cases):
        raise ValueError("corpus contains an empty case field")
    if any(case.gold_label not in LABELS for case in cases):
        raise ValueError("corpus contains an unsupported gold label")
    if len({case.case_id for case in cases}) != len(cases):
        raise ValueError("corpus contains duplicate case ids")
    return cases


def load_jev_fixture(path: Path, case_ids: set[str]) -> tuple[str, dict[str, dict[str, Any]]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "1.0":
        raise ValueError("unsupported Jev fixture schema")
    model = payload.get("model")
    results = payload.get("results")
    safe_fixture_model = safe_model(model)
    if safe_fixture_model is None:
        raise ValueError("Jev fixture model is required")
    if not isinstance(results, dict) or set(results) != case_ids:
        raise ValueError("Jev fixture ids must match corpus ids exactly")
    if not all(isinstance(value, dict) for value in results.values()):
        raise ValueError("Jev fixture results must be objects")
    return safe_fixture_model, results


def validated_answer(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None

    choice = value.get("choice")
    probabilities = value.get("probabilities")
    confidence = value.get("confidence")
    if not isinstance(choice, str) or choice not in LABELS or not isinstance(probabilities, dict):
        return None
    if set(probabilities) != LABELS or not is_probability(confidence):
        return None

    values = list(probabilities.values())
    if not all(is_probability(candidate) for candidate in values):
        return None
    if abs(sum(values) - 1.0) > PROBABILITY_TOLERANCE:
        return None

    selected = probabilities[choice]
    if any(candidate > selected + PROBABILITY_TOLERANCE for candidate in values):
        return None
    return {
        "choice": choice,
        "probabilities": {label: probabilities[label] for label in sorted(LABELS)},
        "confidence": confidence,
    }


def prediction_from_answer(answer: dict[str, Any]) -> dict[str, Any]:
    choice = answer["choice"]
    selected = answer["probabilities"][choice]
    if choice != "UNKNOWN" and selected < THRESHOLD:
        return prediction("UNKNOWN", selected, "JEV")
    return prediction(choice, selected, "JEV")


def is_probability(value: Any) -> bool:
    return isinstance(value, (float, int)) and not isinstance(value, bool) and math.isfinite(value) and 0.0 <= value <= 1.0


def prediction(label: str, confidence: float, source: str) -> dict[str, Any]:
    return {"label": label, "confidence": confidence, "source": source}


def unknown_prediction() -> dict[str, Any]:
    return prediction("UNKNOWN", 0.0, "JEV")


def non_negative_number(value: Any) -> float | int | None:
    if isinstance(value, (float, int)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0:
        return value
    return None


def safe_model(value: Any) -> str | None:
    if isinstance(value, str) and value and value.replace("-", "").replace("_", "").replace(".", "").isalnum():
        return value
    return None


def safe_usage(value: Any) -> dict[str, int] | None:
    if not isinstance(value, dict):
        return None
    input_tokens = value.get("input_tokens")
    output_tokens = value.get("output_tokens")
    if not all(isinstance(tokens, int) and not isinstance(tokens, bool) and tokens >= 0 for tokens in (input_tokens, output_tokens)):
        return None
    return {"input_tokens": input_tokens, "output_tokens": output_tokens}


def safe_error_code(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, dict) and value.get("code") in ERROR_CODES:
        return value["code"]
    return "INVALID_RESPONSE"


def local_result(model: IntentModel, text: str) -> dict[str, Any]:
    started_at = time.perf_counter_ns()
    value = model.predict_with_threshold(text, THRESHOLD)
    latency_ms = (time.perf_counter_ns() - started_at) / 1_000_000
    return {
        "prediction": prediction(value.label, value.confidence, value.source),
        "latency_ms": latency_ms,
    }


def jev_result(model: str, fixture: dict[str, Any]) -> dict[str, Any]:
    latency_ms = non_negative_number(fixture.get("latency_ms"))
    error_code = safe_error_code(fixture.get("error"))
    answer = validated_answer(fixture.get("answer"))
    if latency_ms is None:
        error_code = "INVALID_RESPONSE"
    if error_code is None and answer is None:
        error_code = "INVALID_RESPONSE"

    return {
        "requested_model": model,
        "response_model": safe_model(fixture.get("response_model")),
        "answer": answer if error_code is None else None,
        "usage": safe_usage(fixture.get("usage")),
        "latency_ms": latency_ms,
        "cost_usd": non_negative_number(fixture.get("cost_usd")),
        "error": {"code": error_code} if error_code is not None else None,
        "prediction": prediction_from_answer(answer) if error_code is None else unknown_prediction(),
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_harness(
    dataset: Path,
    local_model_path: Path,
    jev_fixture_path: Path,
) -> dict[str, Any]:
    cases = load_cases(dataset)
    jev_model, fixture_results = load_jev_fixture(
        jev_fixture_path,
        {case.case_id for case in cases},
    )
    local_model = IntentModel.load(local_model_path)

    return {
        "schema_version": "1.0",
        "dataset": {
            "sha256": sha256(dataset),
            "cases": len(cases),
        },
        "local_model_sha256": sha256(local_model_path),
        "jev_fixture_sha256": sha256(jev_fixture_path),
        "results": [
            {
                "id": case.case_id,
                "gold_label": case.gold_label,
                "category": case.category,
                "local": local_result(local_model, case.text),
                "jev": jev_result(jev_model, fixture_results[case.case_id]),
            }
            for case in cases
        ],
    }


def main() -> None:
    args = parse_args()
    report = run_harness(args.dataset, args.local_model, args.jev_fixture)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(report['results'])} cases to {args.output}")


if __name__ == "__main__":
    main()
