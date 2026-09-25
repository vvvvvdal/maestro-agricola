import json
import unittest

from maestro_robot_bridge.models import PoseTarget
from maestro_robot_bridge.operation_history import OperationHistory
from maestro_robot_bridge.read_only_query_service import ReadOnlyQueryService
from maestro_robot_bridge.target_map import TargetMap


REQUEST_ID = "123e4567-e89b-12d3-a456-426614174000"


def query_payload(**overrides):
    payload = {
        "schema_version": "1.0",
        "request_id": REQUEST_ID,
        "requested_at": "2026-09-25T15:34:00Z",
        "kind": "LAST_SIMULATED_SPRAY_FOR_PLOT",
        "plot_id": "plot-02",
    }
    payload.update(overrides)
    return json.dumps(payload)


class ReadOnlyQueryServiceTest(unittest.TestCase):
    def setUp(self):
        self.history = OperationHistory(timestamp=lambda: "2026-09-25T15:32:18Z")
        self.service = ReadOnlyQueryService(
            TargetMap(
                {
                    "plot-01": PoseTarget("plot-01", 1.0, 2.0, 0.0),
                    "plot-02": PoseTarget("plot-02", 2.0, 3.0, 0.0),
                }
            ),
            self.history,
        )

    def test_returns_found_for_completed_simulated_spray(self):
        self.history.record_navigation_completion(
            succeeded=True,
            command_id="completed-command",
            plot_id="plot-02",
        )

        response = self.service.handle(query_payload())

        self.assertEqual(response.status, "FOUND")
        self.assertEqual(response.request_id, REQUEST_ID)
        self.assertEqual(response.record.plot_id, "plot-02")
        self.assertEqual(response.record.completed_at, "2026-09-25T15:32:18Z")
        self.assertFalse(hasattr(response.record, "operation_id"))

    def test_returns_not_found_without_history_for_known_plot(self):
        response = self.service.handle(query_payload())

        self.assertEqual(response.status, "NOT_FOUND")
        self.assertIsNone(response.record)

    def test_rejects_unknown_plot_without_reading_history(self):
        response = self.service.handle(query_payload(plot_id="plot-99"))

        self.assertEqual(response.status, "INVALID_QUERY")
        self.assertIsNone(response.record)

    def test_rejects_command_fields_on_the_read_only_route(self):
        response = self.service.handle(query_payload(confirmed=True))

        self.assertEqual(response.status, "INVALID_QUERY")
        self.assertIsNone(response.record)


if __name__ == "__main__":
    unittest.main()
