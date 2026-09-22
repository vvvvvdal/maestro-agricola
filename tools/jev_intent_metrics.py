#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


LABELS = ("CANCEL", "CONFIRM", "DOCK", "SPRAY", "UNDOCK", "UNKNOWN")
LABEL_SET = frozenset(LABELS)
DANGEROUS_POSITIVE_LABELS = frozenset({"SPRAY", "DOCK", "UNDOCK", "CONFIRM"})
SAFE_NEGATIVE_LABELS = frozenset({"CANCEL", "UNKNOWN"})
ECE_BINS = 10


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Calcula metricas de um relatorio Jev pareado.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def load_report(path: Path) -> dict[str, Any]:
    report = json.loads(path.read_text(encoding="utf-8"))
    if report.get("schema_version") != "1.1" or not isinstance(report.get("results"), list):
        raise ValueError("unsupported paired harness schema")
    return report


def calculate_metrics(report: dict[str, Any]) -> dict[str, Any]:
    cases = validate_cases(report["results"])
    return {
        "schema_version": "1.0",
        "dataset": report["dataset"],
        "local_model_sha256": report["local_model_sha256"],
        "jev_fixture_sha256": report["jev_fixture_sha256"],
        "backends": {backend: backend_metrics(cases, backend) for backend in ("local", "jev")},
    }


def validate_cases(results: list[Any]) -> list[dict[str, Any]]:
    if not results or not all(isinstance(case, dict) for case in results):
        raise ValueError("paired harness report requires case objects")
    ids = [case.get("id") for case in results]
    if any(not isinstance(case_id, str) or not case_id for case_id in ids) or len(set(ids)) != len(ids):
        raise ValueError("paired harness case ids must be unique non-empty strings")
    if any(case.get("gold_label") not in LABEL_SET for case in results):
        raise ValueError("paired harness contains unsupported gold labels")
    return results


def backend_metrics(cases: list[dict[str, Any]], backend: str) -> dict[str, Any]:
    confusion = {expected: {predicted: 0 for predicted in LABELS} for expected in LABELS}
    dangerous, failures, vectors, latencies, models = [], [], [], [], set()
    total_cost, known_cost = 0.0, 0
    correct = 0
    for case in cases:
        result = case.get(backend)
        if not isinstance(result, dict):
            raise ValueError(f"{case['id']}: missing {backend} result")
        predicted, confidence = operational_prediction(case["id"], result)
        expected = case["gold_label"]
        confusion[expected][predicted] += 1
        correct += int(expected == predicted)
        if expected in SAFE_NEGATIVE_LABELS and predicted in DANGEROUS_POSITIVE_LABELS:
            dangerous.append({"id": case["id"], "gold_label": expected, "predicted_label": predicted, "confidence": confidence})
        vector, top_label = probability_vector(result, backend)
        if vector is not None:
            vectors.append((expected, vector, top_label))
        if is_non_negative_number(result.get("latency_ms")):
            latencies.append(float(result["latency_ms"]))
        if backend == "jev":
            if result.get("error") is not None:
                failures.append({"id": case["id"], "code": error_code(result["error"])})
            if is_non_negative_number(result.get("cost_usd")):
                total_cost += float(result["cost_usd"])
                known_cost += 1
            model = result.get("response_model") or result.get("requested_model")
            if isinstance(model, str):
                models.add(model)
    total = len(cases)
    return {
        "examples": total,
        "correct": correct,
        "accuracy": correct / total,
        "macro_f1": macro_f1(confusion),
        "confusion_matrix": confusion,
        "unsafe_accepts": dangerous,
        "unsafe_accept_rate": len(dangerous) / total,
        "failures": failures,
        "failure_rate": len(failures) / total,
        "probability_coverage": len(vectors) / total,
        "calibration": calibration_metrics(vectors),
        "latency_ms": latency_metrics(latencies),
        "cost_usd": {"total": total_cost, "known_cases": known_cost},
        "models": sorted(models),
    }


