from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MissionPhase(str, Enum):
    NEEDS_UNDOCK = "NEEDS_UNDOCK"
    UNDOCKING = "UNDOCKING"
    READY = "READY"
    NAVIGATING = "NAVIGATING"
    READY_TO_DOCK = "READY_TO_DOCK"
    DOCKING = "DOCKING"
    DOCKED = "DOCKED"
    FAILED = "FAILED"


@dataclass
class MissionCycle:
    """Fail-closed lifecycle for one or more queued navigation goals."""

    phase: MissionPhase = MissionPhase.NEEDS_UNDOCK
    failure_reason: str | None = None

    def command_queued(self) -> bool:
        if self.phase == MissionPhase.FAILED:
            return False
        if self.phase == MissionPhase.DOCKED:
            self.phase = MissionPhase.NEEDS_UNDOCK
        elif self.phase == MissionPhase.READY_TO_DOCK:
            self.phase = MissionPhase.READY
        return True

    def begin_undock(self) -> bool:
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
        if self.phase != MissionPhase.NAVIGATING:
            return False
        self.phase = MissionPhase.READY if has_pending else MissionPhase.READY_TO_DOCK
        return True

    def begin_docking(self) -> bool:
        if self.phase != MissionPhase.READY_TO_DOCK:
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
        self.phase = MissionPhase.NEEDS_UNDOCK if has_pending else MissionPhase.DOCKED
        return True

    def retry_docking(self) -> bool:
        if self.phase != MissionPhase.DOCKING:
            return False
        self.phase = MissionPhase.READY_TO_DOCK
        return True

    def fail(self, reason: str) -> None:
        self.phase = MissionPhase.FAILED
        self.failure_reason = reason
