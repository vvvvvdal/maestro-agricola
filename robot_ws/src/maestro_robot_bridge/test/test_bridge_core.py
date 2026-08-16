import json
import unittest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from maestro_robot_bridge.bridge_core import BridgeCore
from maestro_robot_bridge.models import PoseTarget
from maestro_robot_bridge.target_map import TargetMap


NOW = datetime(2026, 8, 16, 15, 0, 0, tzinfo=timezone.utc)


def payload(command_id=None, target_id="plot-03"):
    return json.dumps({
        "schema_version": "1.0",
        "command_id": command_id or str(uuid4()),
        "created_at": (NOW - timedelta(seconds=1)).isoformat(),
        "expires_in_ms": 5000,
        "intent": "SPRAY",
        "target": {"type": "MAPPED_PLOT", "id": target_id},
        "confirmed": True,
    })


class BridgeCoreTest(unittest.TestCase):
    def setUp(self):
        self.target_map = TargetMap({"plot-03": PoseTarget("plot-03", 1.5, 1.0, 0.0)})

    def test_dispatches_mapped_target_once(self):
        calls = []

        def dispatch(pose, command_id):
            calls.append((pose, command_id))
            return True, "queued"

        bridge = BridgeCore(self.target_map, dispatch)
        command_id = str(uuid4())
        first = bridge.handle(payload(command_id), now=NOW)
        second = bridge.handle(payload(command_id), now=NOW)
        self.assertEqual("ACCEPTED", first.status)
        self.assertEqual(first, second)
        self.assertEqual(1, len(calls))

    def test_rejects_unknown_target_without_dispatch(self):
        bridge = BridgeCore(self.target_map, lambda pose, command_id: (True, "queued"))
        response = bridge.handle(payload(target_id="plot-99"), now=NOW)
        self.assertEqual("REJECTED", response.status)
        self.assertEqual("target is not mapped", response.reason)


if __name__ == "__main__":
    unittest.main()
