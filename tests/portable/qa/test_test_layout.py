from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
PORTABLE = ROOT / "tests" / "portable"


class TestLayoutTest(unittest.TestCase):
    def test_portable_tests_are_grouped_by_domain(self) -> None:
        expected_domains = {"ai", "android", "robotics", "qa"}
        actual_domains = {
            path.name
            for path in PORTABLE.iterdir()
            if path.is_dir() and not path.name.startswith("__")
        }

        self.assertEqual(expected_domains, actual_domains)
        self.assertEqual([], list((ROOT / "tests").glob("test_*.py")))
        for domain in expected_domains:
            with self.subTest(domain=domain):
                self.assertTrue(list((PORTABLE / domain).glob("test_*.py")))

    def test_framework_owned_tests_remain_colocated(self) -> None:
        android_tests = list(
            (ROOT / "mobile" / "android" / "app" / "src" / "test").rglob("*Test.kt")
        )
        ros_tests = list(
            (ROOT / "robot_ws" / "src" / "maestro_robot_bridge" / "test").glob(
                "test_*.py"
            )
        )

        self.assertTrue(android_tests)
        self.assertTrue(ros_tests)

    def test_automation_uses_the_portable_discovery_root(self) -> None:
        expected = "-s tests/portable -t . -p 'test_*.py'"
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        workflow = (ROOT / ".github" / "workflows" / "ci-quick.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn(expected, makefile)
        self.assertIn(expected, workflow)
        self.assertNotIn("-s tests -p 'test_*.py'", makefile)
        self.assertNotIn("-s tests -p 'test_*.py'", workflow)


if __name__ == "__main__":
    unittest.main()
