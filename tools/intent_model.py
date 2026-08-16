from __future__ import annotations

import json
import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


TOKEN_RE = re.compile(r"[a-z0-9]+")


def normalize(text: str) -> list[str]:
    folded = unicodedata.normalize("NFKD", text.lower())
    ascii_text = "".join(char for char in folded if not unicodedata.combining(char))
    return TOKEN_RE.findall(ascii_text)


def features(text: str) -> Counter[str]:
    tokens = normalize(text)
    result: Counter[str] = Counter(f"u:{token}" for token in tokens)
    result.update(f"b:{left}_{right}" for left, right in zip(tokens, tokens[1:]))
    for token in tokens:
        if len(token) >= 6:
            result[f"p6:{token[:6]}"] += 1
            result[f"s6:{token[-6:]}"] += 1
    return Counter({feature: 1 for feature in result})


@dataclass(frozen=True)
class Prediction:
    label: str
    confidence: float
    scores: dict[str, float]


class IntentModel:
    def __init__(self, payload: dict):
        if payload.get("model_type") != "linear_softmax":
            raise ValueError("unsupported intent model")
        self.labels = tuple(payload["labels"])
        self.bias = payload["bias"]
        self.weights = payload["weights"]
        self.vocabulary = set().union(*(values.keys() for values in self.weights.values()))

    @classmethod
    def load(cls, path: Path) -> "IntentModel":
        return cls(json.loads(path.read_text(encoding="utf-8")))

    def predict(self, text: str) -> Prediction:
        counts = features(text)
        known_counts = {token: count for token, count in counts.items() if token in self.vocabulary}
        if not known_counts:
            scores = {label: 0.0 for label in self.labels}
            scores["UNKNOWN"] = 1.0
            return Prediction("UNKNOWN", 1.0, scores)
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
        return Prediction(best_label, confidence, scores)

    def predict_with_threshold(self, text: str, threshold: float = 0.40) -> Prediction:
        prediction = self.predict(text)
        if prediction.label != "UNKNOWN" and prediction.confidence < threshold:
            return Prediction("UNKNOWN", prediction.confidence, prediction.scores)
        return prediction
