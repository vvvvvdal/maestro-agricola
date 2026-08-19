#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MATRIX = ROOT / "shared" / "evidence" / "qa04_checkpoints.json"
EXPECTED_CHECKPOINTS = {
    "AI",
    "GLASSES_INPUT",
    "AUDIO_OUTPUT",
    "PRIVACY",
    "EFFICIENCY",
}
ALLOWED_STATUSES = {"NOT_STARTED", "PARTIAL", "PASS", "FAIL", "BLOCKED"}


def validate_matrix(matrix: dict[str, Any], root: Path = ROOT) -> None:
    if matrix.get("schema_version") != "1.0":
        raise ValueError("schema_version deve ser 1.0")

    policy = matrix.get("status_policy")
    if not isinstance(policy, dict) or set(policy.get("allowed", [])) != ALLOWED_STATUSES:
        raise ValueError("status_policy.allowed não corresponde aos estados suportados")

    overall_status = matrix.get("overall_status")
    if overall_status not in ALLOWED_STATUSES:
        raise ValueError("overall_status inválido")

    checkpoints = matrix.get("checkpoints")
    if not isinstance(checkpoints, list) or len(checkpoints) != len(EXPECTED_CHECKPOINTS):
        raise ValueError("a matriz deve conter exatamente cinco checkpoints")

    ids = [checkpoint.get("id") for checkpoint in checkpoints if isinstance(checkpoint, dict)]
    if len(ids) != len(checkpoints) or set(ids) != EXPECTED_CHECKPOINTS or len(ids) != len(set(ids)):
        raise ValueError("IDs de checkpoint ausentes, duplicados ou inesperados")

    for checkpoint in checkpoints:
        validate_checkpoint(checkpoint, root)

    all_pass = all(checkpoint["status"] == "PASS" for checkpoint in checkpoints)
    if (overall_status == "PASS") != all_pass:
        raise ValueError("overall_status e estados dos checkpoints são inconsistentes")


def validate_checkpoint(checkpoint: dict[str, Any], root: Path) -> None:
    status = checkpoint.get("status")
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"{checkpoint.get('id')}: status inválido")
    if not checkpoint.get("owner"):
        raise ValueError(f"{checkpoint.get('id')}: owner ausente")
    if not checkpoint.get("acceptance_criteria"):
        raise ValueError(f"{checkpoint.get('id')}: critérios de aceite ausentes")
    if not isinstance(checkpoint.get("pending"), list):
        raise ValueError(f"{checkpoint.get('id')}: pending deve ser uma lista")
    if not isinstance(checkpoint.get("contains_raw_media"), bool):
        raise ValueError(f"{checkpoint.get('id')}: contains_raw_media deve ser booleano")
    if not checkpoint.get("pitch_claim"):
        raise ValueError(f"{checkpoint.get('id')}: pitch_claim ausente")

    evidence = checkpoint.get("evidence")
    if not isinstance(evidence, list):
        raise ValueError(f"{checkpoint.get('id')}: evidence deve ser uma lista")
    evidence_ids: set[str] = set()
    for item in evidence:
        evidence_id = item.get("id")
        if not evidence_id or evidence_id in evidence_ids:
            raise ValueError(f"{checkpoint.get('id')}: evidência sem ID ou duplicada")
        evidence_ids.add(evidence_id)
        if item.get("status") not in ALLOWED_STATUSES:
            raise ValueError(f"{checkpoint.get('id')}/{evidence_id}: status inválido")
        path_value = item.get("path")
        if not isinstance(path_value, str) or not path_value or Path(path_value).is_absolute():
            raise ValueError(f"{checkpoint.get('id')}/{evidence_id}: caminho deve ser relativo")
        if not (root / path_value).is_file():
            raise ValueError(f"{checkpoint.get('id')}/{evidence_id}: arquivo não encontrado: {path_value}")
        if not item.get("summary") or not item.get("type"):
            raise ValueError(f"{checkpoint.get('id')}/{evidence_id}: descrição incompleta")

    if status == "PASS" and (checkpoint["pending"] or not evidence):
        raise ValueError(f"{checkpoint.get('id')}: PASS não pode manter pendências e exige evidência")
    if status == "BLOCKED" and not checkpoint["pending"]:
        raise ValueError(f"{checkpoint.get('id')}: BLOCKED exige pendência explícita")


def load_matrix(path: Path = DEFAULT_MATRIX) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_MATRIX
    try:
        validate_matrix(load_matrix(path))
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"QA-04 inválida: {error}", file=sys.stderr)
        return 1
    print(f"QA-04 válida: 5 checkpoints, status {load_matrix(path)['overall_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
