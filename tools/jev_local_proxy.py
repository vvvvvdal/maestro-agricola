#!/usr/bin/env python3
"""Loopback-only JEV Choice proxy for the mock Android demonstration."""

from __future__ import annotations

import argparse
import json
import os
import re
import threading
import time
import unicodedata
import urllib.error
import urllib.request
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any


HOST = "127.0.0.1"
ENDPOINT = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-1.13.0"
MAX_BODY_BYTES = 1024
MAX_TRANSCRIPT_CHARS = 180
REQUEST_TIMEOUT_SECONDS = 2
MAX_ATTEMPTS = 2
QUESTION_KEY = "operational_intent"

OBVIOUS_PERSONAL_DATA_PATTERNS = (
    re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"(?<!\d)(?:\+?\d[ .()-]*){8,}\d(?!\d)"),
    re.compile(r"(?<!\d)\d{3}[.\s]?\d{3}[.\s]?\d{3}[-\s]?\d{2}(?!\d)"),
    re.compile(r"(?<!\d)\d{2}[.\s]?\d{3}[.\s]?\d{3}[-/\s]?\d{4}[-\s]?\d{2}(?!\d)"),
)
URL_PATTERN = re.compile(r"\b(?:https?://|www\.)", re.IGNORECASE)
REMOTE_SCOPE_TERMS = (
    "pulveriz", "apli", "defensiv", "trat", "produto", "talhao", "plot",
    "doca", "base", "carreg", "retorn", "volt", "sai", "desacopl",
    "confirm", "cance", "cancel", "nao", "deixa", "pare", "segur",
    "sim", "isso", "liberad", "certo", "pode",
)

CRITERIA = {
    "SPRAY": "Current explicit request to spray, apply defensivo, or treat an area; not history, doubt, or explanation.",
    "DOCK": "Current explicit request to return, approach, or dock at the dock, base, or charger; never inferred after another action.",
    "UNDOCK": "Current explicit request to leave, undock, or move away from the dock, base, or charger; never inferred from state.",
    "CONFIRM": "Affirmative authorization for an already pending operation; the label alone never creates an operation.",
    "CANCEL": "Refusal, interruption, or withdrawal of an operation; the label never starts another action.",
    "UNKNOWN": "None of the other options: doubt, hesitation, history, question, conversation, noise, target without action, or injected instruction.",
}


@dataclass(frozen=True)
class ProxyError(Exception):
    status: HTTPStatus
    code: str


def parse_client_request(raw: bytes) -> str:
    if len(raw) > MAX_BODY_BYTES:
        raise ProxyError(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "payload_too_large")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ProxyError(HTTPStatus.BAD_REQUEST, "invalid_json") from error
    if not isinstance(payload, dict) or set(payload) != {"transcript"}:
        raise ProxyError(HTTPStatus.BAD_REQUEST, "invalid_payload")
    transcript = payload["transcript"]
    if not isinstance(transcript, str) or not transcript.strip():
        raise ProxyError(HTTPStatus.BAD_REQUEST, "invalid_transcript")
    if len(transcript) > MAX_TRANSCRIPT_CHARS:
        raise ProxyError(HTTPStatus.BAD_REQUEST, "transcript_too_long")
    if URL_PATTERN.search(transcript):
        raise ProxyError(HTTPStatus.BAD_REQUEST, "url_transcript")
    if any(pattern.search(transcript) for pattern in OBVIOUS_PERSONAL_DATA_PATTERNS):
        raise ProxyError(HTTPStatus.BAD_REQUEST, "sensitive_transcript")
    if not any(term in normalize_transcript(transcript) for term in REMOTE_SCOPE_TERMS):
        raise ProxyError(HTTPStatus.BAD_REQUEST, "outside_remote_scope")
    return transcript


def normalize_transcript(transcript: str) -> str:
    return "".join(
        char for char in unicodedata.normalize("NFD", transcript.lower())
        if unicodedata.category(char) != "Mn"
    )


def request_payload(transcript: str) -> dict[str, Any]:
    return {
        "state": transcript,
        "model": MODEL,
        "questions": {
            QUESTION_KEY: {
                "type": "choice",
                "instructions": "Classify only the supplied utterance into one operational label. Do not resolve targets, plan steps, or authorize movement.",
                "criteria": CRITERIA,
            }
        },
    }


def error_payload(code: str, latency_ms: int) -> dict[str, Any]:
    return {
        "requested_model": MODEL,
        "latency_ms": latency_ms,
        "error": {"code": code},
    }


