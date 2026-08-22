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
    finishes.

    Docking and undocking are explicit commands. They are never triggered by
    normal navigation completion.
    """

    phase: MissionPhase = MissionPhase.READY
    failure_reason: str | None = None

    def command_queued(self) -> bool:
        """
        Accept navigation commands only while the robot is available.

        A navigation command never changes docking state implicitly.
        """
        return self.phase in (
            MissionPhase.READY,
            MissionPhase.NAVIGATING,
        )

    # ------------------------------------------------------------------
    # Explicit UNDOCK command
    # ------------------------------------------------------------------

    def request_undock(self) -> bool:
        """
        Register an explicit UNDOCK command.

        This only changes lifecycle state. The ROS action is executed by the
        bridge lifecycle loop.
        """
        if self.phase not in (
            MissionPhase.READY,
            MissionPhase.DOCKED,
        ):
            return False

        self.phase = MissionPhase.NEEDS_UNDOCK
        return True

    def begin_undock(self) -> bool:
        """
        Start the ROS undock action after an explicit UNDOCK request.
        """
        if self.phase != MissionPhase.NEEDS_UNDOCK:
            return False

        self.phase = MissionPhase.UNDOCKING
        return True

    def undock_completed(
        self,
        *,
        succeeded: bool,
        is_docked: bool,
    ) -> bool:
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

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def begin_navigation(self) -> bool:
        if self.phase != MissionPhase.READY:
            return False

        self.phase = MissionPhase.NAVIGATING
        return True

    def navigation_completed(
        self,
        *,
        has_pending: bool,
    ) -> bool:
        """
        Finish navigation.

        Never starts return-to-dock or docking automatically.
        """
        if self.phase != MissionPhase.NAVIGATING:
            return False

        self.phase = MissionPhase.READY
        return True

    # ------------------------------------------------------------------
    # Explicit DOCK command
    # ------------------------------------------------------------------

    def request_dock(self) -> bool:
        """
        Register an explicit DOCK command.

        The bridge will later execute the approach navigation and docking
        action.
        """
        if self.phase != MissionPhase.READY:
            return False

        self.phase = MissionPhase.READY_TO_DOCK
        return True

    def begin_return_to_dock(self) -> bool:
        """
        Start navigation to the configured dock approach pose.
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

        self.phase = MissionPhase.READY_FOR_DOCK
        return True

    def begin_docking(self) -> bool:
        """
        Start the physical docking action after successful approach navigation.
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

    # ------------------------------------------------------------------
    # Failure
    # ------------------------------------------------------------------

    def fail(self, reason: str) -> None:
        self.phase = MissionPhase.FAILED
        self.failure_reason = reason