"""
Lateral Steering Controller: Pure Pursuit & Stanley Geometry.
Calculates target front-wheel steering angle based on vehicle wheelbase,
lookahead goal distance, and heading angle to path.
"""

import math
from dataclasses import dataclass
import numpy as np


@dataclass
class SteeringControlOutput:
    steering_angle_rad: float
    steering_angle_deg: float
    servo_pwm_normalized: float  # Normalized -1.0 (full left) to +1.0 (full right)


class PurePursuitController:
    """
    Pure Pursuit lateral controller for 1:10 scale Ackermann vehicle.
    """

    def __init__(
        self,
        wheelbase_m: float = 0.170,
        max_steering_angle_deg: float = 28.0,
        base_lookahead_m: float = 0.22,
        speed_lookahead_gain: float = 0.15,
        min_lookahead_m: float = 0.18,
        max_lookahead_m: float = 0.45,
    ):
        self.L = wheelbase_m
        self.max_steer_rad = math.radians(max_steering_angle_deg)
        self.l_d0 = base_lookahead_m
        self.k_look = speed_lookahead_gain
        self.min_ld = min_lookahead_m
        self.max_ld = max_lookahead_m

    def compute_steering(
        self,
        lateral_offset_m: float,
        heading_error_rad: float,
        current_velocity_ms: float,
        steering_bias: float = 0.0,
    ) -> SteeringControlOutput:
        """
        Computes the target steering angle.
        - lateral_offset_m: distance from vehicle center to lane center (positive = car is left of center, need to steer right)
        - heading_error_rad: angular deviation from lane tangent
        """
        # Dynamic lookahead distance based on current speed
        l_d = self.l_d0 + self.k_look * abs(current_velocity_ms)
        l_d = float(np.clip(l_d, self.min_ld, self.max_ld))

        # Vector to lookahead point on lane center line
        # In vehicle coordinates: forward is +y, right is +x
        # Goal point x_g = lateral_offset + l_d * sin(heading_error)
        # alpha is angle from vehicle heading (+y) to goal point
        goal_x = -lateral_offset_m + l_d * math.sin(heading_error_rad)
        goal_y = l_d * math.cos(heading_error_rad)

        alpha = math.atan2(goal_x, goal_y)

        # Pure pursuit formula: delta = atan2(2 * L * sin(alpha), l_d)
        delta = math.atan2(2.0 * self.L * math.sin(alpha), l_d)

        # Apply external bias (e.g. from obstacle evasion)
        delta += steering_bias

        # Clamp to physical steering limits
        delta_clamped = float(np.clip(delta, -self.max_steer_rad, self.max_steer_rad))
        delta_deg = math.degrees(delta_clamped)

        # Normalize to servo command range [-1.0, 1.0]
        servo_norm = delta_clamped / self.max_steer_rad

        return SteeringControlOutput(
            steering_angle_rad=delta_clamped,
            steering_angle_deg=delta_deg,
            servo_pwm_normalized=servo_norm,
        )
