import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).parents[1]
MODULE_PATH = ROOT / "tools" / "qr_target_detector.py"
SPEC = importlib.util.spec_from_file_location("qr_target_detector", MODULE_PATH)
assert SPEC and SPEC.loader
detector = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = detector
SPEC.loader.exec_module(detector)

try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None
    np = None


CAPTURED_AT = "2026-08-18T12:00:00.000Z"


class SelectionRulesTest(unittest.TestCase):
    def test_unknown_id_is_never_promoted_to_target(self):
        result = detector.select_target(
            [detector.QrCandidate("plot-99", 0.5, 0.5)], {"plot-03"}, CAPTURED_AT
        )
        self.assertEqual("UNKNOWN", result.status)
        self.assertIsNone(result.target_id)
        self.assertEqual(0.0, result.confidence)

    def test_multiple_central_qrs_are_ambiguous(self):
        result = detector.select_target(
            [
                detector.QrCandidate("plot-03", 0.4, 0.5),
                detector.QrCandidate("plot-04", 0.6, 0.5),
            ],
            {"plot-03", "plot-04"},
            CAPTURED_AT,
        )
        self.assertEqual("AMBIGUOUS", result.status)
        self.assertIsNone(result.target_id)
        self.assertEqual(2, result.candidate_count)

    def test_peripheral_qr_is_ignored(self):
        result = detector.select_target(
            [detector.QrCandidate("plot-03", 0.05, 0.5)], {"plot-03"}, CAPTURED_AT
        )
        self.assertEqual("UNKNOWN", result.status)
        self.assertEqual(0, result.candidate_count)

    def test_timestamp_requires_timezone(self):
        with self.assertRaises(ValueError):
            detector.normalize_timestamp("2026-08-18T12:00:00")


@unittest.skipUnless(cv2 is not None and np is not None, "OpenCV não disponível")
class StaticImageTest(unittest.TestCase):
    @staticmethod
    def qr_canvas(value):
        encoder = cv2.QRCodeEncoder_create()
        qr = encoder.encode(value)
        qr = cv2.resize(qr, (240, 240), interpolation=cv2.INTER_NEAREST)
        canvas = np.full((400, 400), 255, dtype=np.uint8)
        canvas[80:320, 80:320] = qr
        return canvas

    def test_versioned_plot_texture_is_detected(self):
        image_path = (
            ROOT
            / "robot_ws"
            / "src"
            / "maestro_simulation"
            / "models"
            / "plot_marker"
            / "materials"
            / "textures"
            / "plot-03.png"
        )
        image = cv2.imread(str(image_path))
        self.assertGreater(image.shape[0], image.shape[1], "a placa deve ser vertical e conter o ID legível")
        result = detector.detect_image(image, {"plot-03"}, CAPTURED_AT, cv2_module=cv2)
        self.assertEqual("DETECTED", result.status)
        self.assertEqual("plot-03", result.target_id)
        self.assertEqual(1.0, result.confidence)

    def test_blank_image_is_unknown(self):
        image = np.full((320, 320, 3), 255, dtype=np.uint8)
        result = detector.detect_image(image, {"plot-03"}, CAPTURED_AT, cv2_module=cv2)
        self.assertEqual("UNKNOWN", result.status)
        self.assertIsNone(result.target_id)

    def test_decoded_but_unmapped_qr_is_unknown(self):
        result = detector.detect_image(
            self.qr_canvas("plot-99"), {"plot-03"}, CAPTURED_AT, cv2_module=cv2
        )
        self.assertEqual("UNKNOWN", result.status)
        self.assertIsNone(result.target_id)

    def test_two_decoded_qrs_are_ambiguous(self):
        encoder = cv2.QRCodeEncoder_create()
        first = cv2.resize(encoder.encode("plot-03"), (200, 200), interpolation=cv2.INTER_NEAREST)
        second = cv2.resize(encoder.encode("plot-04"), (200, 200), interpolation=cv2.INTER_NEAREST)
        canvas = np.full((360, 600), 255, dtype=np.uint8)
        canvas[80:280, 40:240] = first
        canvas[80:280, 360:560] = second

        result = detector.detect_image(
            canvas, {"plot-03", "plot-04"}, CAPTURED_AT, cv2_module=cv2
        )
        self.assertEqual("AMBIGUOUS", result.status)
        self.assertEqual(2, result.candidate_count)


if __name__ == "__main__":
    unittest.main()
