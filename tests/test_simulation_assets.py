import json
import math
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = (
    ROOT
    / "robot_ws"
    / "src"
    / "maestro_simulation"
    / "models"
    / "plot_marker"
    / "model.sdf"
)
TEXTURE_DIR = MODEL_PATH.parent / "materials" / "textures"
TARGETS_PATH = (
    ROOT
    / "robot_ws"
    / "src"
    / "maestro_robot_bridge"
    / "config"
    / "targets.json"
)
LAUNCH_PATH = (
    ROOT
    / "robot_ws"
    / "src"
    / "maestro_simulation"
    / "launch"
    / "demo.launch.py"
)
COMPOSE_PATH = ROOT / "compose.yaml"
LOCALIZATION_PATH = (
    ROOT
    / "robot_ws"
    / "src"
    / "maestro_simulation"
    / "config"
    / "localization.yaml"
)
NAV2_PATH = (
    ROOT
    / "robot_ws"
    / "src"
    / "maestro_simulation"
    / "config"
    / "nav2.yaml"
)


def numbers(element):
    return [float(value) for value in element.text.split()]


def rotated_axes(roll, pitch, yaw):
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    matrix = (
        (cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr),
        (sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr),
        (-sp, cp * sr, cp * cr),
    )
    return tuple(tuple(row[column] for row in matrix) for column in range(3))


class SimulationAssetsTest(unittest.TestCase):
    def setUp(self):
        self.model = ET.parse(MODEL_PATH).getroot().find("model")
        self.targets = json.loads(TARGETS_PATH.read_text(encoding="utf-8"))["targets"]

    def test_distributed_plots_have_matching_textures_and_safe_targets(self):
        expected = {
            "plot-01": ((2.2, -1.8, math.pi / 2), (2.2, -2.3, math.pi / 2)),
            "plot-02": ((0.5, 1.8, -math.pi / 2), (0.5, 2.3, -math.pi / 2)),
            "plot-03": ((2.0, 1.0, 0.0), (1.5, 1.0, 0.0)),
        }
        self.assertEqual(set(expected), set(self.targets))
        links = {link.attrib["name"]: link for link in self.model.findall("link")}
        expected_links = {
            value.replace("-", "_") + "_marker" for value in expected
        }
        self.assertEqual(expected_links, set(links))

        for plot_id, (marker, target) in expected.items():
            with self.subTest(plot_id=plot_id):
                link = links[plot_id.replace("-", "_") + "_marker"]
                pose = numbers(link.find("pose"))
                self.assertEqual([marker[0], marker[1], 0.6, 0.0, 0.0], pose[:5])
                self.assertAlmostEqual(marker[2], pose[5], places=5)
                texture = link.find(
                    "visual[@name='qr_visual']/material/pbr/metal/albedo_map"
                )
                self.assertTrue(texture.text.endswith(f"/{plot_id}.png"))
                self.assertTrue((TEXTURE_DIR / f"{plot_id}.png").is_file())
                actual_target = self.targets[plot_id]
                self.assertEqual(target[0], actual_target["x"])
                self.assertEqual(target[1], actual_target["y"])
                self.assertAlmostEqual(target[2], actual_target["yaw"], places=5)
                distance = math.hypot(
                    marker[0] - actual_target["x"],
                    marker[1] - actual_target["y"],
                )
                self.assertAlmostEqual(0.5, distance, places=5)
                heading_to_marker = math.atan2(
                    marker[1] - actual_target["y"],
                    marker[0] - actual_target["x"],
                )
                self.assertAlmostEqual(heading_to_marker, actual_target["yaw"], places=5)

    def test_qr_plane_is_vertical_and_outside_front_face(self):
        for link in self.model.findall("link"):
            with self.subTest(link=link.attrib["name"]):
                board_size = numbers(
                    link.find(
                        "collision[@name='board_collision']/geometry/box/size"
                    )
                )
                qr_pose = numbers(link.find("visual[@name='qr_visual']/pose"))
                local_x, local_y, normal = rotated_axes(*qr_pose[3:])

                self.assertLess(qr_pose[0], -board_size[0] / 2.0)
                for actual, expected in zip(local_x, (0.0, -1.0, 0.0)):
                    self.assertAlmostEqual(expected, actual, places=5)
                for actual, expected in zip(local_y, (0.0, 0.0, 1.0)):
                    self.assertAlmostEqual(expected, actual, places=5)
                for actual, expected in zip(normal, (-1.0, 0.0, 0.0)):
                    self.assertAlmostEqual(expected, actual, places=5)

    def test_bridge_safety_limits_use_simulation_clock(self):
        launch = LAUNCH_PATH.read_text(encoding="utf-8")
        self.assertIn('"use_sim_time": True', launch)

    def test_saved_map_localization_starts_from_dock_pose(self):
        launch = LAUNCH_PATH.read_text(encoding="utf-8")
        localization = LOCALIZATION_PATH.read_text(encoding="utf-8")

        self.assertIn('"localization.launch.py"', launch)
        self.assertNotIn('"slam.launch.py"', launch)
        self.assertIn("set_initial_pose: true", localization)
        self.assertIn("x: 0.0", localization)
        self.assertIn("y: 0.0", localization)
        self.assertIn("yaw: 0.0", localization)

    def test_progress_checker_allows_slow_create3_maneuvers(self):
        nav2 = NAV2_PATH.read_text(encoding="utf-8")

        self.assertIn("required_movement_radius: 0.1", nav2)
        self.assertIn("movement_time_allowance: 30.0", nav2)

    def test_headless_launch_avoids_hidden_gui_and_preserves_model_choice(self):
        launch = LAUNCH_PATH.read_text(encoding="utf-8")
        compose = COMPOSE_PATH.read_text(encoding="utf-8")

        self.assertIn('"ros_gz_sim"', launch)
        self.assertIn('"gz_sim.launch.py"', launch)
        self.assertIn('"turtlebot4_spawn.launch.py"', launch)
        self.assertIn('str(simulation_share / "models")', launch)
        self.assertNotIn('"turtlebot4_ignition.launch.py"', launch)
        self.assertIn('gz_args += " -s"', launch)
        self.assertNotIn("--headless-rendering", launch)
        self.assertEqual(
            3,
            compose.count("model:=${TURTLEBOT4_MODEL:-standard}"),
        )
        self.assertNotIn("MAESTRO_HEADLESS_MODEL", compose)
        gpu_service = compose.split("  simulation-gpu:", 1)[1]
        self.assertIn('MAESTRO_HEADLESS: "0"', gpu_service)
        self.assertIn("/tmp/.X11-unix:/tmp/.X11-unix:rw", gpu_service)


if __name__ == "__main__":
    unittest.main()