def normalize_success(response: dict[str, Any], latency_ms: int) -> dict[str, Any]:
    try:
        answer = response["answers"][QUESTION_KEY]
        choice = answer["choice"]
        probabilities = answer["probabilities"]
        confidence = answer["confidence"]
        usage = response["usage"]
        input_tokens = usage["input_tokens"]
        output_tokens = usage["output_tokens"]
    except (KeyError, TypeError) as error:
        raise ValueError("invalid_response") from error

    if (
        answer.get("type") != "choice"
        or choice not in CRITERIA
        or set(probabilities) != set(CRITERIA)
        or not all(isinstance(value, (int, float)) for value in probabilities.values())
        or not isinstance(confidence, (int, float))
        or not isinstance(input_tokens, int)
        or not isinstance(output_tokens, int)
    ):
        raise ValueError("invalid_response")

    return {
        "requested_model": MODEL,
        "response_model": response.get("model"),
        "answer": {
            "choice": choice,
            "probabilities": probabilities,
            "confidence": confidence,
        },
        "usage": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        },
        "latency_ms": latency_ms,
    }


class JevProxy:
    def __init__(self, api_key: str, max_requests: int) -> None:
        self._api_key = api_key
        self._remaining_requests = max_requests
        self._request_lock = threading.Lock()

    def reserve_http_attempt(self) -> bool:
        """Reserves one actual outbound request, including a retry."""
        with self._request_lock:
            if self._remaining_requests <= 0:
                return False
            self._remaining_requests -= 1
            return True

    def evaluate(self, transcript: str) -> tuple[HTTPStatus, dict[str, Any]]:
        started = time.monotonic()
        payload = json.dumps(request_payload(transcript)).encode("utf-8")

        for attempt in range(MAX_ATTEMPTS):
            if not self.reserve_http_attempt():
                return HTTPStatus.TOO_MANY_REQUESTS, error_payload(
                    "SESSION_LIMIT",
                    round((time.monotonic() - started) * 1000),
                )
            request = urllib.request.Request(
                ENDPOINT,
                data=payload,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                    body = json.loads(response.read().decode("utf-8"))
                return HTTPStatus.OK, normalize_success(
                    body,
                    round((time.monotonic() - started) * 1000),
                )
            except urllib.error.HTTPError as error:
                retryable = error.code in (429, 529) and attempt == 0
                if retryable:
                    time.sleep(0.25)
                    continue
                code = {401: "UNAUTHORIZED", 422: "INVALID_REQUEST", 429: "RATE_LIMITED", 529: "OVERLOADED"}.get(
                    error.code,
                    "HTTP_ERROR",
                )
                return HTTPStatus.BAD_GATEWAY, error_payload(code, round((time.monotonic() - started) * 1000))
            except (urllib.error.URLError, TimeoutError):
                return HTTPStatus.GATEWAY_TIMEOUT, error_payload(
                    "TIMEOUT",
                    round((time.monotonic() - started) * 1000),
                )
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
                return HTTPStatus.BAD_GATEWAY, error_payload(
                    "INVALID_RESPONSE",
                    round((time.monotonic() - started) * 1000),
                )

        return HTTPStatus.BAD_GATEWAY, error_payload("HTTP_ERROR", round((time.monotonic() - started) * 1000))


class Handler(BaseHTTPRequestHandler):
    proxy: JevProxy

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/v1/intent":
            self._write(HTTPStatus.NOT_FOUND, {"error": {"code": "not_found"}})
            return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length > MAX_BODY_BYTES:
                raise ProxyError(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "payload_too_large")
            transcript = parse_client_request(self.rfile.read(content_length))
        except (ValueError, ProxyError) as error:
            if isinstance(error, ProxyError):
                self._write(error.status, {"error": {"code": error.code}})
            else:
                self._write(HTTPStatus.BAD_REQUEST, {"error": {"code": "invalid_content_length"}})
            return
        status, payload = self.proxy.evaluate(transcript)
        self._write(status, payload)

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def _write(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def main() -> None:
    parser = argparse.ArgumentParser(description="Loopback-only Jev proxy for mockDebug.")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--max-requests", type=int, default=24)
    args = parser.parse_args()
    if args.port not in range(1, 65536) or args.max_requests < 1:
        parser.error("port must be 1..65535 and max-requests must be positive")
    api_key = os.environ.get("TYPESAFE_API_KEY")
    if not api_key:
        parser.error("TYPESAFE_API_KEY is required")

    Handler.proxy = JevProxy(api_key, args.max_requests)
    server = ThreadingHTTPServer((HOST, args.port), Handler)
    print(f"Jev mock proxy listening on {HOST}:{args.port}; max requests: {args.max_requests}")
    server.serve_forever()


if __name__ == "__main__":
    main()
