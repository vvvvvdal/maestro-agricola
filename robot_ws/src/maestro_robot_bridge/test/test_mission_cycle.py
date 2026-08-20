import unittest

from maestro_robot_bridge.mission_cycle import MissionCycle, MissionPhase


class MissionCycleTest(unittest.TestCase):

    def test_default_phase_is_ready(self):
        cycle = MissionCycle()

        self.assertEqual(MissionPhase.READY, cycle.phase)
        self.assertIsNone(cycle.failure_reason)

    def test_runs_navigation_and_remains_ready(self):
        cycle = MissionCycle()

        self.assertTrue(cycle.command_queued())
        self.assertTrue(cycle.begin_navigation())
        self.assertEqual(MissionPhase.NAVIGATING, cycle.phase)

        self.assertTrue(cycle.navigation_completed(has_pending=False))

        self.assertEqual(MissionPhase.READY, cycle.phase)

    def test_consecutive_navigation_goals_without_implicit_dock(self):
        cycle = MissionCycle()

        self.assertTrue(cycle.command_queued())
        self.assertTrue(cycle.begin_navigation())

        self.assertTrue(cycle.command_queued())

        self.assertTrue(cycle.navigation_completed(has_pending=True))
        self.assertEqual(MissionPhase.READY, cycle.phase)

        self.assertTrue(cycle.begin_navigation())
        self.assertEqual(MissionPhase.NAVIGATING, cycle.phase)

        self.assertTrue(cycle.navigation_completed(has_pending=False))
        self.assertEqual(MissionPhase.READY, cycle.phase)

    def test_docked_robot_does_not_implicitly_undock(self):
        cycle = MissionCycle(phase=MissionPhase.DOCKED)

        self.assertFalse(cycle.command_queued())
        self.assertEqual(MissionPhase.DOCKED, cycle.phase)

    def test_explicit_undock_request_moves_to_queue(self):
        cycle = MissionCycle()

        self.assertTrue(cycle.request_undock())
        self.assertEqual(
            MissionPhase.NEEDS_UNDOCK,
            cycle.phase,
        )

        self.assertTrue(cycle.begin_undock())
        self.assertEqual(
            MissionPhase.UNDOCKING,
            cycle.phase,
        )

    def test_undock_request_cannot_start_from_unavailable_state(self):
        cycle = MissionCycle(
            phase=MissionPhase.NAVIGATING
        )

        self.assertFalse(cycle.request_undock())
        self.assertEqual(
            MissionPhase.NAVIGATING,
            cycle.phase,
        )

    def test_manual_undock_utility_transitions(self):
        cycle = MissionCycle(phase=MissionPhase.NEEDS_UNDOCK)

        self.assertTrue(cycle.begin_undock())
        self.assertEqual(MissionPhase.UNDOCKING, cycle.phase)

        self.assertTrue(
            cycle.undock_completed(
                succeeded=True,
                is_docked=False,
            )
        )

        self.assertEqual(MissionPhase.READY, cycle.phase)

    def test_undock_cannot_begin_from_ready(self):
        cycle = MissionCycle()

        self.assertFalse(cycle.begin_undock())
        self.assertEqual(MissionPhase.READY, cycle.phase)

    def test_undock_failure_is_fail_closed(self):
        cycle = MissionCycle(phase=MissionPhase.NEEDS_UNDOCK)

        self.assertTrue(cycle.begin_undock())

        self.assertFalse(
            cycle.undock_completed(
                succeeded=False,
                is_docked=True,
            )
        )

        self.assertEqual(MissionPhase.FAILED, cycle.phase)
        self.assertIsNotNone(cycle.failure_reason)
        self.assertFalse(cycle.command_queued())
        self.assertFalse(cycle.begin_navigation())

    def test_transient_undock_rejection_can_be_retried(self):
        cycle = MissionCycle(phase=MissionPhase.NEEDS_UNDOCK)

        self.assertTrue(cycle.begin_undock())

        self.assertTrue(cycle.retry_undock())
        self.assertEqual(
            MissionPhase.NEEDS_UNDOCK,
            cycle.phase,
        )

        self.assertTrue(cycle.begin_undock())

        self.assertTrue(
            cycle.undock_completed(
                succeeded=True,
                is_docked=False,
            )
        )

        self.assertEqual(MissionPhase.READY, cycle.phase)

    def test_command_does_not_cancel_docking_lifecycle(self):
        for phase in (
            MissionPhase.NEEDS_UNDOCK,
            MissionPhase.UNDOCKING,
            MissionPhase.READY_TO_DOCK,
            MissionPhase.RETURNING_TO_DOCK,
            MissionPhase.READY_FOR_DOCK,
            MissionPhase.DOCKING,
        ):
            with self.subTest(phase=phase):
                cycle = MissionCycle(phase=phase)

                self.assertFalse(cycle.command_queued())
                self.assertEqual(phase, cycle.phase)

    def test_manual_dock_utility_transitions(self):
        cycle = MissionCycle(phase=MissionPhase.READY_TO_DOCK)

        self.assertTrue(cycle.begin_return_to_dock())
        self.assertEqual(
            MissionPhase.RETURNING_TO_DOCK,
            cycle.phase,
        )

        self.assertTrue(
            cycle.return_to_dock_completed(
                succeeded=True,
                has_pending=False,
            )
        )

        self.assertEqual(
            MissionPhase.READY_FOR_DOCK,
            cycle.phase,
        )

        self.assertTrue(cycle.begin_docking())

        self.assertTrue(
            cycle.docking_completed(
                succeeded=True,
                is_docked=True,
                has_pending=False,
            )
        )

        self.assertEqual(
            MissionPhase.DOCKED,
            cycle.phase,
        )

    def test_return_to_dock_cannot_begin_from_ready(self):
        cycle = MissionCycle()

        self.assertFalse(cycle.begin_return_to_dock())
        self.assertEqual(
            MissionPhase.READY,
            cycle.phase,
        )

    def test_return_to_dock_failure_blocks_dock_servo(self):
        cycle = MissionCycle(
            phase=MissionPhase.READY_TO_DOCK
        )

        self.assertTrue(
            cycle.begin_return_to_dock()
        )

        self.assertFalse(
            cycle.return_to_dock_completed(
                succeeded=False,
                has_pending=False,
            )
        )

        self.assertEqual(
            MissionPhase.FAILED,
            cycle.phase,
        )

    def test_dock_failure_is_fail_closed(self):
        cycle = MissionCycle(
            phase=MissionPhase.READY_FOR_DOCK
        )

        self.assertTrue(
            cycle.begin_docking()
        )

        self.assertFalse(
            cycle.docking_completed(
                succeeded=False,
                is_docked=False,
                has_pending=False,
            )
        )

        self.assertEqual(
            MissionPhase.FAILED,
            cycle.phase,
        )

    def test_transient_dock_rejection_can_be_retried(self):
        cycle = MissionCycle(
            phase=MissionPhase.READY_FOR_DOCK
        )

        self.assertTrue(
            cycle.begin_docking()
        )

        self.assertTrue(
            cycle.retry_docking()
        )

        self.assertEqual(
            MissionPhase.READY_FOR_DOCK,
            cycle.phase,
        )

    def test_navigation_cannot_begin_from_docked_state(self):
        cycle = MissionCycle(
            phase=MissionPhase.DOCKED
        )

        self.assertFalse(
            cycle.begin_navigation()
        )

        self.assertEqual(
            MissionPhase.DOCKED,
            cycle.phase,
        )


if __name__ == "__main__":
    unittest.main()