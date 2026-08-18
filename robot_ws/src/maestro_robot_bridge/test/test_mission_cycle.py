import unittest

from maestro_robot_bridge.mission_cycle import MissionCycle, MissionPhase


class MissionCycleTest(unittest.TestCase):
    def ready_cycle(self) -> MissionCycle:
        cycle = MissionCycle()
        self.assertTrue(cycle.begin_undock())
        self.assertTrue(cycle.undock_completed(succeeded=True, is_docked=False))
        self.assertEqual(MissionPhase.READY, cycle.phase)
        return cycle

    def test_runs_undock_navigation_and_dock(self):
        cycle = self.ready_cycle()
        self.assertTrue(cycle.command_queued())
        self.assertTrue(cycle.begin_navigation())
        self.assertTrue(cycle.navigation_completed(has_pending=False))
        self.assertTrue(cycle.begin_docking())
        self.assertTrue(
            cycle.docking_completed(succeeded=True, is_docked=True, has_pending=False)
        )
        self.assertEqual(MissionPhase.DOCKED, cycle.phase)

    def test_new_goal_before_dock_keeps_robot_ready(self):
        cycle = self.ready_cycle()
        cycle.begin_navigation()
        cycle.navigation_completed(has_pending=False)
        self.assertTrue(cycle.command_queued())
        self.assertEqual(MissionPhase.READY, cycle.phase)

    def test_goal_queued_while_docking_starts_a_new_cycle_after_dock(self):
        cycle = self.ready_cycle()
        cycle.begin_navigation()
        cycle.navigation_completed(has_pending=False)
        cycle.begin_docking()
        self.assertTrue(cycle.command_queued())
        cycle.docking_completed(succeeded=True, is_docked=True, has_pending=True)
        self.assertEqual(MissionPhase.NEEDS_UNDOCK, cycle.phase)

    def test_undock_failure_blocks_commands(self):
        cycle = MissionCycle()
        cycle.begin_undock()
        self.assertFalse(cycle.undock_completed(succeeded=False, is_docked=True))
        self.assertEqual(MissionPhase.FAILED, cycle.phase)
        self.assertFalse(cycle.command_queued())

    def test_navigation_failure_can_still_proceed_to_dock(self):
        cycle = self.ready_cycle()
        cycle.begin_navigation()
        self.assertTrue(cycle.navigation_completed(has_pending=False))
        self.assertEqual(MissionPhase.READY_TO_DOCK, cycle.phase)

    def test_dock_failure_blocks_another_mission(self):
        cycle = self.ready_cycle()
        cycle.begin_navigation()
        cycle.navigation_completed(has_pending=False)
        cycle.begin_docking()
        self.assertFalse(
            cycle.docking_completed(succeeded=False, is_docked=False, has_pending=False)
        )
        self.assertEqual(MissionPhase.FAILED, cycle.phase)
        self.assertFalse(cycle.command_queued())


if __name__ == "__main__":
    unittest.main()
