"""Unit tests for EmergencyStopManager module."""

import time
import unittest
from uamc.safety.emergency_stop import EmergencyStopManager


class TestEmergencyStop(unittest.TestCase):
    def setUp(self):
        self.safety = EmergencyStopManager(heartbeat_timeout_s=0.10)

    def test_nominal_safety(self):
        self.safety.ping()
        status = self.safety.evaluate()
        self.assertTrue(status.is_safe)
        self.assertFalse(status.estop_active)

    def test_manual_estop_activation(self):
        self.safety.trigger_estop("Test Kill Switch")
        status = self.safety.evaluate()
        self.assertFalse(status.is_safe)
        self.assertTrue(status.estop_active)

    def test_heartbeat_timeout(self):
        self.safety.ping()
        time.sleep(0.12)  # Wait beyond 100ms timeout
        status = self.safety.evaluate()
        self.assertFalse(status.is_safe)
        self.assertTrue(status.estop_active)
        self.assertIn("Timeout", status.reason)


if __name__ == "__main__":
    unittest.main()
