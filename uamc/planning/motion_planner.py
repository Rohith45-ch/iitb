"""
Motion Planning and Trajectory Generation Module.
Generates smooth velocity profiles (trapezoidal acceleration/deceleration)
and local collision-free lane-change trajectories.
"""

from dataclasses import dataclass
from typing import List, Tuple
import numpy as np


@dataclass
class TrajectoryPoint:
    x_m: float
    y_m: float
    target_velocity_ms: float
    curvature_rad_m: float


class MotionPlanner:
    """
    Computes smooth longitudinal acceleration/braking curves and lateral offsets.
    """

    def __init__(
        self,
        max_accel_ms2: float = 1.2,
        max_decel_ms2: float = 2.2,
    ):
        self.max_accel = max_accel_ms2
        self.max_decel = max_decel_ms2
        self.current_velocity = 0.0

    def compute_speed_profile(
        self,
        target_velocity: float,
        dt: float,
    ) -> float:
        """Rate-limits velocity changes according to physical acceleration/braking boundaries."""
        if target_velocity > self.current_velocity:
            self.current_velocity = min(
                target_velocity,
                self.current_velocity + self.max_accel * dt,
            )
        else:
            self.current_velocity = max(
                target_velocity,
                self.current_velocity - self.max_decel * dt,
            )
        return self.current_velocity

    def generate_overtake_spline(
        self,
        start_offset_m: float,
        target_offset_m: float,
        longitudinal_distance_m: float = 1.0,
        num_points: int = 20,
    ) -> List[Tuple[float, float]]:
        """
        Generates a 5th-order polynomial (quintic spline) for smooth, jerk-minimized lane changes.
        """
        y_pts = np.linspace(0.0, longitudinal_distance_m, num_points)
        # Normalized progress s in [0, 1]
        s = y_pts / (longitudinal_distance_m + 1e-6)
        # Quintic polynomial: 10s^3 - 15s^4 + 6s^5 (zero start & end velocity/acceleration)
        poly = 10 * (s**3) - 15 * (s**4) + 6 * (s**5)
        x_pts = start_offset_m + (target_offset_m - start_offset_m) * poly

        return list(zip(x_pts, y_pts))
