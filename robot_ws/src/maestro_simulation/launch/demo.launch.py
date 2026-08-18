from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    EmitEvent,
    IncludeLaunchDescription,
    LogInfo,
    OpaqueFunction,
    RegisterEventHandler,
    SetLaunchConfiguration,
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


def configure_gazebo(context):
    world = LaunchConfiguration("world").perform(context)
    model = LaunchConfiguration("model").perform(context)
    headless = LaunchConfiguration("headless").perform(context).lower() == "true"
    gz_args = f"{world}.sdf -r -v 4"
    if headless:
        gz_args += " -s --headless-rendering"
    else:
        bringup_share = Path(
            get_package_share_directory("turtlebot4_ignition_bringup")
        )
        gui_config = bringup_share / "gui" / model / "gui.config"
        gz_args += f" --gui-config {gui_config}"
    return [SetLaunchConfiguration("gz_args", gz_args)]


def generate_launch_description() -> LaunchDescription:
    namespace = LaunchConfiguration("namespace")
    world = LaunchConfiguration("world")
    model = LaunchConfiguration("model")
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
        {"namespace": namespace, "world": world, "model": model},
    )
    spawn_marker = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-world", world,
            "-name", "plot_markers",
            "-file", str(marker_model),
            "-x", "2.0",
            "-y", "0.0",
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
        DeclareLaunchArgument("model", default_value="standard"),
        DeclareLaunchArgument("headless", default_value="true"),
        DeclareLaunchArgument("gz_args", default_value=""),
        DeclareLaunchArgument("websocket_port", default_value="18765"),
        OpaqueFunction(function=configure_gazebo),
        gazebo,
        controller_guard,
        navigation_gate,
        bridge,
    ])
