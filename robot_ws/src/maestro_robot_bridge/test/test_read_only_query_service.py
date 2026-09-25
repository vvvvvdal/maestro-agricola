import json
import unittest

from maestro_robot_bridge.models import Command, PoseTarget, Target
from maestro_robot_bridge.operation_history import OperationHistory
from maestro_robot_bridge.operation_status import (
    COMPLETED,
    EXECUTING,
    OperationStatusTracker,
)
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


def status_payload(**overrides):
    payload = {
        "schema_version": "1.0",
        "request_id": REQUEST_ID,
        "requested_at": "2026-09-25T15:34:00Z",
        "kind": "ROBOT_STATUS",
    }
    payload.update(overrides)
    return json.dumps(payload)


class ReadOnlyQueryServiceTest(unittest.TestCase):
    def setUp(self):
        self.history = OperationHistory(timestamp=lambda: "2026-09-25T15:32:18Z")
        self.status = OperationStatusTracker()
        self.service = ReadOnlyQueryService(
            TargetMap(
                {
                    "plot-01": PoseTarget("plot-01", 1.0, 2.0, 0.0),
                    "plot-02": PoseTarget("plot-02", 2.0, 3.0, 0.0),
                }
            ),
            self.history,
            self.status,
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

    def test_returns_status_for_the_same_accepted_command(self):
        command = Command(
            schema_version="1.0",
            command_id=REQUEST_ID,
            created_at="2026-09-25T15:34:00Z",
            expires_in_ms=5000,
            intent="SPRAY",
            target=Target(type="MAPPED_PLOT", id="plot-02"),
            confirmed=True,
        )
        self.status.accepted(command)
        self.status.executing(REQUEST_ID)

        response = self.service.handle(status_payload(command_id=REQUEST_ID))

        self.assertEqual(response.status, "FOUND")
        self.assertEqual(response.kind, "ROBOT_STATUS")
        self.assertEqual(response.operation.command_id, REQUEST_ID)
        self.assertEqual(response.operation.intent, "SPRAY")
        self.assertEqual(response.operation.target_id, "plot-02")
        self.assertEqual(response.operation.state, EXECUTING)

        self.status.completed(REQUEST_ID)
        completed = self.service.handle(status_payload(command_id=REQUEST_ID))
        self.assertEqual(completed.operation.state, COMPLETED)

    def test_returns_latest_status_without_command_id(self):
        response = self.service.handle(status_payload())

        self.assertEqual(response.status, "NOT_FOUND")
        self.assertIsNone(response.operation)

    def test_rejects_plot_id_on_robot_status_query(self):
        response = self.service.handle(status_payload(plot_id="plot-02"))

        self.assertEqual(response.status, "INVALID_QUERY")
        self.assertIsNone(response.operation)


if __name__ == "__main__":
    unittest.main()
