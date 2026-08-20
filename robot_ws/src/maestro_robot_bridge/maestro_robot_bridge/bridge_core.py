from __future__ import annotations

from .models import Command, Response


class BridgeCore:
    """
    Contract-level command dispatcher.

    This layer validates whether a command can enter the bridge lifecycle.
    Physical DOCK/UNDOCK execution is intentionally handled later.
    """

    def __init__(self, target_map: dict[str, dict] | None = None):
        self._target_map = target_map or {}

    def handle_command(self, command: Command) -> Response:
        if command.intent == "SPRAY":
            return self._handle_spray(command)

        if command.intent == "DOCK":
            return Response(
                schema_version="1.0",
                command_id=command.command_id,
                status="ACCEPTED",
                reason="dock command accepted",
            )

        if command.intent == "UNDOCK":
            return Response(
                schema_version="1.0",
                command_id=command.command_id,
                status="ACCEPTED",
                reason="undock command accepted",
            )

        return Response(
            schema_version="1.0",
            command_id=command.command_id,
            status="REJECTED",
            reason="unsupported intent",
        )

    def _handle_spray(self, command: Command) -> Response:
        if command.target is None:
            return Response(
                schema_version="1.0",
                command_id=command.command_id,
                status="REJECTED",
                reason="SPRAY requires target",
            )

        if command.target.id not in self._target_map:
            return Response(
                schema_version="1.0",
                command_id=command.command_id,
                status="REJECTED",
                reason="unknown target",
            )

        return Response(
            schema_version="1.0",
            command_id=command.command_id,
            status="ACCEPTED",
            reason=f"spray target {command.target.id} accepted",
        )