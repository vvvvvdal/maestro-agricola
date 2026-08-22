import os
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
    SetEnvironmentVariable,
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
    headless = LaunchConfiguration("headless").perform(context).lower() == "true"
    gz_args = f"{world}.sdf -r -v 4"
    if headless:
        # TurtleBot 4 Fortress sensors use OGRE 1. Keep Xvfb as their display,
        # but omit the Gazebo GUI process itself.
        gz_args += " -s"
    else:
        simulation_share = Path(
            get_package_share_directory("maestro_simulation")
        )
        gui_config = simulation_share / "config" / "gui.config"
        gz_args += f" --gui-config {gui_config}"
    return [SetLaunchConfiguration("gz_args", gz_args)]


def generate_launch_description() -> LaunchDescription:
    namespace = LaunchConfiguration("namespace")
    world = LaunchConfiguration("world")
    model = LaunchConfiguration("model")
    websocket_port = LaunchConfiguration("websocket_port")
    simulation_share = Path(get_package_share_directory("maestro_simulation"))
    marker_model = simulation_share / "models" / "plot_marker" / "model.sdf"
    localization_params = simulation_share / "config" / "localization.yaml"
    nav2_params = simulation_share / "config" / "nav2.yaml"
    robot_namespace = PythonExpression(["'/' + '", namespace, "'"])
    controller_manager = PythonExpression(
        ["'/' + '", namespace, "' + '/controller_manager'"]
    )

    turtlebot_bringup = Path(
        get_package_share_directory("turtlebot4_ignition_bringup")
    )
    turtlebot_description = Path(
        get_package_share_directory("turtlebot4_description")
    )
    create_bringup = Path(
        get_package_share_directory("irobot_create_ignition_bringup")
    )
    create_description = Path(
        get_package_share_directory("irobot_create_description")
    )
    resource_path = os.pathsep.join([
        str(simulation_share / "models"),
        str(turtlebot_bringup / "worlds"),
        str(create_bringup / "worlds"),
        str(turtlebot_description.parent),
        str(create_description.parent),
    ])
    plugin_path = os.pathsep.join([
        str(
            Path(get_package_share_directory("turtlebot4_ignition_gui_plugins"))
            / "lib"
        ),
        str(
            Path(get_package_share_directory("irobot_create_ignition_plugins"))
            / "lib"
        ),
    ])
    gazebo = include(
        "ros_gz_sim",
        "gz_sim.launch.py",
        {
            "gz_args": LaunchConfiguration("gz_args"),
            "on_exit_shutdown": "true",
        },
    )
    robot_spawn = include(
        "turtlebot4_ignition_bringup",
        "turtlebot4_spawn.launch.py",
        {
            "namespace": namespace,
            "model": model,
            "rviz": "false",
            "use_sim_time": "true",
        },
    )
    clock_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="clock_bridge",
        output="screen",
        arguments=["/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock"],
    )
    spawn_marker = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-world", world,
            "-name", "plot_markers",
            "-file", str(marker_model),
            "-x", "0.0",
            "-y", "0.0",
            "-z", "0.0",
        ],
        output="screen",
    )
    localization = include(
        "turtlebot4_navigation",
        "localization.launch.py",
        {
            "namespace": namespace,
            "params": str(localization_params),
            "use_sim_time": "true",
        },
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
                "use_sim_time": True,
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
            localization,
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
        SetEnvironmentVariable("IGN_GAZEBO_RESOURCE_PATH", resource_path),
        SetEnvironmentVariable("GZ_SIM_RESOURCE_PATH", resource_path),
        SetEnvironmentVariable("IGN_GUI_PLUGIN_PATH", plugin_path),
        OpaqueFunction(function=configure_gazebo),
        gazebo,
        clock_bridge,
        robot_spawn,
        controller_guard,
        navigation_gate,
        bridge,
    ])
