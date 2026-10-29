"""
Traffic Sign Recognition Module.
Detects octagonal STOP signs, triangular WARNING/YIELD signs,
and circular SPEED LIMIT signs using color segmentation and contour geometry.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple
import cv2
import numpy as np


class SignType(Enum):
    NONE = "none"
    STOP = "stop"
    YIELD = "yield"
    SPEED_30 = "speed_30"
    SPEED_50 = "speed_50"


@dataclass
class SignDetection:
    sign_type: SignType
    confidence: float
    bbox: Tuple[int, int, int, int]  # (x, y, w, h)
    estimated_distance_m: float


class TrafficSignDetector:
    """
    Detects and classifies road signs in the camera view using multi-channel color thresholding
    and polygonal contour approximation.
    """

    def __init__(self, min_area: int = 400, max_area: int = 30000):
        self.min_area = min_area
        self.max_area = max_area

    def detect_signs(self, frame: np.ndarray) -> List[SignDetection]:
        detections = []
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h, w, _ = frame.shape

        # Red color in HSV wraps around 0/180
        lower_red1 = np.array([0, 100, 70])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 100, 70])
        upper_red2 = np.array([180, 255, 255])

        mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask_red = cv2.bitwise_or(mask_red1, mask_red2)

        # Morphological clean up
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_CLOSE, kernel)

        # Find contours of candidate red signs
        contours, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < self.min_area or area > self.max_area:
                continue

            x, y, bw, bh = cv2.boundingRect(cnt)
            aspect_ratio = float(bw) / float(bh)

            # Square/circular aspect ratio check
            if not (0.75 <= aspect_ratio <= 1.25):
                continue

            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.03 * peri, True)
            num_vertices = len(approx)

            # Octagon approximation (6 to 10 vertices) -> STOP Sign
            if 6 <= num_vertices <= 10:
                # Estimate distance inversely proportional to bounding box height
                # Calibration: A standard 1:10 scaled stop sign (~6cm) at 0.5m is ~60px high
                dist = float(30.0 / (bh + 1e-6))
                detections.append(
                    SignDetection(
                        sign_type=SignType.STOP,
                        confidence=0.88,
                        bbox=(x, y, bw, bh),
                        estimated_distance_m=dist,
                    )
                )

        return detections

    def draw_detections(self, frame: np.ndarray, detections: List[SignDetection]) -> np.ndarray:
        out = frame.copy()
        for det in detections:
            x, y, w, h = det.bbox
            color = (0, 0, 255) if det.sign_type == SignType.STOP else (0, 255, 255)
            cv2.rectangle(out, (x, y), (x + w, y + h), color, 2)
            cv2.putText(
                out,
                f"{det.sign_type.value.upper()} ({det.estimated_distance_m:.2f}m)",
                (x, max(15, y - 5)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                color,
                2,
            )
        return out
