FROM osrf/ros:humble-desktop AS runtime

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    ignition-fortress \
    libgl1-mesa-dri \
    python3-colcon-common-extensions \
    python3-pip \
    ros-humble-gz-ros2-control \
    ros-humble-irobot-create-nodes \
    ros-humble-nav2-bringup \
    ros-humble-nav2-msgs \
    ros-humble-rmw-cyclonedds-cpp \
    ros-humble-ros-gz \
    ros-humble-rviz2 \
    ros-humble-slam-toolbox \
    ros-humble-turtlebot4-description \
    ros-humble-turtlebot4-navigation \
    ros-humble-turtlebot4-simulator \
    ros-humble-turtlebot4-viz \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir "websockets>=14,<16"

WORKDIR /opt/maestro_ws
COPY robot_ws/src ./src

RUN . /opt/ros/humble/setup.sh \
    && colcon build --symlink-install

COPY --chmod=755 docker/entrypoint.sh /maestro-entrypoint.sh

ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp \
    TURTLEBOT4_MODEL=standard \
    IGN_VERSION=fortress \
    IGNITION_VERSION=fortress

ENTRYPOINT ["/maestro-entrypoint.sh"]
CMD ["ros2", "launch", "maestro_simulation", "demo.launch.py"]
