"""
NVIDIA PilotNet End-to-End Neural Steering Controller.
Predicts lateral steering commands directly from front camera frames
using the lightweight pilotnet_steering.onnx neural network.
"""

from pathlib import Path
from typing import Optional, Tuple
import cv2
import numpy as np

try:
    import onnxruntime as ort
    HAS_ORT = True
except ImportError:
    HAS_ORT = False


class PilotNetController:
    """
    End-to-End Neural Steering Controller running on Raspberry Pi.
    Maps raw road image pixels directly to steering commands.
    """

    INPUT_WIDTH = 200
    INPUT_HEIGHT = 66

    def __init__(
        self,
        model_path: Optional[str] = None,
        max_steer_angle_deg: float = 25.0,
        smoothing_factor: float = 0.20,
    ):
        self.max_steer_angle = max_steer_angle_deg
        self.alpha = smoothing_factor  # Low-pass exponential smoothing
        self.last_steer = 0.0
        self.session = None
        self.input_name = None
        self.model_loaded = False

        if model_path is None:
            default_path = Path(__file__).resolve().parent.parent.parent / "models" / "pilotnet_steering.onnx"
            if default_path.exists():
                model_path = str(default_path)

        if model_path and Path(model_path).exists() and HAS_ORT:
            self.load_model(model_path)

    def load_model(self, model_path: str) -> bool:
        """Loads PilotNet ONNX model for CPU inference."""
        try:
            opts = ort.SessionOptions()
            opts.intra_op_num_threads = 2
            opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            self.session = ort.InferenceSession(
                model_path,
                sess_options=opts,
                providers=["CPUExecutionProvider"],
            )
            self.input_name = self.session.get_inputs()[0].name
            self.model_loaded = True
            print(f"[PilotNetController] Successfully loaded model: {model_path}")
            return True
        except Exception as e:
            print(f"[PilotNetController] Failed to load model: {e}")
            self.model_loaded = False
            return False

    def preprocess(self, frame: np.ndarray) -> np.ndarray:
        """
        Crops road region of interest, resizes to (200, 66),
        normalizes to [0.0, 1.0], and transposes to [1, 3, 66, 200].
        """
        h, w, _ = frame.shape
        # Crop to lower road portion (avoid ceiling lights and background)
        roi = frame[int(h * 0.35) : int(h * 0.95), :]
        resized = cv2.resize(roi, (self.INPUT_WIDTH, self.INPUT_HEIGHT), interpolation=cv2.INTER_AREA)
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        tensor = rgb.transpose((2, 0, 1))[np.newaxis, ...].astype(np.float32) / 255.0
        return tensor

    def predict_steering(self, frame: np.ndarray) -> Tuple[float, float]:
        """
        Runs forward inference.
        Returns:
            normalized_steer: [-1.0 (hard left), +1.0 (hard right)]
            steer_angle_deg: [-25.0 deg, +25.0 deg]
        """
        if not self.model_loaded or self.session is None:
            return 0.0, 0.0

        tensor = self.preprocess(frame)
        raw_output = self.session.run(None, {self.input_name: tensor})[0]
        raw_steer = float(raw_output[0, 0])

        # Clamp between -1.0 and +1.0
        clamped_steer = max(-1.0, min(1.0, raw_steer))

        # Exponential low-pass filter to prevent steering jitter
        smoothed_steer = self.alpha * clamped_steer + (1.0 - self.alpha) * self.last_steer
        self.last_steer = smoothed_steer

        steer_angle_deg = smoothed_steer * self.max_steer_angle
        return smoothed_steer, steer_angle_deg
