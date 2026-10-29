"""Unit tests for BehaviorPlanner module."""

import unittest
import numpy as np
from uamc.perception.lane_detector import LaneResult
from uamc.perception.obstacle_detector import ObstacleState, ObstacleThreat
from uamc.perception.pedestrian import PedestrianCrossingResult
from uamc.perception.traffic_lights import LightState, TrafficLightResult
from uamc.perception.traffic_signs import SignDetection, SignType
from uamc.planning.behavior_planner import BehaviorPlanner, VehicleState


class TestBehaviorPlanner(unittest.TestCase):
    def setUp(self):
        self.planner = BehaviorPlanner(
            cruising_velocity_ms=0.45,
            approach_velocity_ms=0.25,
            stop_sign_hold_time_s=1.0,  # Fast 1.0s for testing
        )
        self.default_lane = LaneResult(
            is_valid=True,
            lateral_offset_m=0.0,
            curvature_radius_m=1000.0,
            heading_error_rad=0.0,
            debug_frame=np.zeros((10, 10, 3), dtype=np.uint8),
        )
        self.default_obstacle = ObstacleState(
            threat_level=ObstacleThreat.CLEAR,
            closest_distance_m=2.0,
            relative_bearing="center",
        )
        self.default_light = TrafficLightResult(state=LightState.GREEN, confidence=0.9, bbox=None)
        self.default_pedestrian = PedestrianCrossingResult(
            crossing_detected=False,
            distance_to_crossing_m=10.0,
            pedestrian_present=False,
        )

    def test_nominal_lane_following(self):
        cmd = self.planner.update(
            lane=self.default_lane,
            obstacle=self.default_obstacle,
            signs=[],
            light=self.default_light,
            pedestrian=self.default_pedestrian,
        )
        self.assertEqual(cmd.state, VehicleState.LANE_FOLLOWING)
        self.assertEqual(cmd.target_velocity_ms, 0.45)

    def test_emergency_obstacle_stop(self):
        close_obstacle = ObstacleState(
            threat_level=ObstacleThreat.EMERGENCY,
            closest_distance_m=0.20,
            relative_bearing="center",
        )
        cmd = self.planner.update(
            lane=self.default_lane,
            obstacle=close_obstacle,
            signs=[],
            light=self.default_light,
            pedestrian=self.default_pedestrian,
        )
        self.assertEqual(cmd.state, VehicleState.EMERGENCY_STOP)
        self.assertEqual(cmd.target_velocity_ms, 0.0)

    def test_red_light_stop(self):
        red_light = TrafficLightResult(state=LightState.RED, confidence=0.95, bbox=None)
        cmd = self.planner.update(
            lane=self.default_lane,
            obstacle=self.default_obstacle,
            signs=[],
            light=red_light,
            pedestrian=self.default_pedestrian,
        )
        self.assertEqual(cmd.state, VehicleState.RED_LIGHT_WAIT)
        self.assertEqual(cmd.target_velocity_ms, 0.0)

    def test_stop_sign_hold(self):
        stop_sign = SignDetection(
            sign_type=SignType.STOP,
            confidence=0.9,
            bbox=(10, 10, 50, 50),
            estimated_distance_m=0.30,
        )
        cmd = self.planner.update(
            lane=self.default_lane,
            obstacle=self.default_obstacle,
            signs=[stop_sign],
            light=self.default_light,
            pedestrian=self.default_pedestrian,
        )
        self.assertEqual(cmd.state, VehicleState.STOP_SIGN_WAIT)
        self.assertEqual(cmd.target_velocity_ms, 0.0)


if __name__ == "__main__":
    unittest.main()
