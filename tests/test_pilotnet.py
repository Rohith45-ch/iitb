"""Unit tests for PilotNetController end-to-end steering."""

import unittest
import numpy as np
from uamc.control.pilotnet_controller import PilotNetController


class TestPilotNetController(unittest.TestCase):
    def setUp(self):
        self.controller = PilotNetController()

    def test_unloaded_model_graceful_fallback(self):
        controller = PilotNetController(model_path="non_existent.onnx")
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        steer_norm, steer_deg = controller.predict_steering(frame)
        self.assertEqual(steer_norm, 0.0)
        self.assertEqual(steer_deg, 0.0)

    def test_preprocess_output_shape(self):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        tensor = self.controller.preprocess(frame)
        self.assertEqual(tensor.shape, (1, 3, 66, 200))
        self.assertEqual(tensor.dtype, np.float32)

    def test_model_inference_and_clamping(self):
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        steer_norm, steer_deg = self.controller.predict_steering(frame)
        self.assertTrue(-1.0 <= steer_norm <= 1.0)
        self.assertTrue(-25.0 <= steer_deg <= 25.0)


if __name__ == "__main__":
    unittest.main()
