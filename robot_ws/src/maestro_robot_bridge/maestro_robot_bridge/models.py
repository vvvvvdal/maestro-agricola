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