#!/usr/bin/env python3
"""
Main Autonomous Vehicle Loop (Physical Vehicle Deployment).
Executes the high-rate perception, behavior planning, Pure Pursuit control,
and safety watchdog loop.
"""

import argparse
import sys
import time
from pathlib import Path
import cv2

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from uamc.control.longitudinal_controller import LongitudinalPIDController
from uamc.control.pure_pursuit import PurePursuitController
from uamc.hal.camera_interface import CameraInterface
from uamc.hal.serial_bridge import SerialBridge
from uamc.perception.lane_detector import LaneDetector
from uamc.perception.obstacle_detector import ObstacleDetector
from uamc.perception.pedestrian import PedestrianDetector
from uamc.perception.traffic_lights import TrafficLightDetector
from uamc.perception.traffic_signs import TrafficSignDetector
from uamc.planning.behavior_planner import BehaviorPlanner
from uamc.safety.emergency_stop import EmergencyStopManager


def main():
    parser = argparse.ArgumentParser(description="UAMC Autonomous Vehicle Runtime")
    parser.add_argument("--camera-id", type=int, default=0, help="V4L2 camera device ID")
    parser.add_argument("--serial-port", type=str, default="/dev/ttyUSB0", help="MCU Serial Port")
    parser.add_argument("--baudrate", type=int, default=115200, help="MCU Baudrate")
    parser.add_argument("--no-gui", action="store_true", help="Run in headless mode without X11 windows")
    args = parser.parse_args()

    print("=" * 60)
    print("  AML-Rover-V1 — Urban Autonomous Mobility Challenge (UAMC)")
    print("  Techfest, IIT Bombay")
    print("=" * 60)

    # 1. Initialize HAL
    camera = CameraInterface(source=args.camera_id, width=640, height=480, fps=30)
    serial_bridge = SerialBridge(port=args.serial_port, baudrate=args.baudrate)

    camera_ok = camera.start()
    serial_ok = serial_bridge.connect()

    # 2. Initialize Core Subsystems
    lane_detector = LaneDetector(image_width=640, image_height=480)
    sign_detector = TrafficSignDetector()
    light_detector = TrafficLightDetector()
    pedestrian_detector = PedestrianDetector(image_width=640, image_height=480)
    obstacle_detector = ObstacleDetector(emergency_stop_dist_m=0.25, advisory_slow_dist_m=0.45)

    planner = BehaviorPlanner(cruising_velocity_ms=0.45, approach_velocity_ms=0.25)
    lateral_ctrl = PurePursuitController(wheelbase_m=0.260, max_steering_angle_deg=28.0)
    longitudinal_ctrl = LongitudinalPIDController(kp=1.8, ki=0.45, kd=0.08)
    safety_mgr = EmergencyStopManager(heartbeat_timeout_s=0.20)

    print("[Main] All subsystems initialized. Commencing autonomous loop...")
    last_time = time.time()
    measured_speed = 0.0

    try:
        while True:
            loop_start = time.time()
            dt = max(0.001, loop_start - last_time)
            last_time = loop_start

            safety_mgr.ping()

            # Read Camera Frame
            frame = camera.read_frame()
            if frame is None:
                # Camera dropout -> engage graceful slowdown
                safety_mgr.record_subsystem_heartbeat("camera")
                time.sleep(0.01)
                continue

            safety_mgr.record_subsystem_heartbeat("camera")

            # Read Telemetry from MCU
            telemetry = serial_bridge.get_telemetry()
            if telemetry.is_hardware_estop_pressed:
                safety_mgr.trigger_estop("Hardware Kill Switch Activated on MCU")

            # --- Perception Pipeline ---
            lane_res = lane_detector.detect_lanes(frame)
            signs = sign_detector.detect_signs(frame)
            light_res = light_detector.detect(frame)
            ped_res = pedestrian_detector.detect(frame)
            obs_res = obstacle_detector.process(
                ultrasonic_left_m=telemetry.ultrasonic_left_m,
                ultrasonic_center_m=telemetry.ultrasonic_center_m,
                ultrasonic_right_m=telemetry.ultrasonic_right_m,
                camera_frame=frame,
            )

            # --- Safety Verification ---
            safety_status = safety_mgr.evaluate()

            # --- Behavioral Planning ---
            cmd = planner.update(
                lane=lane_res,
                obstacle=obs_res,
                signs=signs,
                light=light_res,
                pedestrian=ped_res,
                emergency_stop_triggered=safety_status.estop_active,
            )

            # --- Control Execution ---
            # Steering
            steer_out = lateral_ctrl.compute_steering(
                lateral_offset_m=lane_res.lateral_offset_m if lane_res.is_valid else 0.0,
                heading_error_rad=lane_res.heading_error_rad if lane_res.is_valid else 0.0,
                current_velocity_ms=measured_speed,
                steering_bias=cmd.target_steering_bias,
            )

            # Throttle
            throttle_out = longitudinal_ctrl.compute_throttle(
                target_velocity_ms=cmd.target_velocity_ms,
                measured_velocity_ms=measured_speed,
                dt=dt,
            )

            # Send commands to MCU
            serial_bridge.send_actuator_command(
                steering_normalized=steer_out.servo_pwm_normalized,
                throttle_normalized=throttle_out.throttle_pwm_normalized,
                estop=safety_status.estop_active,
            )

            # GUI Display / Video Feed overlay
            if not args.no_gui:
                hud = lane_res.debug_frame.copy()
                cv2.putText(
                    hud,
                    f"STATE: {cmd.state.value} | {cmd.description}",
                    (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0) if safety_status.is_safe else (0, 0, 255),
                    2,
                )
                cv2.putText(
                    hud,
                    f"Steer: {steer_out.steering_angle_deg:+.1f} deg | V_tgt: {cmd.target_velocity_ms:.2f} m/s",
                    (20, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (255, 255, 255),
                    2,
                )
                cv2.imshow("AML-Rover-V1 Autonomous Telemetry", hud)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            # Target 30 Hz loop rate
            elapsed = time.time() - loop_start
            sleep_time = max(0.0, (1.0 / 30.0) - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\n[Main] User interrupt. Halting vehicle safely...")
    finally:
        serial_bridge.send_actuator_command(0.0, 0.0, estop=True)
        serial_bridge.close()
        camera.stop()
        cv2.destroyAllWindows()
        print("[Main] Shutdown complete.")


if __name__ == "__main__":
    main()
