from __future__ import annotations

import math
from queue import Empty, Queue
from threading import Lock
from time import monotonic

import rclpy
from action_msgs.msg import GoalStatus
from ament_index_python.packages import get_package_share_directory
from irobot_create_msgs.action import Dock, Undock
from irobot_create_msgs.msg import DockStatus
from lifecycle_msgs.srv import GetState
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy

from .bridge_core import BridgeCore
from .mission_cycle import MissionCycle, MissionPhase
from .models import PoseTarget
from .target_map import TargetMap
from .websocket_server import BridgeWebSocketServer


class MaestroBridgeNode(Node):
    def __init__(self) -> None:
        super().__init__("maestro_robot_bridge")
        share = get_package_share_directory("maestro_robot_bridge")
        self.declare_parameter("host", "0.0.0.0")
        self.declare_parameter("port", 18765)
        self.declare_parameter("robot_namespace", "/turtlebot1")
        self.declare_parameter("map_frame", "map")
        self.declare_parameter("targets_path", f"{share}/config/targets.json")
        self.declare_parameter("dock_action_timeout_s", 120.0)
        self.declare_parameter("navigation_timeout_s", 180.0)
        self.declare_parameter("action_retry_limit", 5)
        self.declare_parameter("dock_approach_x", -0.5)
        self.declare_parameter("dock_approach_y", 0.0)
        self.declare_parameter("dock_approach_yaw", 0.0)

        namespace = str(self.get_parameter("robot_namespace").value).rstrip("/")
        self._map_frame = str(self.get_parameter("map_frame").value)
        self._dock_action_timeout_s = float(
            self.get_parameter("dock_action_timeout_s").value
        )
        self._navigation_timeout_s = float(
            self.get_parameter("navigation_timeout_s").value
        )
        self._action_retry_limit = int(self.get_parameter("action_retry_limit").value)
        self._dock_approach = PoseTarget(
            id="dock-approach",
            x=float(self.get_parameter("dock_approach_x").value),
            y=float(self.get_parameter("dock_approach_y").value),
            yaw=float(self.get_parameter("dock_approach_yaw").value),
        )
        self._pending: Queue[tuple[PoseTarget, str]] = Queue(maxsize=16)
        self._mission = MissionCycle()
        self._mission_lock = Lock()
        self._phase_started_at = self._clock_seconds()
        self._active_navigation: tuple[PoseTarget, str] | None = None
        self._undock_goal_handle = None
        self._nav_goal_handle = None
        self._return_goal_handle = None
        self._dock_goal_handle = None
        self._latest_is_docked: bool | None = None
        self._dock_status_changed_at = monotonic()
        self._undock_attempts = 0
        self._dock_attempts = 0
        self._next_undock_attempt_at = 0.0
        self._next_dock_attempt_at = 0.0

        self._undock_client = ActionClient(self, Undock, f"{namespace}/undock")
        self._nav_client = ActionClient(self, NavigateToPose, f"{namespace}/navigate_to_pose")
        self._dock_client = ActionClient(self, Dock, f"{namespace}/dock")
        self._dock_status_subscription = self.create_subscription(
            DockStatus,
            f"{namespace}/dock_status",
            self._dock_status_received,
            QoSProfile(depth=5, reliability=ReliabilityPolicy.BEST_EFFORT),
        )
        self._nav_state_client = self.create_client(
            GetState, f"{namespace}/bt_navigator/get_state"
        )
        self._nav_state_future = None
        self._nav_active = False
        target_map = TargetMap.load(str(self.get_parameter("targets_path").value))
        self._core = BridgeCore(
            target_map,
            self._queue_navigation,
            self._request_dock,
            self._request_undock,
        )
        self._server = BridgeWebSocketServer(
            self._core,
            str(self.get_parameter("host").value),
            int(self.get_parameter("port").value),
        )
        self._server.start()
        self._timer = self.create_timer(0.1, self._advance_mission)
        self.get_logger().info(
            f"Maestro WebSocket listening on {self.get_parameter('host').value}:"
            f"{self.get_parameter('port').value}"
        )
        self.get_logger().info(f"Mission lifecycle uses namespace {namespace}")

    def destroy_node(self) -> bool:
        self._server.close()
        return super().destroy_node()

    def _queue_navigation(self, pose: PoseTarget, command_id: str) -> tuple[bool, str]:
        with self._mission_lock:
            if self._pending.full():
                return False, "navigation queue is full"
            if self._latest_is_docked is True:
                return False, "robot unavailable: robot is docked"
            previous = self._mission.phase
            if not self._mission.command_queued():
                reason = self._mission.failure_reason or "mission lifecycle failed"
                return False, f"robot unavailable: {reason}"
            self._pending.put_nowait((pose, command_id))
            self._record_phase_change(previous)
        return True, "navigation goal queued"

    def _request_undock(self) -> tuple[bool, str]:
        with self._mission_lock:
            if not self._mission.begin_undock():
                return False, "robot unavailable for undock"

            self._record_phase_change(MissionPhase.READY)

        return True, "undock command accepted"


    def _request_dock(self) -> tuple[bool, str]:
        with self._mission_lock:
            if not self._mission.begin_docking():
                return False, "robot unavailable for dock"

            self._record_phase_change(MissionPhase.READY_FOR_DOCK)

        return True, "dock command accepted"

    def _advance_mission(self) -> None:
        phase = self._phase()
        if phase == MissionPhase.NEEDS_UNDOCK:
            self._start_undock()
        elif phase == MissionPhase.UNDOCKING:
            self._monitor_undock()
        elif phase == MissionPhase.READY:
            self._start_navigation()
        elif phase == MissionPhase.NAVIGATING:
            self._check_navigation_timeout()
        elif phase == MissionPhase.READY_TO_DOCK:
            self._start_return_to_dock()
        elif phase == MissionPhase.RETURNING_TO_DOCK:
            self._check_return_to_dock_timeout()
        elif phase == MissionPhase.READY_FOR_DOCK:
            self._start_dock()
        elif phase == MissionPhase.DOCKING:
            self._monitor_dock()

    def _start_undock(self) -> None:
        if monotonic() < self._next_undock_attempt_at:
            return
        if not self._dock_status_is_stable():
            self._fail_if_phase_expired("dock status")
            return
        if self._latest_is_docked is False:
            if self._transition(self._mission.begin_undock):
                self._complete_undock_from_state("robot already clear of dock")
            return
        if not self._undock_client.server_is_ready():
            self._fail_if_phase_expired("undock action server")
            return
        if not self._transition(self._mission.begin_undock):
            return
        self._undock_attempts += 1
        self.get_logger().info("Requesting undock before navigation")
        try:
            future = self._undock_client.send_goal_async(Undock.Goal())
        except Exception as exc:
            self._fail_mission(f"could not send undock goal: {exc}")
            return
        future.add_done_callback(self._undock_goal_response)

    def _undock_goal_response(self, future) -> None:
        if self._phase() != MissionPhase.UNDOCKING:
            return
        try:
            goal_handle = future.result()
        except Exception as exc:
            self._fail_mission(f"undock goal failed: {exc}")
            return
        if not goal_handle.accepted:
            self._retry_undock_or_accept_state()
            return
        self._undock_goal_handle = goal_handle
        self.get_logger().info("Undock goal accepted")
        goal_handle.get_result_async().add_done_callback(self._undock_result)

    def _undock_result(self, future) -> None:
        if self._phase() != MissionPhase.UNDOCKING:
            return
        try:
            wrapped = future.result()
            is_docked = bool(wrapped.result.is_docked)
            succeeded = wrapped.status == GoalStatus.STATUS_SUCCEEDED or not is_docked
        except Exception as exc:
            self._fail_mission(f"undock result failed: {exc}")
            return
        if self._transition(
            self._mission.undock_completed,
            succeeded=succeeded,
            is_docked=is_docked,
        ):
            self._undock_goal_handle = None
            self._undock_attempts = 0
            self.get_logger().info("Undock completed: robot is clear of dock")
        else:
            self._fail_mission(
                f"undock ended with status={wrapped.status}, is_docked={is_docked}"
            )

    def _start_navigation(self) -> None:
        if self._pending.empty():
            return
        if not self._nav_is_active() or not self._nav_client.server_is_ready():
            return
        if not self._transition(self._mission.begin_navigation):
            return
        try:
            pose, command_id = self._pending.get_nowait()
        except Empty:
            self._transition(self._mission.navigation_completed, has_pending=False)
            return

        self._active_navigation = (pose, command_id)
        goal = self._navigation_goal(pose)
        try:
            future = self._nav_client.send_goal_async(goal)
        except Exception as exc:
            self._complete_navigation(False, f"could not send Nav2 goal: {exc}")
            return
        future.add_done_callback(self._nav_goal_response)

    def _nav_goal_response(self, future) -> None:
        if self._phase() != MissionPhase.NAVIGATING:
            return
        pose, command_id = self._current_navigation()
        try:
            goal_handle = future.result()
        except Exception as exc:
            self._complete_navigation(False, f"Nav2 goal {command_id} failed: {exc}")
            return
        if not goal_handle.accepted:
            self._complete_navigation(False, f"Nav2 rejected command {command_id}")
            return
        self._nav_goal_handle = goal_handle
        self.get_logger().info(
            f"Nav2 accepted command {command_id} for target {pose.id}"
        )
        goal_handle.get_result_async().add_done_callback(self._nav_result)

    def _nav_result(self, future) -> None:
        if self._phase() != MissionPhase.NAVIGATING:
            return
        try:
            wrapped = future.result()
            succeeded = wrapped.status == GoalStatus.STATUS_SUCCEEDED
            reason = f"Nav2 ended with status={wrapped.status}"
        except Exception as exc:
            succeeded = False
            reason = f"Nav2 result failed: {exc}"
        self._complete_navigation(succeeded, reason)

    def _complete_navigation(self, succeeded: bool, failure_reason: str) -> None:
        pose, command_id = self._current_navigation()
        if succeeded:
            self.get_logger().info(
                f"Nav2 completed command {command_id} for target {pose.id}"
            )
        else:
            self.get_logger().error(f"{failure_reason} ({command_id}, {pose.id})")
        self._nav_goal_handle = None
        self._active_navigation = None
        self._transition(
            self._mission.navigation_completed,
            has_pending=not self._pending.empty(),
        )

    def _start_return_to_dock(self) -> None:
        if not self._nav_is_active() or not self._nav_client.server_is_ready():
            self._fail_if_navigation_phase_expired("Nav2 return-to-dock action server")
            return
        if not self._transition(self._mission.begin_return_to_dock):
            return
        self.get_logger().info(
            "Requesting Nav2 return to dock approach "
            f"({self._dock_approach.x}, {self._dock_approach.y}, "
            f"{self._dock_approach.yaw})"
        )
        try:
            future = self._nav_client.send_goal_async(
                self._navigation_goal(self._dock_approach)
            )
        except Exception as exc:
            self._complete_return_to_dock(
                False, f"could not send return-to-dock goal: {exc}"
            )
            return
        future.add_done_callback(self._return_goal_response)

    def _return_goal_response(self, future) -> None:
        if self._phase() != MissionPhase.RETURNING_TO_DOCK:
            return
        try:
            goal_handle = future.result()
        except Exception as exc:
            self._complete_return_to_dock(
                False, f"return-to-dock goal failed: {exc}"
            )
            return
        if not goal_handle.accepted:
            self._complete_return_to_dock(False, "Nav2 rejected return-to-dock goal")
            return
        self._return_goal_handle = goal_handle
        self.get_logger().info("Nav2 accepted return-to-dock approach")
        goal_handle.get_result_async().add_done_callback(self._return_result)

    def _return_result(self, future) -> None:
        if self._phase() != MissionPhase.RETURNING_TO_DOCK:
            return
        try:
            wrapped = future.result()
            succeeded = wrapped.status == GoalStatus.STATUS_SUCCEEDED
            reason = f"Return-to-dock Nav2 ended with status={wrapped.status}"
        except Exception as exc:
            succeeded = False
            reason = f"Return-to-dock Nav2 result failed: {exc}"
        self._complete_return_to_dock(succeeded, reason)

    def _complete_return_to_dock(self, succeeded: bool, failure_reason: str) -> None:
        self._return_goal_handle = None
        transitioned = self._transition(
            self._mission.return_to_dock_completed,
            succeeded=succeeded,
            has_pending=not self._pending.empty(),
        )
        if transitioned:
            self.get_logger().info("Nav2 completed return-to-dock approach")
        else:
            self._fail_mission(failure_reason)

    def _navigation_goal(self, pose: PoseTarget) -> NavigateToPose.Goal:
        goal = NavigateToPose.Goal()
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.header.frame_id = self._map_frame
        goal.pose.pose.position.x = pose.x
        goal.pose.pose.position.y = pose.y
        goal.pose.pose.orientation.z = math.sin(pose.yaw / 2.0)
        goal.pose.pose.orientation.w = math.cos(pose.yaw / 2.0)
        return goal

    def _start_dock(self) -> None:
        if monotonic() < self._next_dock_attempt_at:
            return
        if self._latest_is_docked is True and self._dock_status_is_stable():
            if self._transition(self._mission.begin_docking):
                self._complete_dock_from_state("robot already docked")
            return
        if not self._dock_client.server_is_ready():
            self._fail_if_phase_expired("dock action server")
            return
        if not self._transition(self._mission.begin_docking):
            return
        self._dock_attempts += 1
        self.get_logger().info("Requesting dock after navigation queue completed")
        try:
            future = self._dock_client.send_goal_async(Dock.Goal())
        except Exception as exc:
            self._fail_mission(f"could not send dock goal: {exc}")
            return
        future.add_done_callback(self._dock_goal_response)

    def _dock_goal_response(self, future) -> None:
        if self._phase() != MissionPhase.DOCKING:
            return
        try:
            goal_handle = future.result()
        except Exception as exc:
            self._fail_mission(f"dock goal failed: {exc}")
            return
        if not goal_handle.accepted:
            self._retry_dock_or_accept_state()
            return
        self._dock_goal_handle = goal_handle
        self.get_logger().info("Dock goal accepted")
        goal_handle.get_result_async().add_done_callback(self._dock_result)

    def _dock_result(self, future) -> None:
        if self._phase() != MissionPhase.DOCKING:
            return
        try:
            wrapped = future.result()
            is_docked = bool(wrapped.result.is_docked)
            succeeded = wrapped.status == GoalStatus.STATUS_SUCCEEDED or is_docked
        except Exception as exc:
            self._fail_mission(f"dock result failed: {exc}")
            return
        if self._transition(
            self._mission.docking_completed,
            succeeded=succeeded,
            is_docked=is_docked,
            has_pending=not self._pending.empty(),
        ):
            self._dock_goal_handle = None
            self._dock_attempts = 0
            self.get_logger().info("Dock completed: robot is docked")
        else:
            self._fail_mission(
                f"dock ended with status={wrapped.status}, is_docked={is_docked}"
            )

    def _dock_status_received(self, message: DockStatus) -> None:
        value = bool(message.is_docked)
        if value != self._latest_is_docked:
            self._latest_is_docked = value
            self._dock_status_changed_at = monotonic()

    def _dock_status_is_stable(self) -> bool:
        return (
            self._latest_is_docked is not None
            and monotonic() - self._dock_status_changed_at >= 1.0
        )

    def _retry_undock_or_accept_state(self) -> None:
        if self._latest_is_docked is False:
            self._complete_undock_from_state("action rejected after robot became clear")
            return
        if self._undock_attempts < self._action_retry_limit:
            if self._transition(self._mission.retry_undock):
                self._next_undock_attempt_at = monotonic() + 2.0
                self.get_logger().warning(
                    "Undock goal rejected during startup; retrying after dock status settles"
                )
                return
        self._fail_mission("undock goal was rejected after bounded retries")

    def _complete_undock_from_state(self, reason: str) -> None:
        if self._transition(
            self._mission.undock_completed,
            succeeded=True,
            is_docked=False,
        ):
            self._undock_goal_handle = None
            self._undock_attempts = 0
            self.get_logger().info(
                f"Undock completed: robot is clear of dock ({reason})"
            )
            return
        self._fail_mission("could not record confirmed undocked state")

    def _retry_dock_or_accept_state(self) -> None:
        if self._latest_is_docked is True:
            self._complete_dock_from_state("action rejected after robot became docked")
            return
        if self._dock_attempts < self._action_retry_limit:
            if self._transition(self._mission.retry_docking):
                self._next_dock_attempt_at = monotonic() + 2.0
                self.get_logger().warning(
                    "Dock goal rejected while robot was not docked; retrying"
                )
                return
        self._fail_mission("dock goal was rejected after bounded retries")

    def _complete_dock_from_state(self, reason: str) -> None:
        if self._transition(
            self._mission.docking_completed,
            succeeded=True,
            is_docked=True,
            has_pending=not self._pending.empty(),
        ):
            self._dock_goal_handle = None
            self._dock_attempts = 0
            self.get_logger().info(f"Dock completed: robot is docked ({reason})")
            return
        self._fail_mission("could not record confirmed docked state")

    def _nav_is_active(self) -> bool:
        if self._nav_active:
            return True
        if self._nav_state_future is not None:
            if not self._nav_state_future.done():
                return False
            try:
                state = self._nav_state_future.result().current_state
                self._nav_active = state.id == 3  # lifecycle_msgs/State: ACTIVE
            except Exception as exc:
                self.get_logger().warning(f"Could not read Nav2 lifecycle state: {exc}")
            finally:
                self._nav_state_future = None
            return self._nav_active
        if self._nav_state_client.service_is_ready():
            self._nav_state_future = self._nav_state_client.call_async(GetState.Request())
        return False

    def _check_action_timeout(self, label: str, goal_handle) -> None:
        if self._phase_elapsed() <= self._dock_action_timeout_s:
            return
        if goal_handle is not None:
            goal_handle.cancel_goal_async()
        self._fail_mission(f"{label} timed out")

    def _monitor_undock(self) -> None:
        if self._latest_is_docked is False and self._dock_status_is_stable():
            if self._undock_goal_handle is not None:
                self._undock_goal_handle.cancel_goal_async()
            self._complete_undock_from_state("dock status confirmed clear")
            return
        self._check_action_timeout("undock", self._undock_goal_handle)

    def _monitor_dock(self) -> None:
        if self._latest_is_docked is True and self._dock_status_is_stable():
            if self._dock_goal_handle is not None:
                self._dock_goal_handle.cancel_goal_async()
            self._complete_dock_from_state("dock status confirmed docked")
            return
        self._check_action_timeout("dock", self._dock_goal_handle)

    def _check_navigation_timeout(self) -> None:
        if self._phase_elapsed() <= self._navigation_timeout_s:
            return
        if self._nav_goal_handle is not None:
            self._nav_goal_handle.cancel_goal_async()
        self._complete_navigation(False, "navigation timed out")

    def _check_return_to_dock_timeout(self) -> None:
        if self._phase_elapsed() <= self._navigation_timeout_s:
            return
        if self._return_goal_handle is not None:
            self._return_goal_handle.cancel_goal_async()
        self._complete_return_to_dock(False, "return-to-dock navigation timed out")

    def _fail_if_navigation_phase_expired(self, dependency: str) -> None:
        if self._phase_elapsed() > self._navigation_timeout_s:
            self._fail_mission(f"{dependency} was not ready before timeout")

    def _fail_if_phase_expired(self, dependency: str) -> None:
        if self._phase_elapsed() > self._dock_action_timeout_s:
            self._fail_mission(f"{dependency} was not ready before timeout")

    def _fail_mission(self, reason: str) -> None:
        if self._phase() != MissionPhase.FAILED:
            self._transition(self._mission.fail, reason)
        self.get_logger().error(f"Mission lifecycle failed closed: {reason}")

    def _current_navigation(self) -> tuple[PoseTarget, str]:
        if self._active_navigation is None:
            raise RuntimeError("navigation callback without an active goal")
        return self._active_navigation

    def _phase(self) -> MissionPhase:
        with self._mission_lock:
            return self._mission.phase

    def _phase_elapsed(self) -> float:
        with self._mission_lock:
            return self._clock_seconds() - self._phase_started_at

    def _transition(self, operation, *args, **kwargs):
        with self._mission_lock:
            previous = self._mission.phase
            result = operation(*args, **kwargs)
            self._record_phase_change(previous)
            return result

    def _record_phase_change(self, previous: MissionPhase) -> None:
        if self._mission.phase != previous:
            self._phase_started_at = self._clock_seconds()

    def _clock_seconds(self) -> float:
        return self.get_clock().now().nanoseconds / 1_000_000_000.0


def main(args=None) -> None:
    rclpy.init(args=args)
    node = MaestroBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        # ROS may already have shut the context down after SIGINT/SIGTERM.
        # Calling shutdown twice raises RCLError and makes a normal container
        # stop look like a bridge failure.
        if rclpy.ok():
            rclpy.shutdown()
