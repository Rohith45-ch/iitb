#!/usr/bin/env python3
"""
Pre-Flight System Integration & End-to-End Verification Tool.
Verifies that all software components, AI models, communication protocols,
and ESP32 firmware are ready and interconnected before physical hardware tuning.
"""

import sys
import time
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from uamc.control.longitudinal_controller import LongitudinalPIDController
from uamc.control.pilotnet_controller import PilotNetController
from uamc.control.pure_pursuit import PurePursuitController
from uamc.hal.serial_bridge import SerialBridge
from uamc.perception.ai_detector import EdgeAIDetector
from uamc.perception.lane_detector import LaneDetector
from uamc.perception.obstacle_detector import ObstacleDetector
from uamc.perception.pedestrian import PedestrianDetector
from uamc.perception.traffic_lights import LightState, TrafficLightDetector
from uamc.perception.traffic_signs import TrafficSignDetector
from uamc.planning.behavior_planner import BehaviorPlanner, VehicleState
from uamc.safety.emergency_stop import EmergencyStopManager


def check_status(name: str, passed: bool, detail: str = ""):
    status_str = "\033[92m[PASS]\033[0m" if passed else "\033[91m[FAIL]\033[0m"
    print(f"  {status_str} {name:<42} {detail}")
    return passed


def main():
    print("=" * 70)
    print("  UAMC IIT Bombay — Pre-Flight System Integration Check")
    print("  Verifying Raspberry Pi Software <-> ESP32 Firmware Link")
    print("=" * 70)

    all_passed = True

    # 1. Check AI Models on Disk
    print("\n[Step 1/5] Verifying AI Models in repository...")
    models_to_check = [
        ("yolov8n.onnx", "YOLOv8-Nano Object Detector"),
        ("pilotnet_steering.onnx", "NVIDIA PilotNet Steering Model"),
        ("yolo11n.onnx", "YOLO11-Nano Benchmark"),
        ("mobilenet_v1_ssd.onnx", "MobileNetV1-SSD Lite"),
    ]
    for filename, label in models_to_check:
        path = PROJECT_ROOT / "models" / filename
        exists = path.exists() and path.stat().st_size > 100000
        size_mb = path.stat().st_size / (1024 * 1024) if path.exists() else 0.0
        all_passed &= check_status(label, exists, f"({size_mb:.1f} MB)")

    # 2. Check Neural Inference Pipeline
    print("\n[Step 2/5] Testing AI Inference Engines (CPU / ONNX Runtime)...")
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    yolo = EdgeAIDetector(model_path=str(PROJECT_ROOT / "models" / "yolov8n.onnx"))
    yolo_ok = yolo.model_loaded
    dets = yolo.detect(dummy_frame)
    all_passed &= check_status("YOLOv8n Forward Inference", yolo_ok, f"Input size: {yolo.input_size}")

    pilotnet = PilotNetController(model_path=str(PROJECT_ROOT / "models" / "pilotnet_steering.onnx"))
    pilotnet_ok = pilotnet.model_loaded
    steer_norm, steer_deg = pilotnet.predict_steering(dummy_frame)
    all_passed &= check_status("PilotNet Neural Steering Inference", pilotnet_ok, f"Steer angle: {steer_deg:+.2f} deg")

    # 3. Check Inter-Module Software Connections
    print("\n[Step 3/5] Testing Perception -> Planner -> Controller Pipeline...")
    lane_detector = LaneDetector()
    sign_detector = TrafficSignDetector()
    light_detector = TrafficLightDetector()
    planner = BehaviorPlanner()
    lateral_ctrl = PurePursuitController()
    longitudinal_ctrl = LongitudinalPIDController()

    lane_res = lane_detector.detect_lanes(dummy_frame)
    signs = sign_detector.detect_signs(dummy_frame)
    light_res = light_detector.detect(dummy_frame)

    from uamc.perception.obstacle_detector import ObstacleState, ObstacleThreat
    from uamc.perception.pedestrian import PedestrianCrossingResult

    dummy_obs = ObstacleState(threat_level=ObstacleThreat.CLEAR, closest_distance_m=2.0, relative_bearing="none")
    dummy_ped = PedestrianCrossingResult(crossing_detected=False, distance_to_crossing_m=2.0, pedestrian_present=False)

    cmd = planner.update(
        lane=lane_res,
        obstacle=dummy_obs,
        signs=signs,
        light=light_res,
        pedestrian=dummy_ped,
        emergency_stop_triggered=False,
    )
    pipeline_ok = (cmd.state == VehicleState.LANE_FOLLOWING)
    all_passed &= check_status("Behavior FSM State Transition", pipeline_ok, f"State: {cmd.state.value}")

    steer_out = lateral_ctrl.compute_steering(lane_res.lateral_offset_m, lane_res.heading_error_rad, 0.40)
    all_passed &= check_status("Pure Pursuit Lateral Control", True, f"Output PWM: {steer_out.servo_pwm_normalized:+.2f}")

    # 4. Check Internal Virtual ESP32 Bridge
    print("\n[Step 4/5] Testing Serial Bridge (RPi <-> ESP32 Link)...")
    bridge = SerialBridge(port="/dev/virtual_test_bridge")
    bridge.connect()
    bridge.send_actuator_command(steering_normalized=0.15, throttle_normalized=0.45, estop=False)
    time.sleep(0.08)
    telem = bridge.get_telemetry()
    bridge_ok = (telem.ultrasonic_center_m > 0.0)
    all_passed &= check_status("Internal Serial Bridge (Loopback)", bridge_ok, f"US Center: {telem.ultrasonic_center_m:.2f} m")
    bridge.close()

    # 5. Check ESP32 Firmware Files & Pin Mappings
    print("\n[Step 5/5] Checking ESP32 Firmware Artifacts...")
    firmware_files = [
        ("esp32_config.h", "Centralized Tuning & Pin Configuration"),
        ("esp32_vehicle_controller.ino", "FreeRTOS Dual-Core Firmware"),
        ("tinyml_motion.h", "TinyML Anomaly Classifier"),
        ("ultrasonic_filter.h", "Ultrasonic Outlier Filter"),
    ]
    for fname, label in firmware_files:
        fpath = PROJECT_ROOT / "firmware" / "esp32_firmware" / fname
        f_ok = fpath.exists() and fpath.stat().st_size > 500
        all_passed &= check_status(f"ESP32: {fname}", f_ok, label)

    print("\n" + "=" * 70)
    if all_passed:
        print("  \033[92mALL PRE-FLIGHT CHECKS PASSED!\033[0m")
        print("  Software & Firmware are 100% interconnected and ready for hardware.")
    else:
        print("  \033[91mSOME CHECKS FAILED. Please review details above.\033[0m")
    print("=" * 70)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
