import json
import unittest

from maestro_robot_bridge.bridge_core import BridgeCore
from maestro_robot_bridge.models import PoseTarget
from maestro_robot_bridge.operation_history import OperationHistory
from maestro_robot_bridge.read_only_query_service import ReadOnlyQueryService
from maestro_robot_bridge.target_map import TargetMap
from maestro_robot_bridge.websocket_server import BridgeWebSocketServer


class WebSocketRoutingTest(unittest.TestCase):
    def test_read_only_route_never_calls_command_dispatcher(self):
        history = OperationHistory(timestamp=lambda: "2026-09-25T15:32:18Z")
        history.record_navigation_completion(
            succeeded=True,
            command_id="completed-command",
            plot_id="plot-02",
        )
        target_map = TargetMap({"plot-02": PoseTarget("plot-02", 2.0, 3.0, 0.0)})
        command_core = BridgeCore(
            target_map=target_map,
            navigation_callback=lambda *_: (_ for _ in ()).throw(
                AssertionError("read-only route called navigation")
            ),
        )
        server = BridgeWebSocketServer(
            command_core,
            ReadOnlyQueryService(target_map, history),
            "127.0.0.1",
            0,
        )

        response = server._response_for(
            "/read-only",
            json.dumps(
                {
                    "schema_version": "1.0",
                    "request_id": "123e4567-e89b-12d3-a456-426614174000",
                    "requested_at": "2026-09-25T15:34:00Z",
                    "kind": "LAST_SIMULATED_SPRAY_FOR_PLOT",
                    "plot_id": "plot-02",
                }
            ),
        )

        self.assertEqual(response.status, "FOUND")
        self.assertEqual(response.record.plot_id, "plot-02")


if __name__ == "__main__":
    unittest.main()
