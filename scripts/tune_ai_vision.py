#!/usr/bin/env python3
"""
Interactive AI Vision & Model Tuning Tool for Raspberry Pi 5.
Benchmarking tool to test YOLOv8, YOLO11, PilotNet, and Lane Detection live on camera
or synthetic feeds with real-time FPS counter, confidence filtering, and debug image export.
"""

import argparse
import sys
import time
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import cv2
import numpy as np

from config.rpi_tuning import RPI_CONFIG
from uamc.hal.camera_interface import CameraInterface
from uamc.perception.ai_detector import EdgeAIDetector
from uamc.perception.lane_detector import LaneDetector
from uamc.perception.traffic_lights import TrafficLightDetector


def parse_args():
    parser = argparse.ArgumentParser(description="Live AI Vision Tuning & Benchmarking on Raspberry Pi")
    parser.add_argument("--model", type=str, default="models/yolov8n.onnx",
                        help="Path to ONNX model (yolov8n.onnx, yolo11n.onnx, pilotnet_steering.onnx)")
    parser.add_argument("--conf", type=float, default=0.40, help="Confidence threshold (0.1 - 0.9)")
    parser.add_argument("--camera", type=int, default=0, help="Camera device index (/dev/videoX)")
    parser.add_argument("--save-frames", action="store_true", help="Save annotated debug frames to debug_frames/")
    parser.add_argument("--max-frames", type=int, default=100, help="Total frames to process for benchmark")
    return parser.parse_args()


def main():
    args = parse_args()
    print("=" * 60)
    print("🚗 UAMC AI VISION TUNING & BENCHMARK TOOL")
    print(f"Model: {args.model}")
    print(f"Confidence Threshold: {args.conf}")
    print(f"Camera Device ID: {args.camera}")
    print("=" * 60)

    # 1. Initialize Perception Modules
    detector = EdgeAIDetector(model_path=args.model, confidence_threshold=args.conf)
    lane_det = LaneDetector()
    tl_det = TrafficLightDetector()

    if detector.model_loaded:
        print(f"✅ AI Model loaded successfully via ONNX Runtime (Engine active)")
    else:
        print(f"⚠️ Model at {args.model} not found or failed to load. Running visual lane detection only.")

    # 2. Initialize Camera
    cam = CameraInterface(source=args.camera, width=640, height=480, fps=30)
    cam_opened = cam.start()

    if not cam_opened:
        print("⚠️ Physical camera not detected. Generating synthetic test track frame for benchmark...")

    out_dir = Path("debug_frames")
    if args.save_frames:
        out_dir.mkdir(exist_ok=True)

    latencies_ms = []
    frame_count = 0

    print("\nStarting live benchmark loop (Press Ctrl+C to stop)...")
    try:
        while frame_count < args.max_frames:
            t0 = time.perf_counter()

            if cam_opened:
                frame = cam.read_frame()
                if frame is None:
                    continue
            else:
                # Generate synthetic road frame with simulated lanes
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.line(frame, (120, 480), (280, 260), (255, 255, 255), 10)  # Left white lane
                cv2.line(frame, (520, 480), (360, 260), (0, 255, 255), 10)    # Right yellow lane

            # Run Lane Detection
            lane_res = lane_det.detect_lanes(frame)

            # Run AI Object Detection
            detections = []
            if detector.model_loaded:
                detections = detector.detect(frame)

            t_elapsed_ms = (time.perf_counter() - t0) * 1000.0
            latencies_ms.append(t_elapsed_ms)
            frame_count += 1

            fps = 1000.0 / t_elapsed_ms if t_elapsed_ms > 0 else 0

            # Annotate visual frame
            annotated = frame.copy()
            if detector.model_loaded and detections:
                annotated = detector.draw_detections(annotated, detections)

            # Draw HUD
            hud_text = f"FPS: {fps:5.1f} | Latency: {t_elapsed_ms:4.1f}ms | Lanes: {lane_res.is_valid}"
            cv2.putText(annotated, hud_text, (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(annotated, f"Curvature: {lane_res.curvature_radius_m:.1f}m | Offset: {lane_res.lateral_offset_m*100:.1f}cm",
                        (15, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 220, 255), 2)

            if frame_count % 10 == 0 or frame_count == 1:
                print(f"[Frame {frame_count:03d}] {hud_text} | Detections: {len(detections)}")

            if args.save_frames and frame_count % 10 == 0:
                save_path = out_dir / f"frame_{frame_count:03d}.jpg"
                cv2.imwrite(str(save_path), annotated)

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nBenchmark halted by user.")
    finally:
        if cam_opened:
            cam.stop()

    # 3. Summary Statistics
    if latencies_ms:
        avg_lat = np.mean(latencies_ms)
        p95_lat = np.percentile(latencies_ms, 95)
        avg_fps = 1000.0 / avg_lat
        print("\n" + "=" * 60)
        print("📊 BENCHMARK SUMMARY RESULTS:")
        print(f"Total Frames Processed: {frame_count}")
        print(f"Average Inference Latency: {avg_lat:.2f} ms")
        print(f"95th Percentile Latency:   {p95_lat:.2f} ms")
        print(f"Sustained Throughput:      {avg_fps:.1f} FPS")
        print("=" * 60)


if __name__ == "__main__":
    main()
