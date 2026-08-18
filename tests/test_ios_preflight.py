import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


MODULE_PATH = Path(__file__).parents[1] / "mobile" / "ios" / "tools" / "preflight.py"
SPEC = importlib.util.spec_from_file_location("ios_preflight", MODULE_PATH)
assert SPEC and SPEC.loader
preflight = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = preflight
SPEC.loader.exec_module(preflight)


class IosPreflightTest(unittest.TestCase):
    def test_parses_tool_versions(self):
        self.assertEqual((26, 4), preflight.parse_version("Xcode 26.4\nBuild version 1A2", r"Xcode\s+(\d+(?:\.\d+)+)"))
        self.assertEqual((6, 3), preflight.parse_version("Apple Swift version 6.3", r"Swift\s+(?:version\s+)?(\d+(?:\.\d+)+)"))
        self.assertEqual((2, 44, 1), preflight.parse_version("Version: 2.44.1", r"(?:Version:\s*)?(\d+(?:\.\d+)+)"))

    def test_compares_versions_with_missing_components(self):
        self.assertTrue(preflight.version_at_least((26, 4), (26, 4, 0)))
        self.assertTrue(preflight.version_at_least((6, 3, 1), (6, 3)))
        self.assertFalse(preflight.version_at_least((2, 43, 0), (2, 44, 1)))
        self.assertFalse(preflight.version_at_least(None, (1, 0)))

    def test_project_resources_must_exist_and_be_referenced(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ios = root / "mobile" / "ios"
            (ios / "MaestroAgricola").mkdir(parents=True)
            (root / "shared" / "ai").mkdir(parents=True)
            (ios / "MaestroAgricola" / "Info.plist").write_text("<plist/>", encoding="utf-8")
            (root / "shared" / "ai" / "intent_model.json").write_text("{}", encoding="utf-8")
            (ios / "project.yml").write_text(
                "- path: ../../shared/ai/intent_model.json\n", encoding="utf-8"
            )

            checks = preflight.project_checks(ios)
            self.assertTrue(all(check.ok for check in checks), checks)


if __name__ == "__main__":
    unittest.main()
