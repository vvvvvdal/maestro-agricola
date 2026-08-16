from __future__ import annotations

import math
from queue import Empty, Queue

import rclpy
from ament_index_python.packages import get_package_share_directory
from lifecycle_msgs.srv import GetState
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.node import Node

from .bridge_core import BridgeCore
from .models import PoseTarget
from .target_map import TargetMap
from .websocket_server import BridgeWebSocketServer


class MaestroBridgeNode(Node):
    def __init__(self) -> None:
        super().__init__("maestro_robot_bridge")
        share = get_package_share_directory("maestro_robot_bridge")
        self.declare_parameter("host", "0.0.0.0")
        self.declare_parameter("port", 8765)
        self.declare_parameter("robot_namespace", "/turtlebot1")
        self.declare_parameter("map_frame", "map")
        self.declare_parameter("targets_path", f"{share}/config/targets.json")

        namespace = str(self.get_parameter("robot_namespace").value).rstrip("/")
        self._map_frame = str(self.get_parameter("map_frame").value)
        self._pending: Queue[tuple[PoseTarget, str]] = Queue(maxsize=16)
        self._nav_client = ActionClient(self, NavigateToPose, f"{namespace}/navigate_to_pose")
        self._nav_state_client = self.create_client(
            GetState, f"{namespace}/bt_navigator/get_state"
        )
        self._nav_state_future = None
        self._nav_active = False
        target_map = TargetMap.load(str(self.get_parameter("targets_path").value))
        self._core = BridgeCore(target_map, self._queue_navigation)
        self._server = BridgeWebSocketServer(
            self._core,
            str(self.get_parameter("host").value),
            int(self.get_parameter("port").value),
        )
        self._server.start()
        self._timer = self.create_timer(0.1, self._drain_navigation_queue)
        self.get_logger().info(
            f"Maestro WebSocket listening on {self.get_parameter('host').value}:"
            f"{self.get_parameter('port').value}"
        )

    def destroy_node(self) -> bool:
        self._server.close()
        return super().destroy_node()

    def _queue_navigation(self, pose: PoseTarget, command_id: str) -> tuple[bool, str]:
        if self._pending.full():
            return False, "navigation queue is full"
        self._pending.put_nowait((pose, command_id))
        return True, "navigation goal queued"

    def _drain_navigation_queue(self) -> None:
        if not self._nav_is_active() or not self._nav_client.server_is_ready():
            return
        try:
            pose, command_id = self._pending.get_nowait()
        except Empty:
            return

        goal = NavigateToPose.Goal()
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.header.frame_id = self._map_frame
        goal.pose.pose.position.x = pose.x
        goal.pose.pose.position.y = pose.y
        goal.pose.pose.orientation.z = math.sin(pose.yaw / 2.0)
        goal.pose.pose.orientation.w = math.cos(pose.yaw / 2.0)
        future = self._nav_client.send_goal_async(goal)
        future.add_done_callback(lambda result: self._goal_response(command_id, result))

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

    def _goal_response(self, command_id: str, future) -> None:
        try:
            goal_handle = future.result()
        except Exception as exc:
            self.get_logger().error(f"Nav2 goal {command_id} failed: {exc}")
            return
        if goal_handle.accepted:
            self.get_logger().info(f"Nav2 accepted command {command_id}")
        else:
            self.get_logger().error(f"Nav2 rejected command {command_id}")


def main(args=None) -> None:
    rclpy.init(args=args)
    node = MaestroBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
