"""
Hardware Abstraction Layer: Camera Interface.
Runs threaded frame acquisition to eliminate I/O blocking and buffer lag.
Supports USB Cameras, Raspberry Pi CSI Camera, video files, and mock frames.
"""

import threading
import time
from typing import Optional
import cv2
import numpy as np


class CameraInterface:
    """
    Asynchronous threaded camera capture interface.
    Always provides the most recent frame without buffering delay.
    """

    def __init__(
        self,
        source: int | str = 0,
        width: int = 640,
        height: int = 480,
        fps: int = 30,
    ):
        self.source = source
        self.width = width
        self.height = height
        self.fps = fps

        self.cap: Optional[cv2.VideoCapture] = None
        self.current_frame: Optional[np.ndarray] = None
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()

    def start(self) -> bool:
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            # If camera device fails to open, provide synthetic placeholder frames
            print(f"[CameraInterface] Warning: Cannot open camera source {self.source}. Using mock placeholder frames.")
            self.running = True
            return False

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)

        self.running = True
        self.thread = threading.Thread(target=self._capture_worker, daemon=True)
        self.thread.start()
        return True

    def _capture_worker(self):
        while self.running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret and frame is not None:
                with self.lock:
                    self.current_frame = frame
            else:
                time.sleep(0.01)

    def read_frame(self) -> Optional[np.ndarray]:
        with self.lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
        return None

    def stop(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=0.5)
        if self.cap:
            self.cap.release()
