import unittest

from maestro_robot_bridge.bridge_core import BridgeCore
from maestro_robot_bridge.models import Command, Target


def command(intent, target=None):
    return Command(
        schema_version="1.0",
        command_id="123e4567-e89b-12d3-a456-426614174000",
        created_at="2026-08-20T12:00:00Z",
        expires_in_ms=5000,
        confirmed=True,
        intent=intent,
        target=target,
    )


class BridgeCoreTest(unittest.TestCase):

    def test_accepts_spray_known_plot(self):
        calls = []

        bridge = BridgeCore(
            target_map={
                "plot-01": {
                    "x": 1.0,
                    "y": 2.0,
                }
            },
            navigation_callback=lambda pose, command_id: (
                calls.append((pose, command_id))
                or (True, "navigation queued")
            ),
        )

        response = bridge.handle_command(
            command(
                "SPRAY",
                Target(
                    type="MAPPED_PLOT",
                    id="plot-01",
                ),
            )
        )

        self.assertEqual(response.status, "ACCEPTED")
        self.assertEqual(response.reason, "navigation queued")
        self.assertEqual(len(calls), 1)

    def test_rejects_unknown_spray_plot(self):
        bridge = BridgeCore(
            target_map={},
            navigation_callback=lambda *_: (
                True,
                "should not execute",
            ),
        )

        response = bridge.handle_command(
            command(
                "SPRAY",
                Target(
                    type="MAPPED_PLOT",
                    id="plot-99",
                ),
            )
        )

        self.assertEqual(response.status, "REJECTED")
        self.assertEqual(response.reason, "unknown target")

    def test_accepts_dock_contract(self):
        calls = []

        bridge = BridgeCore(
            target_map={},
            navigation_callback=lambda *_: (
                True,
                "navigation queued",
            ),
            dock_callback=lambda: (
                calls.append(True)
                or (True, "dock command accepted")
            ),
        )

        response = bridge.handle_command(
            command("DOCK")
        )

        self.assertEqual(response.status, "ACCEPTED")
        self.assertEqual(response.reason, "dock command accepted")
        self.assertEqual(len(calls), 1)

    def test_accepts_undock_contract(self):
        calls = []

        bridge = BridgeCore(
            target_map={},
            navigation_callback=lambda *_: (
                True,
                "navigation queued",
            ),
            undock_callback=lambda: (
                calls.append(True)
                or (True, "undock command accepted")
            ),
        )

        response = bridge.handle_command(
            command("UNDOCK")
        )

        self.assertEqual(response.status, "ACCEPTED")
        self.assertEqual(response.reason, "undock command accepted")
        self.assertEqual(len(calls), 1)

    def test_rejects_undock_without_callback(self):
        bridge = BridgeCore(
            target_map={},
            navigation_callback=lambda *_: (
                True,
                "navigation queued",
            ),
        )

        response = bridge.handle_command(
            command("UNDOCK")
        )

        self.assertEqual(response.status, "REJECTED")
        self.assertEqual(response.reason, "undock unavailable")


if __name__ == "__main__":
    unittest.main()