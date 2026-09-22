#!/usr/bin/env python3
"""Run the independent frozen recovery evaluation exactly once."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from collections import Counter
from pathlib import Path

from jev_remote_smoke import LABELS, MODEL, SmokeCase, post_json, run_evaluation, worst_case_cost_usd


ROOT = Path(__file__).resolve().parents[1]
RECOVERY_DATASET = ROOT / "docs/study-groups/jev-rl-2026-10-01/corpus/final-recovery.tsv"
RECOVERY_FIXTURE = ROOT / "docs/study-groups/jev-rl-2026-10-01/results/jev-final-recovery-fixture.json"
RECOVERY_RESERVATION = ROOT / "docs/study-groups/jev-rl-2026-10-01/results/jev-final-recovery-reservation.json"
RECOVERY_DATASET_SHA256 = "a157963bd5c63623f1263d1772f72b76fd70e7ebaf333ee5be2ffedc8e7e6d2a"
RECOVERY_CASES = 60
MAX_RECOVERY_ATTEMPTS = RECOVERY_CASES * 2
RECOVERY_COST_CAP_USD = 1.50


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Executa uma unica rodada do corpus final Jev de recuperacao.")
    parser.add_argument("--execute", action="store_true", help="autoriza a rodada remota unica")
    return parser.parse_args()


def load_recovery_cases(path: Path = RECOVERY_DATASET) -> list[SmokeCase]:
    if sha256(path) != RECOVERY_DATASET_SHA256:
        raise ValueError("recovery corpus hash does not match the frozen manifest")
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        if reader.fieldnames != ["id", "text", "gold_label", "category"]:
            raise ValueError("recovery TSV must have id, text, gold_label, category columns")
        cases = [
            SmokeCase(
                case_id=row["id"].strip(),
                text=row["text"].strip(),
                gold_label=row["gold_label"].strip(),
                category=row["category"].strip(),
            )
            for row in reader
            if any(row.values())
        ]
    if len(cases) != RECOVERY_CASES or len({case.case_id for case in cases}) != RECOVERY_CASES:
        raise ValueError("recovery corpus must contain exactly 60 unique cases")
    if any(not all(case.__dict__.values()) for case in cases):
        raise ValueError("recovery corpus contains an empty case field")
    if Counter(case.gold_label for case in cases) != Counter({label: 10 for label in LABELS}):
        raise ValueError("recovery corpus must contain ten cases for every label")
    return cases


def run_recovery_final(cases: list[SmokeCase], api_key: str, transport=post_json, sleep=None) -> dict:
    kwargs = {} if sleep is None else {"sleep": sleep}
    return run_evaluation(
        cases,
        api_key,
        transport,
        MAX_RECOVERY_ATTEMPTS,
        RECOVERY_COST_CAP_USD,
        **kwargs,
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ensure_recovery_fixture_absent(path: Path = RECOVERY_FIXTURE) -> None:
    if path.exists():
        raise FileExistsError(f"refusing a second recovery evaluation: {path} already exists")


def reserve_recovery_evaluation(path: Path = RECOVERY_RESERVATION) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise FileExistsError(f"refusing a second recovery evaluation: reservation {path} already exists") from error
    with os.fdopen(descriptor, "w", encoding="utf-8") as output:
        json.dump({
            "schema_version": "1.0",
            "dataset_sha256": RECOVERY_DATASET_SHA256,
            "model": MODEL,
        }, output, indent=2)
        output.write("\n")


def main() -> None:
    args = parse_args()
    cases = load_recovery_cases()
    if not args.execute:
        print(f"dry run: {len(cases)} frozen recovery cases, at most {MAX_RECOVERY_ATTEMPTS} requests, upper cost ${worst_case_cost_usd(MAX_RECOVERY_ATTEMPTS):.6f}")
        return
    try:
        ensure_recovery_fixture_absent()
    except FileExistsError as error:
        raise SystemExit(str(error)) from error
    api_key = os.environ.get("TYPESAFE_API_KEY")
    if not api_key:
        raise SystemExit("TYPESAFE_API_KEY is required with --execute")
    reserve_recovery_evaluation()
    fixture = run_recovery_final(cases, api_key)
    RECOVERY_FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    RECOVERY_FIXTURE.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
    print(f"wrote sanitized recovery fixture for {len(cases)} cases to {RECOVERY_FIXTURE}")


if __name__ == "__main__":
    main()
