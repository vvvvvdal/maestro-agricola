from __future__ import annotations

from collections.abc import Callable

from .models import Command, Response


class BridgeCore:
    """
    Contract-level command dispatcher.

    Execution is delegated to callbacks owned by the ROS node.
    """

    def __init__(
        self,
        target_map,
        navigation_callback: Callable,
        dock_callback: Callable | None = None,
        undock_callback: Callable | None = None,
    ):
        self._target_map = target_map
        self._navigation_callback = navigation_callback
        self._dock_callback = dock_callback
        self._undock_callback = undock_callback

    def handle(self, raw_message: str) -> Response:
        from .contract import ContractError, parse_command

        try:
            command = parse_command(raw_message)
            return self.handle_command(command)

        except ContractError as exc:
            return Response(
                schema_version="1.0",
                command_id=exc.command_id,
                status="REJECTED",
                reason=exc.reason,
            )

        except Exception as exc:
            return Response(
                schema_version="1.0",
                command_id="unknown",
                status="REJECTED",
                reason=str(exc),
            )

    def handle_command(self, command: Command) -> Response:
        if command.intent == "SPRAY":
            return self._handle_spray(command)

        if command.intent == "DOCK":
            return self._handle_dock(command)

        if command.intent == "UNDOCK":
            return self._handle_undock(command)

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

        pose = self._target_map.get(command.target.id)

        if pose is None:
            return Response(
                schema_version="1.0",
                command_id=command.command_id,
                status="REJECTED",
                reason="unknown target",
            )

        accepted, reason = self._navigation_callback(
            pose,
            command.command_id,
        )

        return Response(
            schema_version="1.0",
            command_id=command.command_id,
            status="ACCEPTED" if accepted else "REJECTED",
            reason=reason,
        )

    def _handle_dock(self, command: Command) -> Response:
        if self._dock_callback is None:
            return Response(
                schema_version="1.0",
                command_id=command.command_id,
                status="REJECTED",
                reason="dock unavailable",
            )

        accepted, reason = self._dock_callback()

        return Response(
            schema_version="1.0",
            command_id=command.command_id,
            status="ACCEPTED" if accepted else "REJECTED",
            reason=reason,
        )

    def _handle_undock(self, command: Command) -> Response:
        if self._undock_callback is None:
            return Response(
                schema_version="1.0",
                command_id=command.command_id,
                status="REJECTED",
                reason="undock unavailable",
            )

        accepted, reason = self._undock_callback()

        return Response(
            schema_version="1.0",
            command_id=command.command_id,
            status="ACCEPTED" if accepted else "REJECTED",
            reason=reason,
        )
