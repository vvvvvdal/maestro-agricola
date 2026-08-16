from glob import glob
from setuptools import find_packages, setup


package_name = "maestro_robot_bridge"


setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=("test",)),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/config", glob("config/*.json")),
        (f"share/{package_name}/launch", glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools", "websockets>=14,<16"],
    zip_safe=True,
    maintainer="AgroTurtles",
    maintainer_email="agroturtles@example.invalid",
    description="Validated WebSocket to ROS 2 Nav2 bridge for Maestro Agricola.",
    license="Apache-2.0",
    entry_points={
        "console_scripts": [
            "bridge_node = maestro_robot_bridge.bridge_node:main",
        ],
    },
)
