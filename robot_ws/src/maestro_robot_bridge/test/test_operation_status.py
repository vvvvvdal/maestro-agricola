import unittest

from maestro_robot_bridge.models import Command, Target
from maestro_robot_bridge.operation_status import (
    COMPLETED,
    EXECUTING,
    FAILED,
    QUEUED,
    OperationStatusTracker,
)


def command(command_id: str, intent: str = "SPRAY"):
    return Command(
        schema_version="1.0",
        command_id=command_id,
        created_at="2026-09-25T15:34:00Z",
        expires_in_ms=5000,
        intent=intent,
        target=Target(type="MAPPED_PLOT", id="plot-02") if intent == "SPRAY" else None,
        confirmed=True,
    )


class OperationStatusTrackerTest(unittest.TestCase):
    def test_tracks_lifecycle_for_one_command(self):
        tracker = OperationStatusTracker()
        tracker.accepted(command("command-1"))
        self.assertEqual(tracker.get("command-1").state, QUEUED)

        tracker.executing("command-1")
        self.assertEqual(tracker.get("command-1").state, EXECUTING)

        tracker.completed("command-1")
        self.assertEqual(tracker.get("command-1").state, COMPLETED)

    def test_fails_all_non_terminal_commands(self):
        tracker = OperationStatusTracker()
        tracker.accepted(command("command-1"))
        tracker.accepted(command("command-2", intent="UNDOCK"))
        tracker.completed("command-1")

        tracker.fail_in_flight()

        self.assertEqual(tracker.get("command-1").state, COMPLETED)
        self.assertEqual(tracker.get("command-2").state, FAILED)


if __name__ == "__main__":
    unittest.main()
