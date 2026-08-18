#!/usr/bin/env python3
"""Decode one allowlisted, central QR target from a still image."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGET_MAP = (
    ROOT
    / "robot_ws"
    / "src"
    / "maestro_robot_bridge"
    / "config"
    / "targets.json"
)


@dataclass(frozen=True)
class QrCandidate:
    value: str
    center_x: float
    center_y: float


@dataclass(frozen=True)
class VisionResult:
    schema_version: str
    status: str
    target_id: str | None
    confidence: float
    captured_at: str
    processed_at: str
    candidate_count: int
    reason: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, sort_keys=True)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def normalize_timestamp(value: str) -> str:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ValueError("timestamp precisa incluir fuso horário")
    return parsed.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def load_allowed_target_ids(path: Path) -> set[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "1.0" or not isinstance(payload.get("targets"), dict):
        raise ValueError(f"mapa de alvos inválido: {path}")
    target_ids = set(payload["targets"])
    if not target_ids or not all(isinstance(value, str) and value for value in target_ids):
        raise ValueError(f"mapa de alvos sem IDs válidos: {path}")
    return target_ids


def is_central(candidate: QrCandidate, central_fraction: float = 0.70) -> bool:
    if not 0.0 < central_fraction <= 1.0:
        raise ValueError("central_fraction deve estar entre 0 e 1")
    margin = (1.0 - central_fraction) / 2.0
    return margin <= candidate.center_x <= 1.0 - margin and margin <= candidate.center_y <= 1.0 - margin


def select_target(
    candidates: Iterable[QrCandidate],
    allowed_target_ids: set[str],
    captured_at: str,
    processed_at: str | None = None,
) -> VisionResult:
    central = [candidate for candidate in candidates if is_central(candidate)]
    completed_at = processed_at or utc_now()

    if not central:
        return VisionResult(
            "1.0", "UNKNOWN", None, 0.0, captured_at, completed_at, 0,
            "nenhum QR decodificado na região central",
        )
    if len(central) > 1:
        return VisionResult(
            "1.0", "AMBIGUOUS", None, 0.0, captured_at, completed_at, len(central),
            "mais de um QR decodificado na região central",
        )

    candidate = central[0]
    if candidate.value not in allowed_target_ids:
        return VisionResult(
            "1.0", "UNKNOWN", None, 0.0, captured_at, completed_at, 1,
            "QR decodificado não existe no mapa de alvos",
        )
    return VisionResult(
        "1.0", "DETECTED", candidate.value, 1.0, captured_at, completed_at, 1,
        "QR decodificado e presente no mapa de alvos",
    )


def _opencv() -> Any:
    try:
        import cv2  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "OpenCV Python não está disponível; a task não instala dependências automaticamente"
        ) from exc
    return cv2


def decode_candidates(image: Any, cv2_module: Any | None = None) -> list[QrCandidate]:
    cv2 = cv2_module or _opencv()
    if image is None or not hasattr(image, "shape") or len(image.shape) < 2:
        raise ValueError("imagem inválida")
    height, width = image.shape[:2]
    if width <= 0 or height <= 0:
        raise ValueError("imagem vazia")

    detector = cv2.QRCodeDetector()
    found, decoded_values, points, _ = detector.detectAndDecodeMulti(image)
    if found and points is not None:
        return [
            QrCandidate(
                value=value,
                center_x=float(polygon[:, 0].mean()) / width,
                center_y=float(polygon[:, 1].mean()) / height,
            )
            for value, polygon in zip(decoded_values, points)
            if value
        ]

    value, single_points, _ = detector.detectAndDecode(image)
    if not value or single_points is None:
        return []
    polygon = single_points[0] if len(single_points.shape) == 3 else single_points
    return [
        QrCandidate(
            value=value,
            center_x=float(polygon[:, 0].mean()) / width,
            center_y=float(polygon[:, 1].mean()) / height,
        )
    ]


def detect_image(
    image: Any,
    allowed_target_ids: set[str],
    captured_at: str,
    cv2_module: Any | None = None,
) -> VisionResult:
    return select_target(
        decode_candidates(image, cv2_module=cv2_module),
        allowed_target_ids,
        captured_at,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, help="Imagem a analisar; nunca é alterada ou copiada")
    parser.add_argument("--target-map", type=Path, default=DEFAULT_TARGET_MAP)
    parser.add_argument("--captured-at", help="Timestamp ISO-8601 da captura; padrão: instante da execução")
    args = parser.parse_args()

    try:
        captured_at = normalize_timestamp(args.captured_at) if args.captured_at else utc_now()
        allowed = load_allowed_target_ids(args.target_map)
        cv2 = _opencv()
        image = cv2.imread(str(args.image))
        if image is None:
            raise ValueError(f"não foi possível abrir a imagem: {args.image}")
        result = detect_image(image, allowed, captured_at, cv2_module=cv2)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 1

    print(result.to_json())
    return 0 if result.status == "DETECTED" else 2


if __name__ == "__main__":
    sys.exit(main())
