"""Unit tests for PurePursuitController and LongitudinalPIDController."""

import unittest
from uamc.control.pure_pursuit import PurePursuitController
from uamc.control.longitudinal_controller import LongitudinalPIDController


class TestControllers(unittest.TestCase):
    def setUp(self):
        self.lateral_ctrl = PurePursuitController(wheelbase_m=0.170, max_steering_angle_deg=28.0)
        self.longitudinal_ctrl = LongitudinalPIDController(kp=1.8, ki=0.45, kd=0.08)

    def test_pure_pursuit_centering(self):
        # Car is 5 cm to the left of lane center -> should steer right (positive steering)
        out = self.lateral_ctrl.compute_steering(
            lateral_offset_m=0.05,
            heading_error_rad=0.0,
            current_velocity_ms=0.45,
        )
        self.assertLess(out.steering_angle_deg, 0.0, "Car left of center should steer right")
        self.assertLessEqual(abs(out.steering_angle_deg), 28.0)

    def test_pure_pursuit_clamping(self):
        # Extreme offset should clamp to max steering angle (28 degrees)
        out = self.lateral_ctrl.compute_steering(
            lateral_offset_m=1.5,
            heading_error_rad=0.0,
            current_velocity_ms=0.45,
        )
        self.assertAlmostEqual(abs(out.steering_angle_deg), 28.0, delta=0.1)

    def test_longitudinal_acceleration(self):
        # Target speed 0.50 m/s when currently stopped -> positive throttle
        out = self.longitudinal_ctrl.compute_throttle(
            target_velocity_ms=0.50,
            measured_velocity_ms=0.0,
            dt=0.05,
        )
        self.assertGreater(out.throttle_pwm_normalized, 0.0)
        self.assertFalse(out.is_braking)

    def test_longitudinal_braking(self):
        # Commanded stop (0.0 m/s) when moving at 0.50 m/s -> active brake
        out = self.longitudinal_ctrl.compute_throttle(
            target_velocity_ms=0.0,
            measured_velocity_ms=0.50,
            dt=0.05,
        )
        self.assertTrue(out.is_braking)
        self.assertLess(out.throttle_pwm_normalized, 0.0)


if __name__ == "__main__":
    unittest.main()
