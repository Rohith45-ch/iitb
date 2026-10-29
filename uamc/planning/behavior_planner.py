"""
Behavioral Planning and Finite State Machine (FSM).
Coordinates perception inputs and dictates the vehicle's tactical driving mode.
Ensures zero rule violations and strict compliance with UAMC smart city regulations.
"""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from uamc.perception.lane_detector import LaneResult
from uamc.perception.obstacle_detector import ObstacleState, ObstacleThreat
from uamc.perception.pedestrian import PedestrianCrossingResult
from uamc.perception.traffic_lights import LightState, TrafficLightResult
from uamc.perception.traffic_signs import SignDetection, SignType


class VehicleState(Enum):
    LANE_FOLLOWING = "LANE_FOLLOWING"
    STOP_SIGN_WAIT = "STOP_SIGN_WAIT"
    RED_LIGHT_WAIT = "RED_LIGHT_WAIT"
    PEDESTRIAN_WAIT = "PEDESTRIAN_WAIT"
    ROUNDABOUT_TRANSIT = "ROUNDABOUT_TRANSIT"
    OBSTACLE_AVOIDANCE = "OBSTACLE_AVOIDANCE"
    PARKING_MANEUVER = "PARKING_MANEUVER"
    EMERGENCY_STOP = "EMERGENCY_STOP"


@dataclass
class BehaviorCommand:
    state: VehicleState
    target_velocity_ms: float
    target_steering_bias: float
    description: str


class BehaviorPlanner:
    """
    Finite State Machine (FSM) managing high-level autonomous behavior.
    """

    def __init__(
        self,
        cruising_velocity_ms: float = 0.45,
        approach_velocity_ms: float = 0.25,
        stop_sign_hold_time_s: float = 3.0,
    ):
        self.v_cruise = cruising_velocity_ms
        self.v_approach = approach_velocity_ms
        self.stop_sign_hold_time = stop_sign_hold_time_s

        self.current_state = VehicleState.LANE_FOLLOWING
        self.state_enter_time = time.time()
        self.has_serviced_last_stop_sign = False
        self.last_stop_sign_time = 0.0

    def transition_to(self, new_state: VehicleState):
        if self.current_state != new_state:
            self.current_state = new_state
            self.state_enter_time = time.time()

    def update(
        self,
        lane: LaneResult,
        obstacle: ObstacleState,
        signs: list[SignDetection],
        light: TrafficLightResult,
        pedestrian: PedestrianCrossingResult,
        emergency_stop_triggered: bool = False,
    ) -> BehaviorCommand:
        now = time.time()

        # Priority 1: Hardware or software Emergency Stop
        if emergency_stop_triggered or obstacle.threat_level == ObstacleThreat.EMERGENCY:
            self.transition_to(VehicleState.EMERGENCY_STOP)
            return BehaviorCommand(
                state=VehicleState.EMERGENCY_STOP,
                target_velocity_ms=0.0,
                target_steering_bias=0.0,
                description="Emergency Stop Active - Threat Detected",
            )

        # State Machine Transitions
        if self.current_state == VehicleState.EMERGENCY_STOP:
            # Recover if threat is cleared
            if obstacle.threat_level == ObstacleThreat.CLEAR and not emergency_stop_triggered:
                self.transition_to(VehicleState.LANE_FOLLOWING)

        elif self.current_state == VehicleState.LANE_FOLLOWING:
            # Check for close Stop sign
            stop_triggered = False
            for s in signs:
                if s.sign_type == SignType.STOP and s.estimated_distance_m < 0.40:
                    if (now - self.last_stop_sign_time) > 10.0:  # Debounce previously serviced sign
                        self.transition_to(VehicleState.STOP_SIGN_WAIT)
                        stop_triggered = True
                        break

            # Check for Red traffic light
            if not stop_triggered and light.state == LightState.RED:
                self.transition_to(VehicleState.RED_LIGHT_WAIT)

            # Check for Pedestrian at crossing
            elif not stop_triggered and pedestrian.crossing_detected and pedestrian.pedestrian_present:
                self.transition_to(VehicleState.PEDESTRIAN_WAIT)

            # Check for Obstacle Advisory (slow down or steer around)
            elif not stop_triggered and obstacle.threat_level == ObstacleThreat.ADVISORY:
                self.transition_to(VehicleState.OBSTACLE_AVOIDANCE)

        if self.current_state == VehicleState.STOP_SIGN_WAIT:
            # Mandate 3.0s stationary pause
            elapsed = now - self.state_enter_time
            if elapsed >= self.stop_sign_hold_time:
                self.last_stop_sign_time = now
                self.transition_to(VehicleState.LANE_FOLLOWING)
            else:
                return BehaviorCommand(
                    state=VehicleState.STOP_SIGN_WAIT,
                    target_velocity_ms=0.0,
                    target_steering_bias=0.0,
                    description=f"Waiting at Stop Sign ({self.stop_sign_hold_time - elapsed:.1f}s remaining)",
                )

        elif self.current_state == VehicleState.RED_LIGHT_WAIT:
            if light.state == LightState.GREEN:
                self.transition_to(VehicleState.LANE_FOLLOWING)
            else:
                return BehaviorCommand(
                    state=VehicleState.RED_LIGHT_WAIT,
                    target_velocity_ms=0.0,
                    target_steering_bias=0.0,
                    description="Waiting for Green Light",
                )

        elif self.current_state == VehicleState.PEDESTRIAN_WAIT:
            if not pedestrian.pedestrian_present:
                self.transition_to(VehicleState.LANE_FOLLOWING)
            else:
                return BehaviorCommand(
                    state=VehicleState.PEDESTRIAN_WAIT,
                    target_velocity_ms=0.0,
                    target_steering_bias=0.0,
                    description="Yielding to Pedestrian on Crossing",
                )

        elif self.current_state == VehicleState.OBSTACLE_AVOIDANCE:
            if obstacle.threat_level == ObstacleThreat.CLEAR:
                self.transition_to(VehicleState.LANE_FOLLOWING)
            else:
                # Creep forward or bias steering depending on bearing
                steering_bias = -0.15 if obstacle.relative_bearing == "right" else 0.15
                return BehaviorCommand(
                    state=VehicleState.OBSTACLE_AVOIDANCE,
                    target_velocity_ms=self.v_approach,
                    target_steering_bias=steering_bias,
                    description=f"Navigating around Obstacle on {obstacle.relative_bearing}",
                )

        # Standard Lane Following
        return BehaviorCommand(
            state=VehicleState.LANE_FOLLOWING,
            target_velocity_ms=self.v_cruise,
            target_steering_bias=0.0,
            description="Autonomous Lane Tracking",
        )
