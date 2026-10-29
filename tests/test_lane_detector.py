"""Unit tests for LaneDetector module."""

import unittest
import numpy as np
from uamc.perception.lane_detector import LaneDetector
from uamc.simulation.synthetic_track import SyntheticTrackSimulator


class TestLaneDetector(unittest.TestCase):
    def setUp(self):
        self.detector = LaneDetector(image_width=640, image_height=480)
        self.sim = SyntheticTrackSimulator(width=640, height=480)

    def test_centered_lane_detection(self):
        # Render a perfectly centered lane
        frame = self.sim.render_frame(lateral_offset_m=0.0, heading_angle_deg=0.0)
        result = self.detector.detect_lanes(frame)

        self.assertTrue(result.is_valid, "Lane detection should be valid on synthetic road")
        self.assertAlmostEqual(result.lateral_offset_m, 0.0, delta=0.05, msg="Offset should be near zero")
        self.assertIsNotNone(result.debug_frame)

    def test_right_offset_lane_detection(self):
        # Car is 5 cm to the right of lane center
        frame = self.sim.render_frame(lateral_offset_m=-0.05, heading_angle_deg=0.0)
        result = self.detector.detect_lanes(frame)

        self.assertTrue(result.is_valid)
        self.assertLess(result.lateral_offset_m, 0.0, "Offset should be negative when car is right of center")

    def test_empty_black_frame(self):
        # Completely blank frame should be safely handled as invalid
        blank = np.zeros((480, 640, 3), dtype=np.uint8)
        result = self.detector.detect_lanes(blank)
        self.assertFalse(result.is_valid)


if __name__ == "__main__":
    unittest.main()
