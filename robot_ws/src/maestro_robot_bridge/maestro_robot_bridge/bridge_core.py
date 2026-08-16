from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from threading import Lock

from .contract import ContractError, parse_command
from .models import PoseTarget, Response
from .target_map import TargetMap


Dispatch = Callable[[PoseTarget, str], tuple[bool, str]]


class BridgeCore:
    def __init__(self, target_map: TargetMap, dispatch: Dispatch):
        self._target_map = target_map
        self._dispatch = dispatch
        self._responses: dict[str, Response] = {}
        self._lock = Lock()

    def handle(self, raw: str | bytes, now: datetime | None = None) -> Response:
        try:
            command = parse_command(raw, now=now)
        except ContractError as exc:
            return Response("1.0", exc.command_id, "REJECTED", exc.reason)

        with self._lock:
            previous = self._responses.get(command.command_id)
            if previous is not None:
                return previous

            pose = self._target_map.get(command.target.id)
            if pose is None:
                response = Response("1.0", command.command_id, "REJECTED", "target is not mapped")
                self._responses[command.command_id] = response
                return response

            try:
                accepted, reason = self._dispatch(pose, command.command_id)
            except Exception:
                response = Response("1.0", command.command_id, "FAILED", "navigation dispatch failed")
            else:
                response = Response(
                    "1.0",
                    command.command_id,
                    "ACCEPTED" if accepted else "REJECTED",
                    reason,
                )
            self._responses[command.command_id] = response
            return response
