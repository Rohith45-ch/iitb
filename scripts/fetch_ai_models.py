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
        "description": "YOLOv8 Nano (320x320) - 3.2M params, high mAP, standard for autonomous edge vision",
        "filename": "yolov8n.onnx",
        "url": "https://huggingface.co/cabelo/yolov8/resolve/main/yolov8n.onnx",
        "recommended": True,
    },
    "yolo11n": {
        "description": "YOLO11 Nano (320x320) - 2.6M params, latest Ultralytics architecture",
        "filename": "yolo11n.onnx",
        "url": "https://huggingface.co/piky/yolo11/resolve/main/yolo11n.onnx",
        "recommended": False,
    },
    "mobilenet_ssd": {
        "description": "MobileNetV1-SSD Lite (300x300) - Lightweight edge detection benchmark",
        "filename": "mobilenet_v1_ssd.onnx",
        "url": "https://github.com/onnx/models/raw/main/validated/vision/object_detection_segmentation/ssd-mobilenetv1/model/ssd_mobilenet_v1_12.onnx",
        "recommended": False,
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
        size_mb = target_path.stat().st_size / (1024 * 1024)
        print(f"[ModelFetcher] Model already present: {target_path} ({size_mb:.1f} MB)")
        return True

    print(f"\n[ModelFetcher] Downloading {model_key}...")
    print(f"  Description: {info['description']}")
    print(f"  Source URL:  {info['url']}")
    print(f"  Target File: {target_path}")

    try:
        req = urllib.request.Request(
            info["url"],
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0"}
        )
        with urllib.request.urlopen(req) as response:
            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0
            chunk_size = 64 * 1024  # 64 KB chunks

            with open(target_path, "wb") as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        pct = int(downloaded * 100 / total_size)
                        mb = downloaded / (1024 * 1024)
                        tot_mb = total_size / (1024 * 1024)
                        sys.stdout.write(f"\r  Progress: {pct}% ({mb:.1f} / {tot_mb:.1f} MB)")
                    else:
                        mb = downloaded / (1024 * 1024)
                        sys.stdout.write(f"\r  Downloaded: {mb:.1f} MB")
                    sys.stdout.flush()

        actual_size_mb = target_path.stat().st_size / (1024 * 1024)
        print(f"\n[ModelFetcher] Download complete: {target_path.name} ({actual_size_mb:.2f} MB)")
        return True
    except Exception as e:
        if target_path.exists():
            target_path.unlink()
        print(f"\n[ModelFetcher] Download failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Fetch Edge AI Models for UAMC Raspberry Pi")
    parser.add_argument(
        "--model",
        choices=list(MODEL_CATALOG.keys()) + ["all"],
        default="yolov8n",
        help="Model architecture to fetch",
    )
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
