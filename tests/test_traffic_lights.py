"""Unit tests for TrafficLightDetector module."""

import unittest
import cv2
import numpy as np
from uamc.perception.traffic_lights import LightState, TrafficLightDetector


class TestTrafficLightDetector(unittest.TestCase):
    def setUp(self):
        self.detector = TrafficLightDetector(debounce_frames=3)

    def test_black_frame_returns_unknown(self):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        result = self.detector.detect(frame)
        self.assertEqual(result.state, LightState.UNKNOWN)

    def test_red_light_synthetic_patch(self):
        # Create an image with an intense red patch in upper half
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # BGR: Red is (0, 0, 255)
        cv2.circle(frame, (320, 100), 25, (0, 0, 255), -1)

        # Feed 3 times to satisfy debounce queue
        for _ in range(3):
            result = self.detector.detect(frame)

        self.assertEqual(result.state, LightState.RED)

    def test_green_light_synthetic_patch(self):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # BGR: Green is (0, 255, 0)
        cv2.circle(frame, (320, 100), 25, (0, 255, 0), -1)

        for _ in range(3):
            result = self.detector.detect(frame)

        self.assertEqual(result.state, LightState.GREEN)

    def test_bbox_targeted_roi_detection(self):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        bbox = (300, 80, 50, 100)
        # Draw red lamp inside bbox
        cv2.circle(frame, (325, 100), 15, (0, 0, 255), -1)

        for _ in range(3):
            result = self.detector.detect(frame, bbox=bbox)

        self.assertEqual(result.state, LightState.RED)
        self.assertEqual(result.bbox, bbox)


if __name__ == "__main__":
    unittest.main()
