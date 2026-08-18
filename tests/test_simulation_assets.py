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

    def test_three_nearby_plots_have_matching_textures_and_targets(self):
        expected = {"plot-01": -1.0, "plot-02": 0.0, "plot-03": 1.0}
        self.assertEqual(set(expected), set(self.targets))
        links = {link.attrib["name"]: link for link in self.model.findall("link")}
        expected_links = {
            value.replace("-", "_") + "_marker" for value in expected
        }
        self.assertEqual(expected_links, set(links))

        for plot_id, marker_y in expected.items():
            with self.subTest(plot_id=plot_id):
                link = links[plot_id.replace("-", "_") + "_marker"]
                self.assertEqual(
                    [0.0, marker_y, 0.6, 0.0, 0.0, 0.0],
                    numbers(link.find("pose")),
                )
                texture = link.find(
                    "visual[@name='qr_visual']/material/pbr/metal/albedo_map"
                )
                self.assertTrue(texture.text.endswith(f"/{plot_id}.png"))
                self.assertTrue((TEXTURE_DIR / f"{plot_id}.png").is_file())
                self.assertEqual(1.5, self.targets[plot_id]["x"])
                self.assertEqual(marker_y, self.targets[plot_id]["y"])

        ordered_y = [self.targets[plot_id]["y"] for plot_id in sorted(expected)]
        self.assertEqual(
            [1.0, 1.0],
            [b - a for a, b in zip(ordered_y, ordered_y[1:])],
        )

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


if __name__ == "__main__":
    unittest.main()
