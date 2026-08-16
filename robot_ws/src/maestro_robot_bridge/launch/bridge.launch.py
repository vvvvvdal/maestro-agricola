from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription([
        DeclareLaunchArgument("host", default_value="0.0.0.0"),
        DeclareLaunchArgument("port", default_value="18765"),
        DeclareLaunchArgument("robot_namespace", default_value="/turtlebot1"),
        DeclareLaunchArgument("map_frame", default_value="map"),
        Node(
            package="maestro_robot_bridge",
            executable="bridge_node",
            name="maestro_robot_bridge",
            output="screen",
            parameters=[{
                "host": LaunchConfiguration("host"),
                "port": LaunchConfiguration("port"),
                "robot_namespace": LaunchConfiguration("robot_namespace"),
                "map_frame": LaunchConfiguration("map_frame"),
            }],
        ),
    ])
