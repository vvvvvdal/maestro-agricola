import json
import unittest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from maestro_robot_bridge.contract import ContractError, parse_command


NOW = datetime(2026, 8, 16, 15, 0, 0, tzinfo=timezone.utc)


def command(**overrides):
    payload = {
        "schema_version": "1.0",
        "command_id": str(uuid4()),
        "created_at": (NOW - timedelta(seconds=1)).isoformat(),
        "expires_in_ms": 5000,
        "intent": "SPRAY",
        "target": {"type": "MAPPED_PLOT", "id": "plot-03"},
        "confirmed": True,
    }
    payload.update(overrides)
    return json.dumps(payload)


class ContractTest(unittest.TestCase):
    def test_accepts_valid_command(self):
        self.assertEqual("plot-03", parse_command(command(), now=NOW).target.id)

    def test_rejects_unsafe_commands(self):
        cases = [
            ({"confirmed": False}, "confirmation"),
            ({"intent": "DRIVE"}, "intent"),
            ({"expires_in_ms": 0}, "expires_in_ms"),
            ({"created_at": (NOW - timedelta(seconds=10)).isoformat()}, "expired"),
        ]
        for override, reason in cases:
            with self.subTest(override=override):
                with self.assertRaisesRegex(ContractError, reason):
                    parse_command(command(**override), now=NOW)


if __name__ == "__main__":
    unittest.main()
