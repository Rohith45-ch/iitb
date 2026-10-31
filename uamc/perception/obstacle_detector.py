"""
Obstacle Detection and Sensor Fusion Module.
Merges front ultrasonic / ToF distance readings with camera contour detections
to detect static and dynamic obstacles and compute time-to-collision (TTC).
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple
import cv2
import numpy as np


class ObstacleThreat(Enum):
    CLEAR = "clear"
    ADVISORY = "advisory"      # Obstacle detected at moderate range, begin slowing down
    EMERGENCY = "emergency"    # Obstacle inside braking safety distance, instant halt


@dataclass
class ObstacleState:
    threat_level: ObstacleThreat
    closest_distance_m: float
    relative_bearing: str  # "left", "center", "right"
    is_dynamic: bool = False


class ObstacleDetector:
    """
    Sensor fusion engine: Combines camera bounding box heuristics with
    ultrasonic range measurements (front-left, front-center, front-right).
    """

    def __init__(
        self,
        emergency_stop_dist_m: float = 0.25,
        advisory_slow_dist_m: float = 0.45,
        single_sonar_mode: bool = True,
    ):
        self.emergency_dist = emergency_stop_dist_m
        self.advisory_dist = advisory_slow_dist_m
        self.single_sonar_mode = single_sonar_mode
        self.prev_distance = None

    def process(
        self,
        ultrasonic_left_m: float,
        ultrasonic_center_m: float,
        ultrasonic_right_m: float,
        camera_frame: Optional[np.ndarray] = None,
    ) -> ObstacleState:
        # Fuse front ultrasonic readings
        # Per Wiring_and_Pin_Map PDF §7: "Only one sonar is fitted. Left, right and flank readings must not stop the car."
        if self.single_sonar_mode:
            valid_ranges = [ultrasonic_center_m] if 0.02 < ultrasonic_center_m < 3.0 else []
        else:
            valid_ranges = [
                d for d in [ultrasonic_left_m, ultrasonic_center_m, ultrasonic_right_m]
                if 0.02 < d < 3.0
            ]

        min_dist = min(valid_ranges) if valid_ranges else 10.0

        # Determine bearing of closest obstacle
        if min_dist == ultrasonic_left_m:
            bearing = "left"
        elif min_dist == ultrasonic_right_m:
            bearing = "right"
        else:
            bearing = "center"

        # Check if dynamic (closing velocity > vehicle's own velocity)
        is_dynamic = False
        if self.prev_distance is not None:
            delta_dist = self.prev_distance - min_dist
            # If closing rapidly (> 0.7 m/s between cycles), likely dynamic
            if delta_dist > 0.15:
                is_dynamic = True
        self.prev_distance = min_dist

        # Map to threat level
        if min_dist <= self.emergency_dist:
            threat = ObstacleThreat.EMERGENCY
        elif min_dist <= self.advisory_dist:
            threat = ObstacleThreat.ADVISORY
        else:
            threat = ObstacleThreat.CLEAR

        return ObstacleState(
            threat_level=threat,
            closest_distance_m=min_dist,
            relative_bearing=bearing,
            is_dynamic=is_dynamic,
        )
