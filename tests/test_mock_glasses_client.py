import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from intent_model import IntentModel  # noqa: E402
from mock_glasses_client import build_command, connect_to_bridge  # noqa: E402


class MockGlassesClientTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = IntentModel.load(ROOT / "shared/ai/intent_model.json")

    def test_requires_explicit_confirmation(self):
        with self.assertRaisesRegex(ValueError, "confirmação recusada"):
            build_command(self.model, "plot-03", "pulverizar esta área", "cancelar")

    def test_builds_confirmed_command(self):
        payload = build_command(self.model, "plot-03", "pulverizar esta área", "confirmar")
        self.assertEqual("SPRAY", payload["intent"])
        self.assertTrue(payload["confirmed"])
        self.assertEqual("plot-03", payload["target"]["id"])

    def test_connection_error_explains_how_to_start_bridge(self):
        def unavailable_connector(*_args, **_kwargs):
            raise OSError("conexão recusada")

        with self.assertRaisesRegex(ConnectionError, "make demo"):
            connect_to_bridge(
                "ws://127.0.0.1:18765",
                wait_seconds=0,
                connector=unavailable_connector,
            )


if __name__ == "__main__":
    unittest.main()
