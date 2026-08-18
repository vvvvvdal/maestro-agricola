from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    EmitEvent,
    IncludeLaunchDescription,
    LogInfo,
    RegisterEventHandler,
    TimerAction,
)
from launch.event_handlers import OnProcessExit
from launch.events import Shutdown
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def include(package: str, launch_file: str, arguments: dict):
    source = Path(get_package_share_directory(package)) / "launch" / launch_file
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(source)),
        launch_arguments=arguments.items(),
    )


def generate_launch_description() -> LaunchDescription:
    namespace = LaunchConfiguration("namespace")
    world = LaunchConfiguration("world")
    websocket_port = LaunchConfiguration("websocket_port")
    simulation_share = Path(get_package_share_directory("maestro_simulation"))
    marker_model = simulation_share / "models" / "plot_marker" / "model.sdf"
    nav2_params = simulation_share / "config" / "nav2.yaml"
    robot_namespace = PythonExpression(["'/' + '", namespace, "'"])
    controller_manager = PythonExpression(
        ["'/' + '", namespace, "' + '/controller_manager'"]
    )

    gazebo = include(
        "turtlebot4_ignition_bringup",
        "turtlebot4_ignition.launch.py",
        {"namespace": namespace, "world": world},
    )
    spawn_marker = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-world", world,
            "-name", "plot_marker",
            "-file", str(marker_model),
            "-x", "2.0",
            "-y", "1.0",
            "-z", "0.0",
        ],
        output="screen",
    )
    slam = include(
        "turtlebot4_navigation",
        "slam.launch.py",
        {"namespace": namespace, "sync": "true"},
    )
    nav2 = include(
        "turtlebot4_navigation",
        "nav2.launch.py",
        {
            "namespace": namespace,
            "params_file": str(nav2_params),
            "cmd_vel": "cmd_vel_nav",
        },
    )
    controller_guard_node = Node(
        package="maestro_simulation",
        executable="controller_guard",
        output="screen",
        parameters=[{
            "controller_manager": controller_manager,
            "controller_name": "diffdrive_controller",
        }],
    )
    controller_guard = TimerAction(
        period=15.0,
        actions=[controller_guard_node],
    )
    bridge = TimerAction(
        period=15.0,
        actions=[Node(
            package="maestro_robot_bridge",
            executable="bridge_node",
            output="screen",
            parameters=[{
                "host": "0.0.0.0",
                "port": websocket_port,
                "robot_namespace": robot_namespace,
                "map_frame": "map",
            }],
        )],
    )

    def after_controller_guard(event, _context):
        if event.returncode != 0:
            reason = "TurtleBot controller did not become active"
            return [
                LogInfo(msg=f"ERROR: {reason}"),
                EmitEvent(event=Shutdown(reason=reason)),
            ]
        return [
            spawn_marker,
            slam,
            TimerAction(period=5.0, actions=[nav2]),
        ]

    navigation_gate = RegisterEventHandler(
        OnProcessExit(
            target_action=controller_guard_node,
            on_exit=after_controller_guard,
        )
    )

    return LaunchDescription([
        DeclareLaunchArgument("namespace", default_value="turtlebot1"),
        DeclareLaunchArgument("world", default_value="warehouse"),
        # ros_gz_sim prefers this global argument over the deprecated ign_args
        # used by TurtleBot 4's upstream launcher. Keep the world in the value:
        # passing only "-s -r" silently starts an empty world.
        DeclareLaunchArgument(
            "gz_args",
            default_value=[world, ".sdf -s -r --headless-rendering -v 4"],
        ),
        DeclareLaunchArgument("websocket_port", default_value="18765"),
        gazebo,
        controller_guard,
        navigation_gate,
        bridge,
    ])
