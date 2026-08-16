from __future__ import annotations

import subprocess

import rclpy
from ament_index_python.packages import get_package_share_directory
from controller_manager_msgs.srv import ListControllers
from rclpy.node import Node


class ControllerGuard(Node):
    """Recover a controller left unconfigured by a slow simulator startup."""

    def __init__(self) -> None:
        super().__init__("maestro_controller_guard")
        self.declare_parameter("controller_manager", "/turtlebot1/controller_manager")
        self.declare_parameter("controller_name", "diffdrive_controller")

    def ensure_active(self) -> int:
        manager = str(self.get_parameter("controller_manager").value).rstrip("/")
        name = str(self.get_parameter("controller_name").value)
        client = self.create_client(ListControllers, f"{manager}/list_controllers")
        if not client.wait_for_service(timeout_sec=60.0):
            self.get_logger().error(f"Controller manager unavailable: {manager}")
            return 1

        future = client.call_async(ListControllers.Request())
        rclpy.spin_until_future_complete(self, future, timeout_sec=15.0)
        if not future.done() or future.result() is None:
            self.get_logger().error("Could not read controller state")
            return 1

        states = {controller.name: controller.state for controller in future.result().controller}
        if states.get(name) == "active":
            self.get_logger().info(f"Controller already active: {name}")
            return 0

        params = (
            get_package_share_directory("irobot_create_control")
            + "/config/control.yaml"
        )
        self.get_logger().warning(
            f"Recovering controller {name} from state {states.get(name, 'not_loaded')}"
        )
        command = [
            "/opt/ros/humble/lib/controller_manager/spawner",
            name,
            "-c",
            manager,
            "-p",
            params,
            "--controller-manager-timeout",
            "60",
            "--service-call-timeout",
            "60",
        ]
        return subprocess.run(command, check=False).returncode


def main(args=None) -> None:
    rclpy.init(args=args)
    node = ControllerGuard()
    try:
        exit_code = node.ensure_active()
    finally:
        node.destroy_node()
        rclpy.shutdown()
    if exit_code:
        raise SystemExit(exit_code)
