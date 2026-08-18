#!/usr/bin/env python3
"""Resolve a mapped plot from visual and explicit spoken identifiers."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sys
import unicodedata


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGET_MAP = ROOT / "robot_ws" / "src" / "maestro_robot_bridge" / "config" / "targets.json"
NUMBER_WORDS = {
    "zero": 0,
    "um": 1,
    "uma": 1,
    "dois": 2,
    "duas": 2,
    "tres": 3,
    "quatro": 4,
    "cinco": 5,
    "seis": 6,
    "sete": 7,
    "oito": 8,
    "nove": 9,
}


@dataclass(frozen=True)
class TargetResolution:
    status: str
    target_id: str | None
    source: str | None


def tokens(text: str) -> list[str]:
    folded = unicodedata.normalize("NFKD", text.lower())
    ascii_text = "".join(char for char in folded if not unicodedata.combining(char))
    return re.findall(r"[a-z0-9]+", ascii_text)


def canonical_target_id(value: str | None) -> str | None:
    if not value:
        return None
    match = re.fullmatch(r"plot[-_ ]?(\d{1,3})", value.strip().lower())
    if not match:
        return value.strip().lower()
    return f"plot-{int(match.group(1)):02d}"


def extract_spoken_target_id(transcript: str) -> str | None:
    current = tokens(transcript)
    for index, token in enumerate(current):
        if token not in {"plot", "talhao"} or index + 1 >= len(current):
            continue
        first = current[index + 1]
        if first.isdigit():
            return f"plot-{int(first):02d}"
        if first in NUMBER_WORDS:
            digits = [NUMBER_WORDS[first]]
            if index + 2 < len(current) and current[index + 2] in NUMBER_WORDS:
                digits.append(NUMBER_WORDS[current[index + 2]])
            number = digits[0] if len(digits) == 1 else digits[0] * 10 + digits[1]
            return f"plot-{number:02d}"
    return None


def resolve_target(
    visual_target_id: str | None,
    transcript: str,
    allowed_target_ids: set[str],
) -> TargetResolution:
    visual = canonical_target_id(visual_target_id)
    spoken = extract_spoken_target_id(transcript)

    if visual and spoken and visual != spoken:
        return TargetResolution("CONFLICT", None, None)
    candidate = visual or spoken
    if candidate and candidate not in allowed_target_ids:
        return TargetResolution("UNKNOWN", None, None)
    if visual and spoken:
        return TargetResolution("RESOLVED", candidate, "AGREED")
    if visual:
        return TargetResolution("RESOLVED", visual, "VISUAL")
    if spoken:
        return TargetResolution("RESOLVED", spoken, "VOICE")
    return TargetResolution("NEEDS_VISUAL", None, None)


def load_allowed_target_ids(path: Path) -> set[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    targets = payload.get("targets")
    if payload.get("schema_version") != "1.0" or not isinstance(targets, dict):
        raise ValueError(f"mapa de alvos inválido: {path}")
    return set(targets)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("transcript")
    parser.add_argument("--visual-target")
    parser.add_argument("--target-map", type=Path, default=DEFAULT_TARGET_MAP)
    args = parser.parse_args()
    try:
        result = resolve_target(
            args.visual_target,
            args.transcript,
            load_allowed_target_ids(args.target_map),
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(asdict(result), ensure_ascii=False, sort_keys=True))
    return 0 if result.status == "RESOLVED" else 2


if __name__ == "__main__":
    sys.exit(main())
