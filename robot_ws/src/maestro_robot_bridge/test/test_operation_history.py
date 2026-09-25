import unittest

from maestro_robot_bridge.operation_history import (
    MAX_OPERATION_RECORDS,
    OperationHistory,
)


class OperationHistoryTest(unittest.TestCase):
    def test_records_only_successful_navigation_completion(self):
        history = OperationHistory(timestamp=lambda: "2026-09-25T15:32:18Z")

        rejected = history.record_navigation_completion(
            succeeded=False,
            command_id="failed-command",
            plot_id="plot-02",
        )
        completed = history.record_navigation_completion(
            succeeded=True,
            command_id="completed-command",
            plot_id="plot-02",
        )

        self.assertIsNone(rejected)
        self.assertEqual(
            completed,
            history.records()[0],
        )
        self.assertEqual(completed.operation_id, "completed-command")
        self.assertEqual(completed.kind, "SIMULATED_SPRAY_ARRIVAL")
        self.assertEqual(completed.plot_id, "plot-02")
        self.assertEqual(completed.completed_at, "2026-09-25T15:32:18Z")
        self.assertEqual(completed.origin, "GAZEBO_SIMULATOR")

    def test_deduplicates_a_repeated_final_callback(self):
        history = OperationHistory(timestamp=lambda: "2026-09-25T15:32:18Z")

        first = history.record_navigation_completion(
            succeeded=True,
            command_id="command-01",
            plot_id="plot-01",
        )
        second = history.record_navigation_completion(
            succeeded=True,
            command_id="command-01",
            plot_id="plot-01",
        )

        self.assertEqual(first, second)
        self.assertEqual(len(history.records()), 1)

    def test_discards_the_oldest_record_after_the_session_limit(self):
        history = OperationHistory(timestamp=lambda: "2026-09-25T15:32:18Z")

        for index in range(MAX_OPERATION_RECORDS + 1):
            history.record_navigation_completion(
                succeeded=True,
                command_id=f"command-{index}",
                plot_id="plot-01",
            )

        records = history.records()

        self.assertEqual(len(records), MAX_OPERATION_RECORDS)
        self.assertEqual(records[0].operation_id, "command-1")
        self.assertEqual(
            records[-1].operation_id,
            f"command-{MAX_OPERATION_RECORDS}",
        )

    def test_new_history_starts_empty_for_a_new_simulator_session(self):
        previous_session = OperationHistory(
            timestamp=lambda: "2026-09-25T15:32:18Z"
        )
        previous_session.record_navigation_completion(
            succeeded=True,
            command_id="command-01",
            plot_id="plot-01",
        )

        new_session = OperationHistory(
            timestamp=lambda: "2026-09-25T15:33:18Z"
        )

        self.assertEqual(new_session.records(), ())


if __name__ == "__main__":
    unittest.main()
