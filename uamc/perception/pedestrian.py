"""
Pedestrian and Zebra Crossing Detection Module.
Detects periodic white stripe patterns on the road surface denoting zebra pedestrian crossings,
and tracks pedestrian figures / props in or approaching the crossing.
"""

from dataclasses import dataclass
from typing import Optional, Tuple
import cv2
import numpy as np


@dataclass
class PedestrianCrossingResult:
    crossing_detected: bool
    distance_to_crossing_m: float
    pedestrian_present: bool
    debug_bbox: Optional[Tuple[int, int, int, int]] = None


class PedestrianDetector:
    """
    Identifies high-frequency alternating light/dark horizontal bands on the road plane
    representing zebra pedestrian crossings, as well as pedestrian props.
    """

    def __init__(self, image_width: int = 640, image_height: int = 480):
        self.width = image_width
        self.height = image_height

    def detect(self, frame: np.ndarray) -> PedestrianCrossingResult:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        # Zebra crossings lie in lower 50% of the camera image
        road_roi = gray[int(h * 0.50) : int(h * 0.90), int(w * 0.20) : int(w * 0.80)]
        _, thresh = cv2.threshold(road_roi, 190, 255, cv2.THRESH_BINARY)

        # Morphological horizontal filtering to find alternating stripe bars
        stripe_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
        filtered = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, stripe_kernel)

        contours, _ = cv2.findContours(filtered, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Count parallel stripe-like blobs
        stripe_count = 0
        min_y = 1000
        for cnt in contours:
            x, y, bw, bh = cv2.boundingRect(cnt)
            aspect = float(bw) / float(bh + 1e-5)
            area = cv2.contourArea(cnt)
            if 1.5 < aspect < 8.0 and 80 < area < 5000:
                stripe_count += 1
                if y < min_y:
                    min_y = y

        crossing_detected = stripe_count >= 3
        distance_to_crossing = 10.0

        if crossing_detected:
            # Distance inversely proportional to vertical position in ROI
            y_norm = 1.0 - (min_y / float(road_roi.shape[0]))
            distance_to_crossing = float(0.20 + y_norm * 0.60)

        # Check for pedestrian figure standing at or within crossing zone
        pedestrian_present = False
        if crossing_detected:
            # Check for non-road vertical silhouettes above or on crossing
            upper_roi = gray[int(h * 0.35) : int(h * 0.65), int(w * 0.15) : int(w * 0.85)]
            edges = cv2.Canny(upper_roi, 60, 150)
            if cv2.countNonZero(edges) > 600:
                pedestrian_present = True

        return PedestrianCrossingResult(
            crossing_detected=crossing_detected,
            distance_to_crossing_m=distance_to_crossing,
            pedestrian_present=pedestrian_present,
        )
