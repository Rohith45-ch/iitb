"""
Hardware Abstraction Layer: Mock / Virtual Hardware Interface.
Allows full end-to-end testing and simulation on any developer laptop.
"""

import time
import numpy as np
from uamc.hal.serial_bridge import TelemetryPacket


class MockHardwareInterface:
    """
    Virtual hardware simulator mimicking vehicle kinematics, encoder integration,
    and obstacle presence.
    """

    def __init__(self):
        self.simulated_speed = 0.0
        self.simulated_heading = 0.0
        self.simulated_x = 0.0
        self.simulated_y = 0.0
        self.obstacle_distance = 2.0
        self.estop_pressed = False
        self.last_update = time.time()

    def update(self, steering_norm: float, throttle_norm: float, dt: float):
        # Scale throttle to speed
        target_v = throttle_norm * 0.50
        self.simulated_speed += (target_v - self.simulated_speed) * min(1.0, 4.0 * dt)
        if throttle_norm < 0:
            self.simulated_speed = max(0.0, self.simulated_speed - 2.0 * dt)

        # Steering to yaw
        steer_rad = steering_norm * np.radians(28.0)
        yaw_rate = (self.simulated_speed / 0.260) * np.tan(steer_rad)
        self.simulated_heading += np.degrees(yaw_rate * dt)

        # Update position
        self.simulated_x += self.simulated_speed * np.sin(np.radians(self.simulated_heading)) * dt
        self.simulated_y += self.simulated_speed * np.cos(np.radians(self.simulated_heading)) * dt

    def get_telemetry(self) -> TelemetryPacket:
        return TelemetryPacket(
            timestamp=time.time(),
            ultrasonic_left_m=float(self.obstacle_distance),
            ultrasonic_center_m=float(self.obstacle_distance),
            ultrasonic_right_m=float(self.obstacle_distance),
            ultrasonic_side_m=0.18,
            encoder_ticks_left=int(self.simulated_y * 1000),
            encoder_ticks_right=int(self.simulated_y * 1000),
            yaw_deg=float(self.simulated_heading),
            is_hardware_estop_pressed=self.estop_pressed,
        )

    def set_mock_obstacle(self, distance_m: float):
        self.obstacle_distance = distance_m
