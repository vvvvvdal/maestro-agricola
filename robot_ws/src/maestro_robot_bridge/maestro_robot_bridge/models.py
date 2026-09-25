from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Target:
    type: str
    id: str


@dataclass(frozen=True)
class Command:
    schema_version: str
    command_id: str
    created_at: str
    expires_in_ms: int
    intent: str
    target: Target | None
    confirmed: bool


@dataclass(frozen=True)
class OperationRecord:
    schema_version: str
    operation_id: str
    kind: str
    plot_id: str
    completed_at: str
    origin: str


@dataclass(frozen=True)
class ReadOnlyQuery:
    schema_version: str
    request_id: str
    requested_at: str
    kind: str
    plot_id: str


@dataclass(frozen=True)
class ReadOnlyOperationSummary:
    plot_id: str
    completed_at: str
    origin: str


@dataclass(frozen=True)
class ReadOnlyResponse:
    schema_version: str
    request_id: str
    kind: str
    status: str
    record: ReadOnlyOperationSummary | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class PoseTarget:
    id: str
    x: float
    y: float
    yaw: float


@dataclass(frozen=True)
class Response:
    schema_version: str
    command_id: str
    status: str
    reason: str

    def to_dict(self) -> dict:
        return asdict(self)