def operational_prediction(case_id: str, result: dict[str, Any]) -> tuple[str, float]:
    prediction = result.get("prediction")
    if not isinstance(prediction, dict) or prediction.get("label") not in LABEL_SET or not is_probability(prediction.get("confidence")):
        raise ValueError(f"{case_id}: invalid operational prediction")
    return prediction["label"], float(prediction["confidence"])


def probability_vector(result: dict[str, Any], backend: str) -> tuple[dict[str, float] | None, str | None]:
    if backend == "jev" and result.get("error") is not None:
        return None, None
    answer = result.get("answer") if backend == "jev" else None
    candidate = answer.get("probabilities") if isinstance(answer, dict) else result.get("probabilities")
    choice = answer.get("choice") if isinstance(answer, dict) else None
    if not isinstance(candidate, dict) or set(candidate) != LABEL_SET or not all(is_probability(value) for value in candidate.values()):
        return None, None
    vector = {label: float(candidate[label]) for label in LABELS}
    if abs(sum(vector.values()) - 1.0) > 0.001:
        return None, None
    top_label = choice if choice in LABEL_SET else max(LABELS, key=vector.get)
    if any(value > vector[top_label] + 0.001 for value in vector.values()):
        return None, None
    return vector, top_label


def macro_f1(confusion: dict[str, dict[str, int]]) -> float:
    values = []
    for label in LABELS:
        tp = confusion[label][label]
        fp = sum(confusion[expected][label] for expected in LABELS if expected != label)
        fn = sum(confusion[label][predicted] for predicted in LABELS if predicted != label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        values.append(2 * precision * recall / (precision + recall) if precision + recall else 0.0)
    return sum(values) / len(values)


def calibration_metrics(values: list[tuple[str, dict[str, float], str]]) -> dict[str, Any]:
    if not values:
        return {"examples": 0, "brier_multiclass": None, "top_label_ece": None, "reliability_bins": reliability_bins([])}
    brier = sum(sum((vector[label] - float(label == expected)) ** 2 for label in LABELS) for expected, vector, _ in values) / len(values)
    observations = [[] for _ in range(ECE_BINS)]
    for expected, vector, top_label in values:
        confidence = vector[top_label]
        observations[min(int(confidence * ECE_BINS), ECE_BINS - 1)].append((float(top_label == expected), confidence))
    bins = reliability_bins(observations)
    ece = sum(bin_["examples"] / len(values) * abs(bin_["accuracy"] - bin_["confidence"]) for bin_ in bins if bin_["examples"])
    return {"examples": len(values), "brier_multiclass": brier, "top_label_ece": ece, "reliability_bins": bins}


def reliability_bins(observations: list[list[tuple[float, float]]]) -> list[dict[str, Any]]:
    if not observations:
        observations = [[] for _ in range(ECE_BINS)]
    bins = []
    for index, values in enumerate(observations):
        accuracy = sum(value[0] for value in values) / len(values) if values else None
        confidence = sum(value[1] for value in values) / len(values) if values else None
        bins.append({"lower": index / ECE_BINS, "upper": (index + 1) / ECE_BINS, "examples": len(values), "accuracy": accuracy, "confidence": confidence})
    return bins


def latency_metrics(values: list[float]) -> dict[str, float | int | None]:
    return {"examples": len(values), "p50": percentile(values, 0.50), "p95": percentile(values, 0.95)}


def percentile(values: list[float], fraction: float) -> float | None:
    return sorted(values)[math.ceil(fraction * len(values)) - 1] if values else None


def error_code(error: Any) -> str:
    return error["code"] if isinstance(error, dict) and isinstance(error.get("code"), str) else "INVALID_RESPONSE"


def is_non_negative_number(value: Any) -> bool:
    return isinstance(value, (float, int)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0


def is_probability(value: Any) -> bool:
    return is_non_negative_number(value) and value <= 1.0


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    args = parse_args()
    metrics = calculate_metrics(load_report(args.input))
    metrics["input_sha256"] = sha256(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(f"wrote metrics for {metrics['backends']['local']['examples']} cases to {args.output}")


if __name__ == "__main__":
    main()
