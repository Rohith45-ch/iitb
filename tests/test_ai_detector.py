"""Unit tests for EdgeAIDetector module."""

import unittest
import numpy as np
from uamc.perception.ai_detector import EdgeAIDetector


class TestEdgeAIDetector(unittest.TestCase):
    def setUp(self):
        self.detector = EdgeAIDetector(model_path=None)

    def test_unloaded_model_graceful_fallback(self):
        # When no ONNX weights are loaded, detector should gracefully return empty list without crashing
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections = self.detector.detect(frame)
        self.assertEqual(len(detections), 0)

    def test_draw_detections_clean_render(self):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        rendered = self.detector.draw_detections(frame, [])
        self.assertEqual(rendered.shape, (480, 640, 3))


if __name__ == "__main__":
    unittest.main()
