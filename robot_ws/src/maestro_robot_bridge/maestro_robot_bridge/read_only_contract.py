from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import UUID

from .models import ReadOnlyQuery


SCHEMA_VERSION = "1.0"
LAST_SIMULATED_SPRAY_FOR_PLOT = "LAST_SIMULATED_SPRAY_FOR_PLOT"
ALLOWED_FIELDS = {
    "schema_version",
    "request_id",
    "requested_at",
    "kind",
    "plot_id",
}


class ReadOnlyContractError(ValueError):
    def __init__(self, reason: str, request_id: str = "unknown"):
        super().__init__(reason)
        self.reason = reason
        self.request_id = request_id


def parse_read_only_query(raw: str | bytes) -> ReadOnlyQuery:
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError, TypeError) as exc:
        raise ReadOnlyContractError("payload is not valid JSON") from exc

    if not isinstance(payload, dict):
        raise ReadOnlyContractError("payload must be a JSON object")

    request_id = str(payload.get("request_id", "unknown"))
    missing = ALLOWED_FIELDS - payload.keys()
    extra = payload.keys() - ALLOWED_FIELDS
    if missing:
        raise ReadOnlyContractError(
            f"missing fields: {', '.join(sorted(missing))}",
            request_id,
        )
    if extra:
        raise ReadOnlyContractError(
            f"unexpected fields: {', '.join(sorted(extra))}",
            request_id,
        )
    if payload["schema_version"] != SCHEMA_VERSION:
        raise ReadOnlyContractError("unsupported schema_version", request_id)

    try:
        UUID(request_id)
    except (ValueError, AttributeError) as exc:
        raise ReadOnlyContractError("request_id must be a UUID", request_id) from exc

    _parse_requested_at(payload["requested_at"], request_id)
    if payload["kind"] != LAST_SIMULATED_SPRAY_FOR_PLOT:
        raise ReadOnlyContractError("query kind is not allowed", request_id)
    if not isinstance(payload["plot_id"], str) or not payload["plot_id"]:
        raise ReadOnlyContractError("plot_id is invalid", request_id)

    return ReadOnlyQuery(
        schema_version=SCHEMA_VERSION,
        request_id=request_id,
        requested_at=payload["requested_at"],
        kind=payload["kind"],
        plot_id=payload["plot_id"],
    )


def _parse_requested_at(value: object, request_id: str) -> None:
    if not isinstance(value, str):
        raise ReadOnlyContractError("requested_at must be an ISO-8601 string", request_id)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ReadOnlyContractError("requested_at is invalid", request_id) from exc
    if parsed.tzinfo is None:
        raise ReadOnlyContractError(
            "requested_at must include a timezone",
            request_id,
        )
    parsed.astimezone(timezone.utc)
