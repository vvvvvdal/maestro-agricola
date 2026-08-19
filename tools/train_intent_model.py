from __future__ import annotations

import argparse
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

from intent_model import IntentModel, features


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "shared" / "ai" / "dataset" / "intents.tsv"
MODEL = ROOT / "shared" / "ai" / "intent_model.json"
REPORT = ROOT / "shared" / "ai" / "evaluation.json"
EPOCHS = 350
LEARNING_RATE = 0.04
L2 = 0.0005
CONFIDENCE_THRESHOLD = 0.40
ARTIFACT_FLOAT_TOLERANCE = 1e-12


def load_examples() -> list[tuple[str, str]]:
    rows = []
    for index, line in enumerate(DATASET.read_text(encoding="utf-8").splitlines()):
        if index == 0 or not line.strip():
            continue
        label, text = line.split("\t", 1)
        rows.append((label, text))
    return rows


def split(examples: list[tuple[str, str]]) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for label, text in examples:
        grouped[label].append(text)
    train = []
    test = []
    for label, texts in sorted(grouped.items()):
        for index, text in enumerate(texts):
            (test if index % 5 == 4 else train).append((label, text))
    return train, test


def train(examples: list[tuple[str, str]]) -> dict:
    labels = sorted({label for label, _ in examples})
    vocabulary: set[str] = set()
    encoded = []
    for label, text in examples:
        current = features(text)
        vocabulary.update(current)
        encoded.append((label, tuple(current)))

    weights = {label: defaultdict(float) for label in labels}
    bias = {label: 0.0 for label in labels}
    generator = random.Random(20260816)
    for epoch in range(EPOCHS):
        generator.shuffle(encoded)
        learning_rate = LEARNING_RATE / (1.0 + epoch / 120.0)
        for expected, current in encoded:
            scores = {
                label: bias[label] + sum(weights[label][token] for token in current)
                for label in labels
            }
            peak = max(scores.values())
            denominator = sum(math.exp(score - peak) for score in scores.values())
            probabilities = {
                label: math.exp(scores[label] - peak) / denominator
                for label in labels
            }
            for label in labels:
                gradient = probabilities[label] - (1.0 if label == expected else 0.0)
                bias[label] -= learning_rate * gradient
                for token in current:
                    value = weights[label][token]
                    weights[label][token] = value - learning_rate * (gradient + L2 * value)

    compact_weights = {
        label: {
            token: value
            for token, value in sorted(weights[label].items())
            if abs(value) >= 0.0001
        }
        for label in labels
    }

    return {
        "schema_version": "1.0",
        "model_type": "linear_softmax",
        "labels": labels,
        "feature_type": "word_unigrams_bigrams_and_six_character_affixes",
        "bias": bias,
        "weights": compact_weights,
        "epochs": EPOCHS,
        "learning_rate": LEARNING_RATE,
        "l2": L2,
        "training_examples": len(examples),
        "vocabulary_size": len(vocabulary),
    }


def evaluate(model: IntentModel, examples: list[tuple[str, str]]) -> dict:
    labels = list(model.labels)
    confusion = {label: {candidate: 0 for candidate in labels} for label in labels}
    errors = []
    correct = 0
    operational_correct = 0
    for expected, text in examples:
        prediction = model.predict(text)
        operational = model.predict_with_threshold(text, CONFIDENCE_THRESHOLD)
        confusion[expected][prediction.label] += 1
        if prediction.label == expected:
            correct += 1
        else:
            errors.append({
                "text": text,
                "expected": expected,
                "predicted": prediction.label,
                "confidence": prediction.confidence,
            })
        if operational.label == expected:
            operational_correct += 1
    return {
        "examples": len(examples),
        "correct": correct,
        "accuracy": correct / len(examples) if examples else 0.0,
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "operational_correct": operational_correct,
        "operational_accuracy": operational_correct / len(examples) if examples else 0.0,
        "confusion_matrix": confusion,
        "errors": errors,
    }


def build_artifacts() -> tuple[dict, dict]:
    examples = load_examples()
    train_examples, test_examples = split(examples)
    payload = train(train_examples)
    report = evaluate(IntentModel(payload), test_examples)
    report["train_examples"] = len(train_examples)
    report["test_examples"] = len(test_examples)
    return payload, report


def artifacts_equal(current: object, expected: object) -> bool:
    if isinstance(current, float) and isinstance(expected, float):
        return math.isclose(
            current,
            expected,
            rel_tol=0.0,
            abs_tol=ARTIFACT_FLOAT_TOLERANCE,
        )
    if isinstance(current, dict) and isinstance(expected, dict):
        return current.keys() == expected.keys() and all(
            artifacts_equal(current[key], expected[key]) for key in current
        )
    if isinstance(current, list) and isinstance(expected, list):
        return len(current) == len(expected) and all(
            artifacts_equal(current_item, expected_item)
            for current_item, expected_item in zip(current, expected)
        )
    return current == expected


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Treina ou verifica o classificador local.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="compara os artefatos versionados sem escrever no repositório",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload, report = build_artifacts()

    if args.check:
        current_model = json.loads(MODEL.read_text(encoding="utf-8"))
        current_report = json.loads(REPORT.read_text(encoding="utf-8"))
        stale = []
        if not artifacts_equal(current_model, payload):
            stale.append(str(MODEL.relative_to(ROOT)))
        if not artifacts_equal(current_report, report):
            stale.append(str(REPORT.relative_to(ROOT)))
        if stale:
            print("artefatos desatualizados: " + ", ".join(stale), file=sys.stderr)
            print("execute `make model` e revise o diff", file=sys.stderr)
            raise SystemExit(1)
        print("model artifacts: up to date (read-only check)")
    else:
        MODEL.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"model: {MODEL}")

    print(f"raw accuracy: {report['accuracy']:.3f} ({report['correct']}/{report['examples']})")
    print(
        "operational accuracy: "
        f"{report['operational_accuracy']:.3f} "
        f"({report['operational_correct']}/{report['examples']}, threshold={CONFIDENCE_THRESHOLD})"
    )


if __name__ == "__main__":
    main()
