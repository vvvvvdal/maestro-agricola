#!/usr/bin/env python3
"""Run the bounded, synthetic Jev smoke experiment outside the Android app."""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import socket
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping


ROOT = Path(__file__).resolve().parents[1]
SMOKE_DATASET = ROOT / "docs/study-groups/jev-rl-2026-10-01/corpus/smoke.tsv"
MODEL = "jev-1.13.0"
ENDPOINT = "https://api.typesafe.ai/v1/systemone"
LABELS = ("SPRAY", "DOCK", "UNDOCK", "CONFIRM", "CANCEL", "UNKNOWN")
MAX_TOTAL_ATTEMPTS = 8
REQUEST_TIMEOUT_SECONDS = 2.0
MAX_RETRY_AFTER_SECONDS = 1.0
DEFAULT_RETRY_SECONDS = 0.25
INPUT_COST_PER_MILLION_USD = 0.042
SMOKE_COST_CAP_USD = 0.50
MODEL_CONTEXT_LIMIT_TOKENS = 64_000

CRITERIA = {
    "SPRAY": "Pedido atual e explicito para pulverizar, aplicar defensivo ou tratar uma area; nao e historico, duvida ou explicacao.",
    "DOCK": "Pedido atual e explicito para retornar, aproximar ou acoplar na doca, base ou carregador; nunca e implicito apos outra acao.",
    "UNDOCK": "Pedido atual e explicito para sair, desacoplar ou afastar da doca, base ou carregador; nunca e implicito pelo estado.",
    "CONFIRM": "Autorizacao afirmativa para uma operacao que ja esta pendente; o rotulo sozinho nao cria operacao.",
    "CANCEL": "Recusa, interrupcao ou desistencia de uma operacao; o rotulo nunca inicia outra acao.",
    "UNKNOWN": "Nenhuma das outras opcoes: duvida, hesitacao, historico, pergunta, conversa, ruido, alvo sem acao ou instrucao injetada.",
}


@dataclass(frozen=True)
class SmokeCase:
    case_id: str
    text: str
    gold_label: str
    category: str


@dataclass(frozen=True)
class HttpResponse:
    status: int
    headers: Mapping[str, str]
    body: bytes


class TransportError(Exception):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


Transport = Callable[[bytes, str], HttpResponse]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Executa o smoke remoto Jev com corpus fixo e sintetico.")
    parser.add_argument("--execute", action="store_true", help="autoriza as chamadas remotas")
    parser.add_argument("--output", type=Path, help="fixture sanitizada de saida")
    args = parser.parse_args()
    if args.execute and args.output is None:
        parser.error("--output is required with --execute")
    return args


def load_smoke_cases(path: Path = SMOKE_DATASET) -> list[SmokeCase]:
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        if reader.fieldnames != ["id", "text", "gold_label", "category"]:
            raise ValueError("smoke TSV must have id, text, gold_label, category columns")
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

    if len(cases) != len(LABELS):
        raise ValueError("smoke corpus must contain exactly six cases")
    if {case.gold_label for case in cases} != set(LABELS):
        raise ValueError("smoke corpus must contain one case for every label")
    if len({case.case_id for case in cases}) != len(cases) or any(
        not all(case.__dict__.values()) for case in cases
    ):
        raise ValueError("smoke corpus contains an empty or duplicate case")
    return cases


def request_body(text: str) -> bytes:
    payload = {
        "state": text,
        "model": MODEL,
        "questions": {
            "operational_intent": {
                "type": "choice",
                "instructions": "Classifique somente a fala fornecida em um dos seis rotulos operacionais. Nao resolva alvo, nao planeje etapas e nao autorize movimento.",
                "criteria": CRITERIA,
            }
        },
    }
    return json.dumps(payload, separators=(",", ":")).encode("utf-8")


def post_json(body: bytes, api_key: str) -> HttpResponse:
    request = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return HttpResponse(response.status, dict(response.headers.items()), response.read())
    except urllib.error.HTTPError as error:
        return HttpResponse(error.code, dict(error.headers.items()) if error.headers else {}, b"")
    except socket.timeout as error:
        raise TransportError("TIMEOUT") from error
    except urllib.error.URLError as error:
        if isinstance(error.reason, TimeoutError):
            raise TransportError("TIMEOUT") from error
        raise TransportError("TRANSPORT") from error
    except OSError as error:
        raise TransportError("TRANSPORT") from error


