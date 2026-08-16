from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable
from uuid import uuid4

from websockets.exceptions import InvalidHandshake
from websockets.sync.client import ClientConnection, connect

from intent_model import IntentModel


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simula a jornada dos óculos no terminal.")
    parser.add_argument("--endpoint", default="ws://127.0.0.1:18765")
    parser.add_argument("--target", default="plot-03")
    parser.add_argument("--command", default="pulverizar esta área")
    parser.add_argument("--confirmation", default="confirmar")
    parser.add_argument(
        "--wait-seconds",
        type=float,
        default=10,
        help="tempo máximo para aguardar o bridge WebSocket iniciar",
    )
    return parser.parse_args()


def build_command(model: IntentModel, target: str, command_text: str, confirmation: str) -> dict:
    intent = model.predict_with_threshold(command_text, 0.40)
    decision = model.predict_with_threshold(confirmation, 0.40)
    if intent.label != "SPRAY":
        raise ValueError(f"intenção recusada: {intent.label} ({intent.confidence:.1%})")
    if decision.label != "CONFIRM":
        raise ValueError(f"confirmação recusada: {decision.label} ({decision.confidence:.1%})")
    return {
        "schema_version": "1.0",
        "command_id": str(uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "expires_in_ms": 5000,
        "intent": "SPRAY",
        "target": {"type": "MAPPED_PLOT", "id": target},
        "confirmed": True,
    }


def connect_to_bridge(
    endpoint: str,
    wait_seconds: float,
    connector: Callable[..., ClientConnection] = connect,
) -> ClientConnection:
    """Connect directly to the local/LAN bridge, retrying during simulator startup."""
    deadline = time.monotonic() + max(0, wait_seconds)
    last_error: Exception | None = None

    while True:
        try:
            # This is a local/LAN protocol. Bypassing system HTTP proxies also
            # prevents their HTTP/1.0 responses from being mistaken for a bridge.
            return connector(
                endpoint,
                open_timeout=3,
                close_timeout=2,
                proxy=None,
            )
        except (OSError, TimeoutError, InvalidHandshake) as error:
            last_error = error
            if time.monotonic() >= deadline:
                break
            print(f"Aguardando o bridge em {endpoint}...", file=sys.stderr)
            time.sleep(min(2, max(0, deadline - time.monotonic())))

    detail = str(last_error) if last_error else "erro desconhecido"
    raise ConnectionError(
        f"não foi possível conectar ao bridge em {endpoint}: {detail}. "
        "Inicie-o com `make simulation-up` ou execute a jornada completa com `make demo`."
    ) from last_error


def main() -> None:

    args = parse_args()
    model = IntentModel(json.loads((ROOT / "shared/ai/intent_model.json").read_text()))
    try:
        with connect_to_bridge(args.endpoint, args.wait_seconds) as socket:
            # Build the expiring payload only after the potentially long startup wait.
            command = build_command(model, args.target, args.command, args.confirmation)
            socket.send(json.dumps(command, ensure_ascii=False))
            response = json.loads(socket.recv(timeout=6))
    except (ConnectionError, TimeoutError) as error:
        raise SystemExit(f"Erro: {error}") from None

    if response.get("status") != "ACCEPTED":
        reason = response.get("reason", "motivo não informado")
        raise SystemExit(f"Erro: bridge recusou o comando: {reason}")
    print(json.dumps(response, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
