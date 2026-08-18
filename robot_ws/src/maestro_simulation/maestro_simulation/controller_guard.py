from __future__ import annotations

import subprocess
import time

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
        self.declare_parameter("upstream_wait_seconds", 45.0)
        self.declare_parameter("recovery_wait_seconds", 20.0)

    def _controller_state(self, client, name: str) -> str | None:
        future = client.call_async(ListControllers.Request())
        rclpy.spin_until_future_complete(self, future, timeout_sec=15.0)
        if not future.done():
            future.cancel()
            return None
        try:
            response = future.result()
        except Exception as error:
            self.get_logger().warning(f"Could not read controller state: {error}")
            return None
        if response is None:
            return None
        states = {controller.name: controller.state for controller in response.controller}
        return states.get(name, "not_loaded")

    def _wait_until_active(self, client, name: str, timeout_sec: float) -> bool:
        deadline = time.monotonic() + timeout_sec
        last_state = None
        while time.monotonic() < deadline:
            state = self._controller_state(client, name)
            if state == "active":
                self.get_logger().info(f"Controller active: {name}")
                return True
            if state != last_state:
                self.get_logger().info(
                    f"Waiting for upstream controller startup: {name}={state or 'unavailable'}"
                )
                last_state = state
            time.sleep(1.0)
        return False

    def ensure_active(self) -> int:
        manager = str(self.get_parameter("controller_manager").value).rstrip("/")
        name = str(self.get_parameter("controller_name").value)
        client = self.create_client(ListControllers, f"{manager}/list_controllers")
        if not client.wait_for_service(timeout_sec=180.0):
            self.get_logger().error(f"Controller manager unavailable: {manager}")
            return 1

        upstream_wait = float(self.get_parameter("upstream_wait_seconds").value)
        if self._wait_until_active(client, name, upstream_wait):
            return 0

        params = (
            get_package_share_directory("irobot_create_control")
            + "/config/control.yaml"
        )
        self.get_logger().warning(
            f"Upstream startup did not activate {name}; attempting recovery"
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
        recovery_result = subprocess.run(command, check=False).returncode
        recovery_wait = float(self.get_parameter("recovery_wait_seconds").value)
        if self._wait_until_active(client, name, recovery_wait):
            return 0
        self.get_logger().error(
            f"Controller recovery failed: {name} (spawner exit {recovery_result})"
        )
        return recovery_result or 1


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