def is_probability(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and 0.0 <= value <= 1.0


def safe_model(value: Any) -> str | None:
    if isinstance(value, str) and value and value.replace("-", "").replace("_", "").replace(".", "").isalnum():
        return value
    return None


def safe_usage(value: Any) -> dict[str, int] | None:
    if not isinstance(value, dict):
        return None
    input_tokens = value.get("input_tokens")
    output_tokens = value.get("output_tokens")
    if not all(isinstance(token, int) and not isinstance(token, bool) and token >= 0 for token in (input_tokens, output_tokens)):
        return None
    return {"input_tokens": input_tokens, "output_tokens": output_tokens}


def safe_answer(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    choice = value.get("choice")
    probabilities = value.get("probabilities")
    confidence = value.get("confidence")
    if value.get("type") != "choice" or not isinstance(choice, str) or choice not in LABELS or not isinstance(probabilities, dict) or set(probabilities) != set(LABELS):
        return None
    if not is_probability(confidence) or not all(is_probability(probabilities[label]) for label in LABELS):
        return None
    if abs(sum(probabilities.values()) - 1.0) > 0.001:
        return None
    if any(probabilities[label] > probabilities[choice] + 0.001 for label in LABELS):
        return None
    return {
        "choice": choice,
        "probabilities": {label: probabilities[label] for label in LABELS},
        "confidence": confidence,
    }


def result_from_success(payload: Any, latency_ms: float) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return failed_result("INVALID_RESPONSE", latency_ms)
    answers = payload.get("answers")
    answer = safe_answer(answers.get("operational_intent") if isinstance(answers, dict) else None)
    usage = safe_usage(payload.get("usage"))
    response_model = safe_model(payload.get("model"))
    if answer is None or usage is None or response_model is None:
        return failed_result("INVALID_RESPONSE", latency_ms)
    return {
        "response_model": response_model,
        "answer": answer,
        "usage": usage,
        "latency_ms": latency_ms,
        "cost_usd": usage["input_tokens"] * INPUT_COST_PER_MILLION_USD / 1_000_000,
    }


def failed_result(code: str, latency_ms: float | None) -> dict[str, Any]:
    return {
        "response_model": None,
        "answer": None,
        "usage": None,
        "latency_ms": latency_ms,
        "cost_usd": None,
        "error": {"code": code},
    }


def error_code(status: int) -> str:
    return {
        401: "UNAUTHORIZED",
        422: "INVALID_REQUEST",
        429: "RATE_LIMITED",
        529: "OVERLOADED",
    }.get(status, "HTTP_ERROR")


def retry_delay(headers: Mapping[str, str]) -> float | None:
    value = next((value for name, value in headers.items() if name.lower() == "retry-after"), None)
    if value is None:
        return DEFAULT_RETRY_SECONDS
    try:
        seconds = float(value)
    except ValueError:
        return None
    return seconds if 0.0 <= seconds <= MAX_RETRY_AFTER_SECONDS else None


def run_smoke(cases: list[SmokeCase], api_key: str, transport: Transport, sleep: Callable[[float], None] = time.sleep) -> dict[str, Any]:
    if worst_case_cost_usd() > SMOKE_COST_CAP_USD:
        raise RuntimeError("documented model limit exceeds smoke cost cap")

    attempts = 0
    results: dict[str, dict[str, Any]] = {}
    for case in cases:
        if attempts >= MAX_TOTAL_ATTEMPTS:
            results[case.case_id] = failed_result("ATTEMPT_LIMIT", None)
            continue

        started_at = time.perf_counter_ns()
        can_retry = True
        while True:
            attempts += 1
            try:
                response = transport(request_body(case.text), api_key)
            except TransportError as error:
                results[case.case_id] = failed_result(error.code, elapsed_ms(started_at))
                break
            except TimeoutError:
                results[case.case_id] = failed_result("TIMEOUT", elapsed_ms(started_at))
                break

            if response.status == 200:
                try:
                    payload = json.loads(response.body.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    results[case.case_id] = failed_result("INVALID_RESPONSE", elapsed_ms(started_at))
                else:
                    results[case.case_id] = result_from_success(payload, elapsed_ms(started_at))
                break

            code = error_code(response.status)
            delay = retry_delay(response.headers) if response.status in (429, 529) else None
            if can_retry and delay is not None and attempts < MAX_TOTAL_ATTEMPTS:
                can_retry = False
                sleep(delay)
                continue
            results[case.case_id] = failed_result(code, elapsed_ms(started_at))
            break

    return {"schema_version": "1.0", "model": MODEL, "results": results}


def elapsed_ms(started_at: int) -> float:
    return (time.perf_counter_ns() - started_at) / 1_000_000


def worst_case_cost_usd() -> float:
    return MAX_TOTAL_ATTEMPTS * MODEL_CONTEXT_LIMIT_TOKENS * INPUT_COST_PER_MILLION_USD / 1_000_000


def main() -> None:
    args = parse_args()
    cases = load_smoke_cases()
    if not args.execute:
        print(f"dry run: {len(cases)} synthetic cases, at most {MAX_TOTAL_ATTEMPTS} requests, upper cost ${worst_case_cost_usd():.6f}")
        return

    api_key = os.environ.get("TYPESAFE_API_KEY")
    if not api_key:
        raise SystemExit("TYPESAFE_API_KEY is required with --execute")
    fixture = run_smoke(cases, api_key, post_json)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
    print(f"wrote sanitized fixture for {len(cases)} cases to {args.output}")


if __name__ == "__main__":
    main()
