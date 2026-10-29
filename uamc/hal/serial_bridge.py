"""
Hardware Abstraction Layer: Serial Communication Bridge.
Transmits steering servo and motor throttle commands to Arduino/ESP32 via UART,
and parses incoming sensor telemetry packets (ultrasonic ranges, encoder ticks, IMU).
"""

import threading
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class TelemetryPacket:
    timestamp: float
    ultrasonic_left_m: float
    ultrasonic_center_m: float
    ultrasonic_right_m: float
    ultrasonic_side_m: float
    encoder_ticks_left: int
    encoder_ticks_right: int
    yaw_deg: float
    is_hardware_estop_pressed: bool


class SerialBridge:
    """
    Manages robust serial protocol to the microcontroller.
    Packet Format (SBC -> MCU): `#CMD,<steer_norm>,<throttle_norm>,<estop_flag>*\n`
    Packet Format (MCU -> SBC): `#TEL,<us_l>,<us_c>,<us_r>,<us_s>,<enc_l>,<enc_r>,<yaw>,<estop>*\n`
    """

    def __init__(
        self,
        port: str = "/dev/ttyUSB0",
        baudrate: int = 115200,
        timeout: float = 0.05,
    ):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout

        self.serial_conn = None
        self.is_connected = False
        self.latest_telemetry = TelemetryPacket(
            timestamp=time.time(),
            ultrasonic_left_m=2.0,
            ultrasonic_center_m=2.0,
            ultrasonic_right_m=2.0,
            ultrasonic_side_m=0.15,
            encoder_ticks_left=0,
            encoder_ticks_right=0,
            yaw_deg=0.0,
            is_hardware_estop_pressed=False,
        )

        self.lock = threading.Lock()
        self.running = False
        self.thread: Optional[threading.Thread] = None

    def connect(self) -> bool:
        try:
            import serial
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            self.is_connected = True
            self.running = True
            self.thread = threading.Thread(target=self._rx_worker, daemon=True)
            self.thread.start()
            print(f"[SerialBridge] Connected to MCU on {self.port} at {self.baudrate} baud.")
            return True
        except Exception as e:
            print(f"[SerialBridge] Serial port {self.port} not found ({e}). Running in loopback/sim mode.")
            self.is_connected = False
            return False

    def send_actuator_command(
        self,
        steering_normalized: float,
        throttle_normalized: float,
        estop: bool = False,
    ):
        """Sends control command packet to Arduino/ESP32."""
        packet = f"#CMD,{steering_normalized:.3f},{throttle_normalized:.3f},{1 if estop else 0}*\n"
        if self.is_connected and self.serial_conn:
            try:
                self.serial_conn.write(packet.encode("ascii"))
            except Exception as e:
                print(f"[SerialBridge] Send error: {e}")

    def get_telemetry(self) -> TelemetryPacket:
        with self.lock:
            return self.latest_telemetry

    def _rx_worker(self):
        while self.running and self.serial_conn:
            try:
                line = self.serial_conn.readline().decode("ascii", errors="ignore").strip()
                if line.startswith("#TEL,") and line.endswith("*"):
                    payload = line[5:-1].split(",")
                    if len(payload) == 8:
                        with self.lock:
                            self.latest_telemetry = TelemetryPacket(
                                timestamp=time.time(),
                                ultrasonic_left_m=float(payload[0]),
                                ultrasonic_center_m=float(payload[1]),
                                ultrasonic_right_m=float(payload[2]),
                                ultrasonic_side_m=float(payload[3]),
                                encoder_ticks_left=int(payload[4]),
                                encoder_ticks_right=int(payload[5]),
                                yaw_deg=float(payload[6]),
                                is_hardware_estop_pressed=(payload[7] == "1"),
                            )
            except Exception:
                time.sleep(0.01)

    def close(self):
        self.running = False
        if self.serial_conn:
            self.serial_conn.close()
