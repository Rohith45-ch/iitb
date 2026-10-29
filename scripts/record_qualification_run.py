#!/usr/bin/env python3
"""
Qualification Run Video Recorder.
Records the autonomous test run with live telemetry HUD overlay
directly to an MP4 video file for the Techfest IIT Bombay Round 1 submission!
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
from uamc.simulation.synthetic_track import SyntheticTrackSimulator


def main():
    parser = argparse.ArgumentParser(description="Record UAMC Qualification Video")
    parser.add_argument("--output", type=str, default="qualification_run.mp4", help="Output MP4 file path")
    parser.add_argument("--duration", type=float, default=15.0, help="Recording duration in seconds")
    parser.add_argument("--fps", type=int, default=30, help="Video recording frame rate")
    parser.add_argument("--sim", action="store_true", help="Record in simulation mode if physical car not connected")
    parser.add_argument("--camera-id", type=int, default=0, help="V4L2 camera ID")
    parser.add_argument("--serial-port", type=str, default="/dev/ttyAMA0", help="RPi UART port to ESP32")
    args = parser.parse_args()

    print("=" * 65)
    print("  UAMC IIT Bombay — Qualification Run Video Recorder")
    print(f"  Target Output: {args.output} ({args.duration:.1f}s @ {args.fps} FPS)")
    print("=" * 65)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out_writer = cv2.VideoWriter(args.output, fourcc, args.fps, (640, 480))

    lane_detector = LaneDetector(image_width=640, image_height=480)
    sign_detector = TrafficSignDetector()
    light_detector = TrafficLightDetector()
    pedestrian_detector = PedestrianDetector()
    obstacle_detector = ObstacleDetector()

    planner = BehaviorPlanner(cruising_velocity_ms=0.45, approach_velocity_ms=0.25)
    lateral_ctrl = PurePursuitController(wheelbase_m=0.260, max_steering_angle_deg=28.0)
    longitudinal_ctrl = LongitudinalPIDController(kp=1.8, ki=0.45, kd=0.08)
    safety_mgr = EmergencyStopManager()

    if args.sim:
        sim = SyntheticTrackSimulator(width=640, height=480)
        camera = None
        serial_bridge = None
        print("[Recorder] Running in Synthetic Simulation Mode...")
    else:
        camera = CameraInterface(source=args.camera_id, width=640, height=480, fps=args.fps)
        camera.start()
        serial_bridge = SerialBridge(port=args.serial_port, baudrate=115200)
        serial_bridge.connect()
        print(f"[Recorder] Recording physical vehicle on camera {args.camera_id} & port {args.serial_port}...")

    start_time = time.time()
    last_time = start_time
    frame_count = 0

    car_offset_m = -0.05
    car_heading_deg = 2.0
    measured_speed = 0.0

    try:
        while True:
            now = time.time()
            elapsed = now - start_time
            if elapsed >= args.duration:
                break

            dt = max(0.001, now - last_time)
            last_time = now

            safety_mgr.ping()
            safety_mgr.record_subsystem_heartbeat("camera")

            # Acquire Frame
            if args.sim:
                show_obstacle = (elapsed > 6.0)
                obs_dist = max(0.20, 2.0 - (elapsed - 6.0) * 0.40) if show_obstacle else 3.0
                frame = sim.render_frame(
                    lateral_offset_m=car_offset_m,
                    heading_angle_deg=car_heading_deg,
                    show_stop_sign=(1.0 <= elapsed <= 3.5),
                    show_obstacle_dist_m=obs_dist if show_obstacle else None,
                )
                us_left = obs_dist
                us_center = obs_dist
                us_right = obs_dist
            else:
                frame = camera.read_frame()
                if frame is None:
                    time.sleep(0.01)
                    continue
                telem = serial_bridge.get_telemetry()
                us_left = telem.ultrasonic_left_m
                us_center = telem.ultrasonic_center_m
                us_right = telem.ultrasonic_right_m

            # Perception
            lane_res = lane_detector.detect_lanes(frame)
            signs = sign_detector.detect_signs(frame)
            light_res = light_detector.detect(frame)
            ped_res = pedestrian_detector.detect(frame)
            obs_res = obstacle_detector.process(
                ultrasonic_left_m=us_left,
                ultrasonic_center_m=us_center,
                ultrasonic_right_m=us_right,
                camera_frame=frame,
            )

            # Behavior & Control
            safety_status = safety_mgr.evaluate()
            cmd = planner.update(
                lane=lane_res,
                obstacle=obs_res,
                signs=signs,
                light=light_res,
                pedestrian=ped_res,
                emergency_stop_triggered=safety_status.estop_active,
            )

            steer_out = lateral_ctrl.compute_steering(
                lateral_offset_m=lane_res.lateral_offset_m if lane_res.is_valid else car_offset_m,
                heading_error_rad=lane_res.heading_error_rad if lane_res.is_valid else 0.0,
                current_velocity_ms=measured_speed,
                steering_bias=cmd.target_steering_bias,
            )

            throttle_out = longitudinal_ctrl.compute_throttle(
                target_velocity_ms=cmd.target_velocity_ms,
                measured_velocity_ms=measured_speed,
                dt=dt,
            )

            if args.sim:
                car_offset_m += (cmd.target_velocity_ms * 0.5) * (steer_out.steering_angle_rad * 0.3) * dt
                measured_speed = cmd.target_velocity_ms
            elif serial_bridge:
                serial_bridge.send_actuator_command(
                    steer_out.servo_pwm_normalized,
                    throttle_out.throttle_pwm_normalized,
                    estop=safety_status.estop_active,
                )

            # Render Telemetry HUD
            hud = lane_res.debug_frame.copy()

            # Techfest Header Banner
            cv2.rectangle(hud, (0, 0), (640, 50), (20, 20, 20), -1)
            cv2.putText(
                hud,
                "UAMC TECHFEST IIT BOMBAY - QUALIFICATION RUN",
                (15, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 220, 255),
                2,
            )

            # Telemetry Box
            cv2.rectangle(hud, (15, 60), (330, 145), (10, 10, 10), -1)
            cv2.rectangle(hud, (15, 60), (330, 145), (0, 180, 0), 1)

            cv2.putText(
                hud,
                f"State: {cmd.state.value}",
                (25, 82),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
            )
            cv2.putText(
                hud,
                f"Target Speed: {cmd.target_velocity_ms:.2f} m/s",
                (25, 102),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )
            cv2.putText(
                hud,
                f"Steer: {steer_out.steering_angle_deg:+.1f} deg | Offset: {lane_res.lateral_offset_m*100:+.1f} cm",
                (25, 122),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )
            cv2.putText(
                hud,
                f"Time: {elapsed:04.1f}s | Obs: {obs_res.closest_distance_m:.2f}m",
                (25, 138),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (0, 255, 255),
                1,
            )

            out_writer.write(hud)
            frame_count += 1
            time.sleep(1.0 / args.fps)

    finally:
        out_writer.release()
        if camera:
            camera.stop()
        if serial_bridge:
            serial_bridge.send_actuator_command(0.0, 0.0, estop=True)
            serial_bridge.close()

    print(f"\n[Recorder] Successfully recorded {frame_count} frames to {args.output}!")
    print(f"[Recorder] Video duration: {frame_count / args.fps:.1f} seconds. Ready for submission.")


if __name__ == "__main__":
    main()
