"""
Traffic Light Detection and State Classification Module.
Identifies vertical 3-lamp miniature traffic lights and detects Red, Yellow, Green states.
Includes temporal debouncing to eliminate false flicker.
"""

from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple
import cv2
import numpy as np


class LightState(Enum):
    UNKNOWN = "unknown"
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"


@dataclass
class TrafficLightResult:
    state: LightState
    confidence: float
    bbox: Optional[Tuple[int, int, int, int]]  # (x, y, w, h)


class TrafficLightDetector:
    """
    Detects traffic lights using color brightness analysis within vertical aspect ratio boxes.
    Maintains a rolling history queue to debounce transient lighting changes.
    """

    def __init__(self, debounce_frames: int = 4):
        self.history = deque(maxlen=debounce_frames)

    def detect(self, frame: np.ndarray, bbox: Optional[Tuple[int, int, int, int]] = None) -> TrafficLightResult:
        h, w, _ = frame.shape
        if bbox is not None:
            bx, by, bw, bh = bbox
            x1, y1 = max(0, bx), max(0, by)
            x2, y2 = min(w, bx + bw), min(h, by + bh)
            if (x2 - x1) < 5 or (y2 - y1) < 10:
                roi = frame[0:int(h * 0.70), :]
            else:
                roi = frame[y1:y2, x1:x2]
        else:
            # Search primarily in the upper half of the frame where traffic light posts are located
            roi_y_limit = int(h * 0.70)
            roi = frame[0:roi_y_limit, :]

        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # Red mask
        r1 = cv2.inRange(hsv, np.array([0, 100, 100]), np.array([10, 255, 255]))
        r2 = cv2.inRange(hsv, np.array([165, 100, 100]), np.array([180, 255, 255]))
        red_mask = cv2.bitwise_or(r1, r2)

        # Yellow mask
        yellow_mask = cv2.inRange(hsv, np.array([18, 100, 100]), np.array([35, 255, 255]))

        # Green mask
        green_mask = cv2.inRange(hsv, np.array([38, 80, 80]), np.array([88, 255, 255]))

        # Count active pixel clusters
        red_pixels = cv2.countNonZero(red_mask)
        yellow_pixels = cv2.countNonZero(yellow_mask)
        green_pixels = cv2.countNonZero(green_mask)

        threshold = 20 if bbox is not None else 60
        detected_state = LightState.UNKNOWN
        max_pixels = max(red_pixels, yellow_pixels, green_pixels)

        if max_pixels > threshold:
            if max_pixels == red_pixels:
                detected_state = LightState.RED
            elif max_pixels == yellow_pixels:
                detected_state = LightState.YELLOW
            elif max_pixels == green_pixels:
                detected_state = LightState.GREEN

        self.history.append(detected_state)

        # Debounce: only commit state if majority in history agree
        if len(self.history) == self.history.maxlen:
            counts = {s: self.history.count(s) for s in LightState}
            most_common = max(counts, key=counts.get)
            if counts[most_common] >= (self.history.maxlen // 2 + 1):
                return TrafficLightResult(state=most_common, confidence=0.90, bbox=bbox)

        return TrafficLightResult(state=detected_state, confidence=0.60, bbox=bbox)
