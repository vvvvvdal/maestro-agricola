#!/usr/bin/env python3
"""Build or verify the Python/Kotlin intent-classifier parity fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

from intent_model import IntentModel


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "shared" / "ai" / "intent_model.json"
FIXTURE_PATH = ROOT / "shared" / "ai" / "parity_cases.json"
THRESHOLD = 0.40
PARITY_INPUTS = (
    ("spray_uppercase_accent", "PULVERIZE ESTE TALHÃO", "SPRAY"),
    ("spray_phrase", "pode aplicar o defensivo aqui", "SPRAY"),
    ("spray_explicit_plot_numeric", "pulverize no plot-03", "SPRAY"),
    ("spray_explicit_plot_words", "pulverize no plot três", "SPRAY"),
    ("confirm_phrase", "sim, pode continuar", "CONFIRM"),
    ("confirm_synonym", "confirmo a ordem", "CONFIRM"),
    ("cancel_accent", "não envie esse comando", "CANCEL"),
    ("cancel_phrase", "cancele agora", "CANCEL"),
    ("unknown_domain", "qual é a cotação do dólar", "UNKNOWN"),
    ("unknown_request", "conte uma história", "UNKNOWN"),
    ("threshold_rejection", "onde está meu celular", "UNKNOWN"),
    ("cancel_threshold_rejection", "interrompa o comando", "UNKNOWN"),
    ("unknown_vocabulary", "xyzzy quux", "UNKNOWN"),
)


def build_fixture(model_path: Path = MODEL_PATH) -> dict:
    model_bytes = model_path.read_bytes()
    model = IntentModel(json.loads(model_bytes))
    cases = []
    for case_id, text, expected_label in PARITY_INPUTS:
        prediction = model.predict_with_threshold(text, threshold=THRESHOLD)
        if prediction.label != expected_label:
            raise RuntimeError(
                f"regressão semântica em {case_id}: esperado {expected_label}, obtido {prediction.label}"
            )
        cases.append({
            "id": case_id,
            "text": text,
            "expected_label": expected_label,
            "expected_confidence": prediction.confidence,
        })
    return {
        "schema_version": "1.0",
        "model_sha256": hashlib.sha256(model_bytes).hexdigest(),
        "confidence_threshold": THRESHOLD,
        "confidence_tolerance": 1e-9,
        "cases": cases,
    }


def render_fixture(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def validate_fixture(current: dict, expected: dict) -> None:
    for field in (
        "schema_version",
        "model_sha256",
        "confidence_threshold",
        "confidence_tolerance",
    ):
        if current.get(field) != expected[field]:
            raise RuntimeError(
                f"fixture de paridade diverge em {field}: "
                f"esperado {expected[field]!r}, obtido {current.get(field)!r}"
            )

    current_cases = current.get("cases")
    expected_cases = expected["cases"]
    if not isinstance(current_cases, list) or len(current_cases) != len(expected_cases):
        raise RuntimeError(
            f"fixture de paridade deve conter {len(expected_cases)} casos"
        )

    tolerance = expected["confidence_tolerance"]
    for current_case, expected_case in zip(current_cases, expected_cases):
        case_id = expected_case["id"]
        for field in ("id", "text", "expected_label"):
            if current_case.get(field) != expected_case[field]:
                raise RuntimeError(
                    f"caso {case_id} diverge em {field}: "
                    f"esperado {expected_case[field]!r}, obtido {current_case.get(field)!r}"
                )
        confidence = current_case.get("expected_confidence")
        if not isinstance(confidence, (int, float)):
            raise RuntimeError(f"caso {case_id} não possui confiança numérica")
        if abs(confidence - expected_case["expected_confidence"]) > tolerance:
            raise RuntimeError(
                f"caso {case_id} diverge na confiança: "
                f"esperado {expected_case['expected_confidence']!r}, obtido {confidence!r}"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="Falha se o fixture estiver desatualizado")
    mode.add_argument("--write", action="store_true", help="Atualiza o fixture após validar os rótulos")
    args = parser.parse_args()

    try:
        expected = render_fixture(build_fixture())
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 1

    if args.write:
        FIXTURE_PATH.write_text(expected, encoding="utf-8")
        print(FIXTURE_PATH)
        return 0

    try:
        current = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        validate_fixture(current, build_fixture())
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(
            f"fixture de paridade desatualizado: {exc}; "
            "revise o modelo e execute --write",
            file=sys.stderr,
        )
        return 1
    print(f"paridade atual: {len(PARITY_INPUTS)} casos, modelo {build_fixture()['model_sha256'][:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
