import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


MODULE_PATH = Path(__file__).parents[1] / "mobile" / "android" / "tools" / "preflight.py"
SPEC = importlib.util.spec_from_file_location("android_preflight", MODULE_PATH)
assert SPEC and SPEC.loader
preflight = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = preflight
SPEC.loader.exec_module(preflight)


class AndroidPreflightTest(unittest.TestCase):
    def test_parses_supported_java_versions(self):
        self.assertEqual(17, preflight.parse_java_major('openjdk version "17.0.12" 2024-07-16'))
        self.assertEqual(21, preflight.parse_java_major('openjdk version "21" 2023-09-19'))
        self.assertEqual(8, preflight.parse_java_major('java version "1.8.0_412"'))
        self.assertIsNone(preflight.parse_java_major("unexpected output"))
        self.assertTrue(preflight.is_supported_java_major(21))
        self.assertFalse(preflight.is_supported_java_major(25))

    def test_reads_sdk_from_local_properties(self):
        with tempfile.TemporaryDirectory() as directory:
            properties = Path(directory) / "local.properties"
            properties.write_text("sdk.dir=/opt/android-sdk\n", encoding="utf-8")
            self.assertEqual(Path("/opt/android-sdk"), preflight.read_sdk_dir(properties))

    def test_parses_ready_and_blocked_adb_devices(self):
        devices = preflight.parse_adb_devices(
            "List of devices attached\nABC123\tdevice\nOLD456\tunauthorized\n\n"
        )
        self.assertEqual({"ABC123": "device", "OLD456": "unauthorized"}, devices)

    def test_explicit_paths_take_precedence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            java_home = root / "studio-jbr"
            sdk_dir = root / "android-sdk"
            (java_home / "bin").mkdir(parents=True)
            (java_home / "bin" / "java").touch()
            sdk_dir.mkdir()
            self.assertEqual(java_home / "bin" / "java", preflight.resolve_java(java_home))
            self.assertEqual(sdk_dir, preflight.resolve_sdk(root, sdk_dir))


if __name__ == "__main__":
    unittest.main()
