from __future__ import annotations

import json
import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


TOKEN_RE = re.compile(r"[a-z0-9]+")


def normalize_text(text: str) -> str:
    folded = unicodedata.normalize("NFKD", text.lower())
    ascii_text = "".join(char for char in folded if not unicodedata.combining(char))
    return " ".join(TOKEN_RE.findall(ascii_text))


def normalize(text: str) -> list[str]:
    return normalize_text(text).split()


def features(text: str) -> Counter[str]:
    tokens = normalize(text)
    result: Counter[str] = Counter(f"u:{token}" for token in tokens)
    result.update(f"b:{left}_{right}" for left, right in zip(tokens, tokens[1:]))
    for token in tokens:
        padded = f"^{token}$"
        for size in range(3, 6):
            result.update(f"c{size}:{padded[index:index + size]}" for index in range(len(padded) - size + 1))
    return Counter({feature: 1 for feature in result})


@dataclass(frozen=True)
class Prediction:
    label: str
    confidence: float
    scores: dict[str, float]
    source: str = "MODEL"


class IntentModel:
    def __init__(self, payload: dict):
        if payload.get("model_type") not in {"linear_softmax", "hybrid_regex_linear_softmax"}:
            raise ValueError("unsupported intent model")
        self.labels = tuple(payload["labels"])
        self.bias = payload["bias"]
        self.weights = payload["weights"]
        self.vocabulary = set().union(*(values.keys() for values in self.weights.values()))
        self.rules = tuple(
            (rule["label"], tuple(re.compile(pattern) for pattern in rule["patterns"]))
            for rule in payload.get("deterministic_rules", ())
        )

    def match_rule(self, text: str) -> str | None:
        normalized = normalize_text(text)
        for label, patterns in self.rules:
            if any(pattern.search(normalized) for pattern in patterns):
                return label
        return None

    @classmethod
    def load(cls, path: Path) -> "IntentModel":
        return cls(json.loads(path.read_text(encoding="utf-8")))

    def predict(self, text: str) -> Prediction:
        rule_label = self.match_rule(text)
        if rule_label is not None:
            return Prediction(rule_label, 1.0, {label: float(label == rule_label) for label in self.labels}, "RULE")

        counts = features(text)
        known_counts = {token: count for token, count in counts.items() if token in self.vocabulary}
        if not known_counts:
            scores = {label: 0.0 for label in self.labels}
            scores["UNKNOWN"] = 1.0
            return Prediction("UNKNOWN", 1.0, scores, "MODEL")
        scores: dict[str, float] = {}
        for label in self.labels:
            score = float(self.bias[label])
            weights = self.weights[label]
            for token, count in known_counts.items():
                score += count * float(weights.get(token, 0.0))
            scores[label] = score

        best_label = max(scores, key=scores.get)
        peak = max(scores.values())
        denominator = sum(math.exp(value - peak) for value in scores.values())
        confidence = math.exp(scores[best_label] - peak) / denominator
        return Prediction(best_label, confidence, scores, "MODEL")

    def predict_with_threshold(self, text: str, threshold: float = 0.40) -> Prediction:
        prediction = self.predict(text)
        if prediction.label != "UNKNOWN" and prediction.confidence < threshold:
            return Prediction("UNKNOWN", prediction.confidence, prediction.scores, prediction.source)
        return prediction
