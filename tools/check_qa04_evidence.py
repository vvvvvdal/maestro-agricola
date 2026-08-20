#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
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
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
CURRENT_MODEL = ROOT / "shared" / "ai" / "intent_model.json"
PARITY_FIXTURE = ROOT / "shared" / "ai" / "parity_cases.json"
DEVICE_EVALUATION = ROOT / "shared" / "ai" / "device_evaluation.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_matrix(matrix: dict[str, Any], root: Path = ROOT) -> None:
    if matrix.get("schema_version") != "1.1":
        raise ValueError("schema_version deve ser 1.1")

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

    validate_build_traceability(matrix, root)

    all_pass = all(checkpoint["status"] == "PASS" for checkpoint in checkpoints)
    if (overall_status == "PASS") != all_pass:
        raise ValueError("overall_status e estados dos checkpoints são inconsistentes")


def validate_build_traceability(matrix: dict[str, Any], root: Path) -> None:
    traceability = matrix.get("build_traceability")
    if not isinstance(traceability, dict):
        raise ValueError("build_traceability ausente ou inválida")

    hash_fields = (
        "device_benchmarked_model_sha256",
        "device_benchmarked_apk_sha256",
        "current_candidate_model_sha256",
        "current_candidate_apk_sha256",
    )
    for field in hash_fields:
        if not SHA256_PATTERN.fullmatch(str(traceability.get(field, ""))):
            raise ValueError(f"build_traceability.{field} deve ser um SHA-256")

    pending = traceability.get("final_build_benchmark_pending")
    if not isinstance(pending, bool):
        raise ValueError("build_traceability.final_build_benchmark_pending deve ser booleano")

    current_model = root / CURRENT_MODEL.relative_to(ROOT)
    parity_fixture = root / PARITY_FIXTURE.relative_to(ROOT)
    device_evaluation_path = root / DEVICE_EVALUATION.relative_to(ROOT)
    expected_current_model_hash = sha256_file(current_model)
    if traceability["current_candidate_model_sha256"] != expected_current_model_hash:
        raise ValueError("current_candidate_model_sha256 diverge do modelo canônico")

    parity = json.loads(parity_fixture.read_text(encoding="utf-8"))
    if parity.get("model_sha256") != expected_current_model_hash:
        raise ValueError("fixture de paridade diverge do modelo canônico")

    device_evaluation = json.loads(device_evaluation_path.read_text(encoding="utf-8"))
    if traceability["device_benchmarked_model_sha256"] != device_evaluation.get("model_sha256"):
        raise ValueError("device_benchmarked_model_sha256 diverge da avaliação física")
    if traceability["device_benchmarked_apk_sha256"] != device_evaluation.get("apk_sha256"):
        raise ValueError("device_benchmarked_apk_sha256 diverge da avaliação física")

    artifacts_diverge = (
        traceability["device_benchmarked_model_sha256"]
        != traceability["current_candidate_model_sha256"]
        or traceability["device_benchmarked_apk_sha256"]
        != traceability["current_candidate_apk_sha256"]
    )
    if artifacts_diverge and not pending:
        raise ValueError("benchmark final não pode estar concluído com artefatos divergentes")

    ai_checkpoint = next(checkpoint for checkpoint in matrix["checkpoints"] if checkpoint["id"] == "AI")
    if pending and ai_checkpoint["status"] == "PASS":
        raise ValueError("AI não pode estar PASS enquanto o benchmark final estiver pendente")


def validate_candidate_apk(matrix: dict[str, Any], apk_path: Path) -> None:
    if not apk_path.is_file():
        raise ValueError(f"APK candidato não encontrado: {apk_path}")
    expected = matrix["build_traceability"]["current_candidate_apk_sha256"]
    if sha256_file(apk_path) != expected:
        raise ValueError("current_candidate_apk_sha256 diverge do APK informado")


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Valida a matriz de evidências da QA-04.")
    parser.add_argument("matrix", nargs="?", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--apk", type=Path, help="confere explicitamente o APK candidato montado")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = args.matrix.resolve()
    try:
        matrix = load_matrix(path)
        validate_matrix(matrix)
        if args.apk is not None:
            validate_candidate_apk(matrix, args.apk.resolve())
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"QA-04 inválida: {error}", file=sys.stderr)
        return 1
    apk_suffix = ", APK candidato conferido" if args.apk is not None else ""
    print(f"QA-04 válida: 5 checkpoints, status {matrix['overall_status']}{apk_suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
