#!/usr/bin/env python3
"""
AI Edge Model Fetcher for Raspberry Pi & UAMC Vehicle.
Downloads or exports lightweight INT8/FP16 ONNX models (YOLOv8n / MobileNetV2-SSD)
optimized for low-latency ARM CPU inference on Raspberry Pi.
"""

import argparse
import sys
import urllib.request
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "models"


# Pre-optimized lightweight ONNX models for Edge Robotics
MODEL_CATALOG = {
    "yolov8n": {
        "description": "YOLOv8 Nano (320x320) - 3.2MB (Stop signs, traffic lights, pedestrians, cars)",
        "filename": "yolov8n_320.onnx",
        "url": "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.onnx",
    },
    "mobilenet_ssd": {
        "description": "MobileNetV2-SSD Lite (300x300) - 6.8MB (Fast object detection)",
        "filename": "mobilenet_v2_ssd.onnx",
        "url": "https://github.com/onnx/models/raw/main/validated/vision/object_detection_segmentation/ssd-mobilenetv1/model/ssd_mobilenet_v1_12.onnx",
    },
}


def download_model(model_key: str):
    if model_key not in MODEL_CATALOG:
        print(f"Unknown model: {model_key}. Available models: {list(MODEL_CATALOG.keys())}")
        return False

    info = MODEL_CATALOG[model_key]
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    target_path = MODELS_DIR / info["filename"]

    if target_path.exists():
        print(f"[ModelFetcher] Model already present: {target_path}")
        return True

    print(f"[ModelFetcher] Downloading {model_key}: {info['description']}...")
    print(f"[ModelFetcher] URL: {info['url']}")

    try:
        def reporthook(count, block_size, total_size):
            if total_size > 0:
                percent = int(count * block_size * 100 / total_size)
                sys.stdout.write(f"\r  Progress: {percent}% ({count * block_size / 1024 / 1024:.1f} MB)")
                sys.stdout.flush()

        urllib.request.urlretrieve(info["url"], str(target_path), reporthook=reporthook)
        print(f"\n[ModelFetcher] Download complete: {target_path}")
        return True
    except Exception as e:
        print(f"\n[ModelFetcher] Download failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Fetch Edge AI Models for UAMC Raspberry Pi")
    parser.add_argument("--model", choices=["yolov8n", "mobilenet_ssd", "all"], default="yolov8n")
    args = parser.parse_args()

    print("=" * 65)
    print("  UAMC IIT Bombay — Edge AI Model Manager")
    print("=" * 65)

    if args.model == "all":
        for k in MODEL_CATALOG:
            download_model(k)
    else:
        download_model(args.model)


if __name__ == "__main__":
    main()
