from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from uuid import UUID

from .models import Command, Target


SCHEMA_VERSION = "1.0"
ALLOWED_FIELDS = {
    "schema_version",
    "command_id",
    "created_at",
    "expires_in_ms",
    "intent",
    "target",
    "confirmed",
}


class ContractError(ValueError):
    def __init__(self, reason: str, command_id: str = "unknown"):
        super().__init__(reason)
        self.reason = reason
        self.command_id = command_id


def parse_datetime(value: object) -> datetime:
    if not isinstance(value, str):
        raise ContractError("created_at must be an ISO-8601 string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContractError("created_at is invalid") from exc
    if parsed.tzinfo is None:
        raise ContractError("created_at must include a timezone")
    return parsed.astimezone(timezone.utc)


def parse_command(raw: str | bytes, now: datetime | None = None) -> Command:
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError, TypeError) as exc:
        raise ContractError("payload is not valid JSON") from exc
    if not isinstance(payload, dict):
        raise ContractError("payload must be a JSON object")

    command_id = str(payload.get("command_id", "unknown"))
    missing = ALLOWED_FIELDS - payload.keys()
    extra = payload.keys() - ALLOWED_FIELDS
    if missing:
        raise ContractError(f"missing fields: {', '.join(sorted(missing))}", command_id)
    if extra:
        raise ContractError(f"unexpected fields: {', '.join(sorted(extra))}", command_id)
    if payload["schema_version"] != SCHEMA_VERSION:
        raise ContractError("unsupported schema_version", command_id)
    try:
        UUID(command_id)
    except (ValueError, AttributeError) as exc:
        raise ContractError("command_id must be a UUID", command_id) from exc
    if type(payload["expires_in_ms"]) is not int or not 1 <= payload["expires_in_ms"] <= 30000:
        raise ContractError("expires_in_ms must be between 1 and 30000", command_id)
    if payload["intent"] != "SPRAY":
        raise ContractError("intent is not allowed", command_id)
    if payload["confirmed"] is not True:
        raise ContractError("explicit confirmation is required", command_id)

    target_payload = payload["target"]
    if not isinstance(target_payload, dict) or set(target_payload) != {"type", "id"}:
        raise ContractError("target must contain only type and id", command_id)
    if target_payload["type"] != "MAPPED_PLOT":
        raise ContractError("target type is not allowed", command_id)
    target_id = target_payload["id"]
    if not isinstance(target_id, str) or not target_id or len(target_id) > 64:
        raise ContractError("target id is invalid", command_id)

    created_at = parse_datetime(payload["created_at"])
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if created_at > current + timedelta(seconds=5):
        raise ContractError("command timestamp is in the future", command_id)
    expires_at = created_at + timedelta(milliseconds=payload["expires_in_ms"])
    if current > expires_at:
        raise ContractError("command expired", command_id)

    return Command(
        schema_version=SCHEMA_VERSION,
        command_id=command_id,
        created_at=payload["created_at"],
        expires_in_ms=payload["expires_in_ms"],
        intent=payload["intent"],
        target=Target(type=target_payload["type"], id=target_id),
        confirmed=True,
    )
