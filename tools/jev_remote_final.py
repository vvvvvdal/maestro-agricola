#!/usr/bin/env python3
"""Run the frozen final Jev evaluation exactly once outside the Android app."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path

from jev_remote_smoke import LABELS, MODEL, SmokeCase, post_json, run_evaluation, worst_case_cost_usd


ROOT = Path(__file__).resolve().parents[1]
FINAL_DATASET = ROOT / "docs/study-groups/jev-rl-2026-10-01/corpus/final.tsv"
FINAL_FIXTURE = ROOT / "docs/study-groups/jev-rl-2026-10-01/results/jev-final-fixture.json"
FINAL_RESERVATION = ROOT / "docs/study-groups/jev-rl-2026-10-01/results/jev-final-reservation.json"
FINAL_DATASET_SHA256 = "d0438948d9d239b2cafae8be044f7079935590b50ad9eff522ff570a6188b8b0"
FINAL_CASES = 60
MAX_FINAL_ATTEMPTS = FINAL_CASES * 2
FINAL_COST_CAP_USD = 3.00


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Executa uma unica rodada do corpus final Jev congelado.")
    parser.add_argument("--execute", action="store_true", help="autoriza a rodada remota unica")
    return parser.parse_args()


def load_final_cases(path: Path = FINAL_DATASET) -> list[SmokeCase]:
    if sha256(path) != FINAL_DATASET_SHA256:
        raise ValueError("final corpus hash does not match the frozen manifest")
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        if reader.fieldnames != ["id", "text", "gold_label", "category"]:
            raise ValueError("final TSV must have id, text, gold_label, category columns")
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
    if len(cases) != FINAL_CASES or len({case.case_id for case in cases}) != FINAL_CASES:
        raise ValueError("final corpus must contain exactly 60 unique cases")
    if any(not all(case.__dict__.values()) for case in cases):
        raise ValueError("final corpus contains an empty case field")
    if {case.gold_label for case in cases} != set(LABELS):
        raise ValueError("final corpus must cover exactly the six labels")
    return cases


def run_final(cases: list[SmokeCase], api_key: str, transport=post_json, sleep=None) -> dict:
    kwargs = {} if sleep is None else {"sleep": sleep}
    return run_evaluation(
        cases,
        api_key,
        transport,
        MAX_FINAL_ATTEMPTS,
        FINAL_COST_CAP_USD,
        **kwargs,
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ensure_final_fixture_absent(path: Path = FINAL_FIXTURE) -> None:
    if path.exists():
        raise FileExistsError(f"refusing a second final evaluation: {path} already exists")


def reserve_final_evaluation(path: Path = FINAL_RESERVATION) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise FileExistsError(f"refusing a second final evaluation: reservation {path} already exists") from error
    with os.fdopen(descriptor, "w", encoding="utf-8") as output:
        json.dump({
            "schema_version": "1.0",
            "dataset_sha256": FINAL_DATASET_SHA256,
            "model": MODEL,
        }, output, indent=2)
        output.write("\n")


def main() -> None:
    args = parse_args()
    cases = load_final_cases()
    if not args.execute:
        print(f"dry run: {len(cases)} frozen cases, at most {MAX_FINAL_ATTEMPTS} requests, upper cost ${worst_case_cost_usd(MAX_FINAL_ATTEMPTS):.6f}")
        return
    try:
        ensure_final_fixture_absent()
    except FileExistsError as error:
        raise SystemExit(str(error)) from error
    api_key = os.environ.get("TYPESAFE_API_KEY")
    if not api_key:
        raise SystemExit("TYPESAFE_API_KEY is required with --execute")
    reserve_final_evaluation()
    fixture = run_final(cases, api_key)
    FINAL_FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    FINAL_FIXTURE.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
    print(f"wrote sanitized final fixture for {len(cases)} cases to {FINAL_FIXTURE}")


if __name__ == "__main__":
    main()
