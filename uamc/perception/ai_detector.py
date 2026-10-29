"""
Deep Learning Edge Object Detector (Raspberry Pi Optimized).
Uses OpenCV DNN engine (cv2.dnn) to run quantized ONNX edge models (YOLOv8n / MobileNet-SSD)
on Raspberry Pi CPU without requiring heavy dependencies like PyTorch or TensorFlow.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple
import cv2
import numpy as np


@dataclass
class AIDetection:
    class_id: int
    label: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # (x, y, w, h)
    distance_estimate_m: float


class EdgeAIDetector:
    """
    Lightweight Edge AI Inference Engine for Raspberry Pi.
    Detects traffic lights, stop signs, pedestrians, and obstacles.
    """

    COCO_CLASSES = {
        0: "pedestrian",
        2: "obstacle_car",
        9: "traffic_light",
        11: "stop_sign",
    }

    def __init__(
        self,
        model_path: Optional[str] = None,
        input_size: Tuple[int, int] = (320, 320),
        confidence_threshold: float = 0.45,
        nms_threshold: float = 0.40,
    ):
        self.input_size = input_size
        self.conf_thresh = confidence_threshold
        self.nms_thresh = nms_threshold
        self.net = None
        self.model_loaded = False

        if model_path and Path(model_path).exists():
            self.load_model(model_path)

    def load_model(self, model_path: str) -> bool:
        """Loads ONNX model into OpenCV DNN module with multi-threaded CPU execution."""
        try:
            self.net = cv2.dnn.readNetFromONNX(model_path)
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
            self.model_loaded = True
            print(f"[EdgeAIDetector] Successfully loaded ONNX model: {model_path}")
            return True
        except Exception as e:
            print(f"[EdgeAIDetector] Failed to load ONNX model: {e}")
            self.model_loaded = False
            return False

    def detect(self, frame: np.ndarray) -> List[AIDetection]:
        """Runs forward inference on the camera frame."""
        if not self.model_loaded or self.net is None:
            return []

        h, w, _ = frame.shape
        # Prepare letterbox blob (normalized to 0-1, RGB)
        blob = cv2.dnn.blobFromImage(
            frame,
            scalefactor=1.0 / 255.0,
            size=self.input_size,
            swapRB=True,
            crop=False,
        )
        self.net.setInput(blob)
        outputs = self.net.forward()

        # Parse outputs (e.g. YOLOv8 format: [1, 84, 2100])
        detections = []
        if len(outputs.shape) == 3:
            predictions = outputs[0]
            if predictions.shape[0] < predictions.shape[1]:
                predictions = predictions.T  # Transpose to (num_boxes, 84)

            boxes = []
            confidences = []
            class_ids = []

            for row in predictions:
                scores = row[4:]
                class_id = int(np.argmax(scores))
                conf = float(scores[class_id])

                if conf > self.conf_thresh and class_id in self.COCO_CLASSES:
                    cx, cy, bw, bh = row[0:4]
                    x = int((cx - bw / 2.0) * (w / self.input_size[0]))
                    y = int((cy - bh / 2.0) * (h / self.input_size[1]))
                    bw_scaled = int(bw * (w / self.input_size[0]))
                    bh_scaled = int(bh * (h / self.input_size[1]))

                    boxes.append([x, y, bw_scaled, bh_scaled])
                    confidences.append(conf)
                    class_ids.append(class_id)

            indices = cv2.dnn.NMSBoxes(boxes, confidences, self.conf_thresh, self.nms_thresh)

            for idx in indices:
                i = idx if isinstance(idx, int) else idx[0]
                bx, by, bw, bh = boxes[i]
                cid = class_ids[i]
                lbl = self.COCO_CLASSES.get(cid, "object")

                # Distance estimation based on bounding box height
                dist = float(25.0 / (bh + 1e-5))

                detections.append(
                    AIDetection(
                        class_id=cid,
                        label=lbl,
                        confidence=confidences[i],
                        bbox=(bx, by, bw, bh),
                        distance_estimate_m=dist,
                    )
                )

        return detections

    def draw_detections(self, frame: np.ndarray, detections: List[AIDetection]) -> np.ndarray:
        out = frame.copy()
        for d in detections:
            x, y, w, h = d.bbox
            cv2.rectangle(out, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                out,
                f"{d.label} {d.confidence:.2f} ({d.distance_estimate_m:.1f}m)",
                (x, max(15, y - 5)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )
        return out
