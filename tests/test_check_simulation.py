import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import check_simulation  # noqa: E402


class SimulationCheckTest(unittest.TestCase):
    def test_odom_timeout_is_retryable(self):
        timeout = subprocess.TimeoutExpired(["docker", "compose", "exec"], 12)
        with patch.object(check_simulation, "container_shell", side_effect=timeout):
            self.assertIsNone(check_simulation.read_odom())

    def test_odom_position_is_parsed(self):
        output = """pose:
  pose:
    position:
      x: 0.022
      y: 0.001
      z: 0.0
"""
        completed = subprocess.CompletedProcess([], 0, output, "")
        with patch.object(check_simulation, "container_shell", return_value=completed):
            self.assertEqual((0.022, 0.001), check_simulation.read_odom())


if __name__ == "__main__":
    unittest.main()
