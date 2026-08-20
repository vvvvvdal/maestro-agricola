import unittest

from maestro_robot_bridge.bridge_core import BridgeCore
from maestro_robot_bridge.models import Command, Target


class BridgeCoreTest(unittest.TestCase):

    def command(
        self,
        intent: str,
        target=None,
    ):
        return Command(
            schema_version="1.0",
            command_id="123e4567-e89b-12d3-a456-426614174000",
            created_at="2026-08-20T12:00:00Z",
            expires_in_ms=5000,
            intent=intent,
            target=target,
            confirmed=True,
        )

    def test_accepts_spray_known_plot(self):
        bridge = BridgeCore(
            target_map={
                "plot-01": {
                    "x": 1.0,
                    "y": 2.0,
                }
            }
        )

        response = bridge.handle_command(
            self.command(
                "SPRAY",
                Target(
                    type="MAPPED_PLOT",
                    id="plot-01",
                ),
            )
        )

        self.assertEqual(response.status, "ACCEPTED")

    def test_rejects_unknown_spray_plot(self):
        bridge = BridgeCore()

        response = bridge.handle_command(
            self.command(
                "SPRAY",
                Target(
                    type="MAPPED_PLOT",
                    id="plot-99",
                ),
            )
        )

        self.assertEqual(response.status, "REJECTED")

    def test_accepts_dock_contract(self):
        bridge = BridgeCore()

        response = bridge.handle_command(
            self.command("DOCK")
        )

        self.assertEqual(response.status, "ACCEPTED")

    def test_accepts_undock_contract(self):
        bridge = BridgeCore()

        response = bridge.handle_command(
            self.command("UNDOCK")
        )

        self.assertEqual(response.status, "ACCEPTED")


if __name__ == "__main__":
    unittest.main()