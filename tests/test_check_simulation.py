import sys
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from check_simulation import evaluate_mission_logs, wait_for_nav2  # noqa: E402


class MissionLogStatusTest(unittest.TestCase):
    @patch("check_simulation.time.sleep")
    @patch("check_simulation.require_no_fatal_render_error")
    @patch("check_simulation.require_processes")
    @patch("check_simulation.container_shell")
    def test_nav2_probe_retries_a_transient_cli_timeout(
        self,
        container_shell,
        _require_processes,
        _require_no_fatal_render_error,
        _sleep,
    ):
        container_shell.side_effect = [
            subprocess.TimeoutExpired(["ros2", "lifecycle", "get"], 10),
            subprocess.CompletedProcess([], 0, "active [3]"),
        ]

        wait_for_nav2(30)

        self.assertEqual(2, container_shell.call_count)

    def test_requires_ordered_targets_and_dock(self):
        logs = "\n".join([
            "Undock completed: robot is clear of dock",
            "Nav2 completed command a for target plot-01",
            "Nav2 completed command b for target plot-02",
            "Nav2 completed command c for target plot-03",
            "Nav2 completed return-to-dock approach",
            "Dock completed: robot is docked",
        ])
        status = evaluate_mission_logs(logs, ["plot-01", "plot-02", "plot-03"])
        self.assertTrue(status.undocked)
        self.assertEqual(("plot-01", "plot-02", "plot-03"), status.completed_targets)
        self.assertTrue(status.docked)
        self.assertIsNone(status.failure)

    def test_does_not_accept_dock_before_last_target(self):
        logs = "\n".join([
            "Undock completed: robot is clear of dock",
            "Nav2 completed command a for target plot-01",
            "Dock completed: robot is docked",
            "Nav2 completed command b for target plot-02",
            "Nav2 completed return-to-dock approach",
        ])
        status = evaluate_mission_logs(logs, ["plot-01", "plot-02"])
        self.assertFalse(status.docked)

    def test_does_not_accept_servo_dock_without_global_return(self):
        logs = "\n".join([
            "Undock completed: robot is clear of dock",
            "Nav2 completed command a for target plot-03",
            "Dock completed: robot is docked",
        ])
        status = evaluate_mission_logs(logs, ["plot-03"])
        self.assertFalse(status.docked)

    def test_reports_navigation_timeout_after_latest_undock(self):
        logs = "\n".join([
            "navigation timed out",
            "Undock completed: robot is clear of dock",
            "Nav2 accepted command a for target plot-01",
            "navigation timed out",
        ])
        status = evaluate_mission_logs(logs, ["plot-01"])
        self.assertEqual("navigation timed out", status.failure)


if __name__ == "__main__":
    unittest.main()
