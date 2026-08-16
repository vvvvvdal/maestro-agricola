from __future__ import annotations

import json
from pathlib import Path

from .models import PoseTarget


class TargetMap:
    def __init__(self, targets: dict[str, PoseTarget]):
        if not targets:
            raise ValueError("target map cannot be empty")
        self._targets = dict(targets)

    @classmethod
    def load(cls, path: str | Path) -> "TargetMap":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if payload.get("schema_version") != "1.0" or not isinstance(payload.get("targets"), dict):
            raise ValueError("invalid target map")
        targets = {}
        for target_id, value in payload["targets"].items():
            targets[target_id] = PoseTarget(
                id=target_id,
                x=float(value["x"]),
                y=float(value["y"]),
                yaw=float(value.get("yaw", 0.0)),
            )
        return cls(targets)

    def get(self, target_id: str) -> PoseTarget | None:
        return self._targets.get(target_id)
