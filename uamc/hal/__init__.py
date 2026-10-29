"""Hardware Abstraction Layer (HAL) for UAMC autonomous vehicle."""

from uamc.hal.camera_interface import CameraInterface
from uamc.hal.serial_bridge import SerialBridge, TelemetryPacket
from uamc.hal.mock_hal import MockHardwareInterface

__all__ = [
    "CameraInterface",
    "SerialBridge",
    "TelemetryPacket",
    "MockHardwareInterface",
]
