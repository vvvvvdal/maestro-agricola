import json
import unittest
from datetime import datetime, timezone

from maestro_robot_bridge.contract import (
    ContractError,
    parse_command,
)


BASE = {
    "schema_version": "1.0",
    "command_id": "123e4567-e89b-12d3-a456-426614174000",
    "expires_in_ms": 5000,
    "confirmed": True,
}


def payload(**kwargs):
    data = {
        **BASE,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "intent": "SPRAY",
        "target": {
            "type": "MAPPED_PLOT",
            "id": "plot-01",
        },
    }

    data.update(kwargs)
    return data


class ContractTest(unittest.TestCase):

    def test_accepts_spray_with_plot(self):
        command = parse_command(
            json.dumps(payload())
        )

        self.assertEqual(command.intent, "SPRAY")
        self.assertEqual(command.target.id, "plot-01")

    def test_accepts_dock_without_target(self):
        command = parse_command(
            json.dumps(
                payload(
                    intent="DOCK",
                    target=None,
                )
            )
        )

        self.assertEqual(command.intent, "DOCK")
        self.assertIsNone(command.target)

    def test_accepts_undock_without_target(self):
        command = parse_command(
            json.dumps(
                payload(
                    intent="UNDOCK",
                    target=None,
                )
            )
        )

        self.assertEqual(command.intent, "UNDOCK")
        self.assertIsNone(command.target)

    def test_rejects_unconfirmed_command(self):
        with self.assertRaises(ContractError) as caught:
            parse_command(
                json.dumps(
                    payload(
                        confirmed=False,
                    )
                )
            )

        self.assertEqual(
            caught.exception.reason,
            "explicit confirmation is required",
        )

    def test_rejects_expired_command(self):
        now = datetime(
            2026,
            8,
            22,
            12,
            0,
            0,
            tzinfo=timezone.utc,
        )

        with self.assertRaises(ContractError) as caught:
            parse_command(
                json.dumps(
                    payload(
                        created_at="2026-08-22T11:59:50+00:00",
                        expires_in_ms=5000,
                    )
                ),
                now=now,
            )

        self.assertEqual(
            caught.exception.reason,
            "command expired",
        )

    def test_rejects_spray_without_target(self):
        with self.assertRaises(ContractError):
            parse_command(
                json.dumps(
                    payload(
                        target=None,
                    )
                )
            )

    def test_rejects_dock_with_target(self):
        with self.assertRaises(ContractError):
            parse_command(
                json.dumps(
                    payload(
                        intent="DOCK",
                    )
                )
            )


if __name__ == "__main__":
    unittest.main()