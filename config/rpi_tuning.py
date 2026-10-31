"""
Raspberry Pi 5 — Centralized Tuning & Parameter Configuration Block.
All tuneable perception, AI model, behavior planning, and control parameters
for the physical vehicle are defined here in one place.
"""

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class CameraConfig:
    device_id: int = 0
    width: int = 640
    height: int = 480
    fps: int = 30
    # Inverse Perspective Mapping (IPM) Trapezoid Points (as fractions of image width/height)
    # [Bottom-Left, Bottom-Right, Top-Right, Top-Left]
    src_trapezoid_fractions: List[Tuple[float, float]] = field(
        default_factory=lambda: [
            (0.12, 0.95),  # Bottom-Left
            (0.88, 0.95),  # Bottom-Right
            (0.62, 0.52),  # Top-Right
            (0.38, 0.52),  # Top-Left
        ]
    )


@dataclass
class ColorThresholdConfig:
    # Lane Color Ranges (HSV)
    lane_white_min_hsv: Tuple[int, int, int] = (0, 0, 180)
    lane_white_max_hsv: Tuple[int, int, int] = (180, 50, 255)

    lane_yellow_min_hsv: Tuple[int, int, int] = (18, 90, 120)
    lane_yellow_max_hsv: Tuple[int, int, int] = (35, 255, 255)

    # Traffic Light Color Ranges (HSV)
    light_red1_hsv: Tuple[Tuple[int, int, int], Tuple[int, int, int]] = ((0, 100, 100), (10, 255, 255))
    light_red2_hsv: Tuple[Tuple[int, int, int], Tuple[int, int, int]] = ((165, 100, 100), (180, 255, 255))
    light_yellow_hsv: Tuple[Tuple[int, int, int], Tuple[int, int, int]] = ((18, 100, 100), (35, 255, 255))
    light_green_hsv: Tuple[Tuple[int, int, int], Tuple[int, int, int]] = ((38, 80, 80), (88, 255, 255))
    light_debounce_frames: int = 4

    # Stop Sign Red Range (HSV)
    stop_sign_red1_hsv: Tuple[Tuple[int, int, int], Tuple[int, int, int]] = ((0, 120, 80), (10, 255, 255))
    stop_sign_red2_hsv: Tuple[Tuple[int, int, int], Tuple[int, int, int]] = ((170, 120, 80), (180, 255, 255))


@dataclass
class AIModelConfig:
    # YOLOv8-Nano Settings
    yolo_model_path: str = "models/yolov8n.onnx"
    yolo_input_size: Tuple[int, int] = (640, 640)
    yolo_confidence_threshold: float = 0.45
    yolo_nms_threshold: float = 0.40

    # NVIDIA PilotNet Settings
    pilotnet_model_path: str = "models/pilotnet_steering.onnx"
    pilotnet_input_width: int = 200
    pilotnet_input_height: int = 66
    pilotnet_smoothing_alpha: float = 0.20  # Low-pass filter (0.1 = smoother, 0.5 = more responsive)
    max_steering_angle_deg: float = 25.0


@dataclass
class VehicleControlConfig:
    # Pure Pursuit Lateral Steering Controller
    wheelbase_m: float = 0.260           # 26.0 cm wheelbase (1:10 scale chassis)
    lookahead_min_m: float = 0.28        # Minimum lookahead distance at low speed
    lookahead_gain: float = 0.40         # Speed-adaptive lookahead (l_d = k * v + l_d0)
    max_servo_angle_deg: float = 28.0

    # Longitudinal PID Controller (Speed & Dynamic Braking)
    kp_velocity: float = 1.80
    ki_velocity: float = 0.45
    kd_velocity: float = 0.08
    min_throttle_deadband: float = 0.12  # Minimum PWM fraction to overcome static motor friction
    max_throttle_limit: float = 0.85     # Safety cap on maximum motor PWM


@dataclass
class BehaviorPlannerConfig:
    v_cruise_ms: float = 0.45            # Standard lane-following cruising speed (~1.6 km/h)
    v_approach_ms: float = 0.25          # Approach speed near intersections / obstacles
    stop_sign_hold_time_s: float = 3.0   # Mandatory pause duration at stop sign
    stop_sign_trigger_dist_m: float = 0.40
    obstacle_emergency_dist_m: float = 0.25
    obstacle_advisory_dist_m: float = 0.50
    pedestrian_wait_hold_s: float = 2.0


@dataclass
class HardwareInterfaceConfig:
    serial_port: str = "/dev/ttyUSB0"
    baudrate: int = 115200
    heartbeat_timeout_s: float = 0.20    # 200ms fail-safe timeout


# Global Default Tuning Profile
RPI_CONFIG = {
    "camera": CameraConfig(),
    "color": ColorThresholdConfig(),
    "ai": AIModelConfig(),
    "control": VehicleControlConfig(),
    "planner": BehaviorPlannerConfig(),
    "hal": HardwareInterfaceConfig(),
}
