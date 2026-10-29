"""
Longitudinal Velocity Controller (PID with Anti-Windup & Feedforward).
Translates target velocity into motor throttle PWM commands.
"""

from dataclasses import dataclass
import numpy as np


@dataclass
class ThrottleControlOutput:
    throttle_pwm_normalized: float  # -1.0 (full reverse / brake) to +1.0 (full forward)
    is_braking: bool
    current_velocity_error: float


class LongitudinalPIDController:
    """
    Discrete PID speed controller with integral anti-windup and feedforward gain.
    """

    def __init__(
        self,
        kp: float = 1.80,
        ki: float = 0.45,
        kd: float = 0.08,
        k_ff: float = 0.50,
        max_integral: float = 0.50,
    ):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.k_ff = k_ff
        self.max_integral = max_integral

        self.integral = 0.0
        self.prev_error = 0.0

    def compute_throttle(
        self,
        target_velocity_ms: float,
        measured_velocity_ms: float,
        dt: float,
    ) -> ThrottleControlOutput:
        # If commanded stop (target = 0.0), reset integrator and apply braking
        if target_velocity_ms <= 0.001:
            self.integral = 0.0
            self.prev_error = 0.0
            is_braking = measured_velocity_ms > 0.05
            brake_cmd = -0.5 if is_braking else 0.0
            return ThrottleControlOutput(
                throttle_pwm_normalized=brake_cmd,
                is_braking=is_braking,
                current_velocity_error=-measured_velocity_ms,
            )

        error = target_velocity_ms - measured_velocity_ms

        # Integral with anti-windup clamping
        if dt > 0.0:
            self.integral += error * dt
            self.integral = float(np.clip(self.integral, -self.max_integral, self.max_integral))
            derivative = (error - self.prev_error) / dt
        else:
            derivative = 0.0

        self.prev_error = error

        # Feedforward + PID
        u = (
            self.k_ff * target_velocity_ms
            + self.kp * error
            + self.ki * self.integral
            + self.kd * derivative
        )

        throttle_clamped = float(np.clip(u, -1.0, 1.0))
        is_braking = throttle_clamped < 0.0

        return ThrottleControlOutput(
            throttle_pwm_normalized=throttle_clamped,
            is_braking=is_braking,
            current_velocity_error=error,
        )

    def reset(self):
        self.integral = 0.0
        self.prev_error = 0.0
