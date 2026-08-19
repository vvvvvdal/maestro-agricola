from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MissionPhase(str, Enum):
    NEEDS_UNDOCK = "NEEDS_UNDOCK"
    UNDOCKING = "UNDOCKING"
    READY = "READY"
    NAVIGATING = "NAVIGATING"
    READY_TO_DOCK = "READY_TO_DOCK"
    RETURNING_TO_DOCK = "RETURNING_TO_DOCK"
    READY_FOR_DOCK = "READY_FOR_DOCK"
    DOCKING = "DOCKING"
    DOCKED = "DOCKED"
    FAILED = "FAILED"


@dataclass
class MissionCycle:
    """
    Fail-closed mission lifecycle.

    Normal navigation missions start in READY and return to READY when Nav2
    finishes. Docking and undocking states are preserved as infrastructure for
    explicit DOCK/UNDOCK commands, but they are not entered automatically by a
    normal navigation command.
    """

    phase: MissionPhase = MissionPhase.READY
    failure_reason: str | None = None

    def command_queued(self) -> bool:
        """
        Accept a navigation command only while the robot is available for
        navigation or while another navigation command is already running.

        Queuing a command must never implicitly change docking state.
        """
        return self.phase in (
            MissionPhase.READY,
            MissionPhase.NAVIGATING,
        )

    def begin_undock(self) -> bool:
        """
        Begin an undock operation only when the lifecycle was explicitly placed
        in NEEDS_UNDOCK.
        """
        if self.phase != MissionPhase.NEEDS_UNDOCK:
            return False

        self.phase = MissionPhase.UNDOCKING
        return True

    def undock_completed(self, *, succeeded: bool, is_docked: bool) -> bool:
        if self.phase != MissionPhase.UNDOCKING:
            return False

        if not succeeded or is_docked:
            self.fail("undock did not leave the robot clear of the dock")
            return False

        self.phase = MissionPhase.READY
        return True

    def retry_undock(self) -> bool:
        if self.phase != MissionPhase.UNDOCKING:
            return False

        self.phase = MissionPhase.NEEDS_UNDOCK
        return True

    def begin_navigation(self) -> bool:
        if self.phase != MissionPhase.READY:
            return False

        self.phase = MissionPhase.NAVIGATING
        return True

    def navigation_completed(self, *, has_pending: bool) -> bool:
        """
        Complete the current navigation mission.

        Navigation completion never starts a docking lifecycle. If another
        command is pending, the bridge can start it from READY. If the queue is
        empty, the robot simply remains at the current destination.
        """
        if self.phase != MissionPhase.NAVIGATING:
            return False

        self.phase = MissionPhase.READY
        return True

    def begin_return_to_dock(self) -> bool:
        """
        Preserve the existing return-to-dock transition for future explicit
        DOCK commands. Normal navigation does not enter READY_TO_DOCK.
        """
        if self.phase != MissionPhase.READY_TO_DOCK:
            return False

        self.phase = MissionPhase.RETURNING_TO_DOCK
        return True

    def return_to_dock_completed(
        self,
        *,
        succeeded: bool,
        has_pending: bool,
    ) -> bool:
        if self.phase != MissionPhase.RETURNING_TO_DOCK:
            return False

        if not succeeded:
            self.fail("navigation to dock approach failed")
            return False

        self.phase = (
            MissionPhase.READY
            if has_pending
            else MissionPhase.READY_FOR_DOCK
        )
        return True

    def begin_docking(self) -> bool:
        """
        Preserve the existing docking transition for future explicit DOCK
        commands. Normal navigation does not enter READY_FOR_DOCK.
        """
        if self.phase != MissionPhase.READY_FOR_DOCK:
            return False

        self.phase = MissionPhase.DOCKING
        return True

    def docking_completed(
        self,
        *,
        succeeded: bool,
        is_docked: bool,
        has_pending: bool,
    ) -> bool:
        if self.phase != MissionPhase.DOCKING:
            return False

        if not succeeded or not is_docked:
            self.fail("dock did not confirm that the robot is docked")
            return False

        self.phase = (
            MissionPhase.NEEDS_UNDOCK
            if has_pending
            else MissionPhase.DOCKED
        )
        return True

    def retry_docking(self) -> bool:
        if self.phase != MissionPhase.DOCKING:
            return False

        self.phase = MissionPhase.READY_FOR_DOCK
        return True

    def fail(self, reason: str) -> None:
        self.phase = MissionPhase.FAILED
        self.failure_reason = reason
