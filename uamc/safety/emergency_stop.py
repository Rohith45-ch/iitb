"""
Safety Watchdog and Emergency Stop (E-Stop) Manager.
Monitors system health, sensor freshness, and heartbeat intervals.
If any critical subsystem stalls or communication times out, forces immediate failsafe stop.
"""

import time
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class SafetyStatus:
    is_safe: bool
    estop_active: bool
    reason: str
    last_heartbeat_age_ms: float


class EmergencyStopManager:
    """
    Manages safety assertions and software E-stop.
    Enforces a strict heartbeat window (e.g. 150 ms) to prevent runaway conditions.
    """

    def __init__(self, heartbeat_timeout_s: float = 0.20):
        self.timeout_s = heartbeat_timeout_s
        self.last_heartbeat_time = time.time()
        self.manual_estop_triggered = False
        self.subsystem_timestamps: Dict[str, float] = {}

    def trigger_estop(self, reason: str = "Manual E-Stop Activated"):
        self.manual_estop_triggered = True

    def reset_estop(self):
        self.manual_estop_triggered = False
        self.last_heartbeat_time = time.time()

    def record_subsystem_heartbeat(self, subsystem: str):
        self.subsystem_timestamps[subsystem] = time.time()

    def evaluate(self) -> SafetyStatus:
        now = time.time()
        heartbeat_age = now - self.last_heartbeat_time
        heartbeat_age_ms = heartbeat_age * 1000.0

        if self.manual_estop_triggered:
            return SafetyStatus(
                is_safe=False,
                estop_active=True,
                reason="Manual E-Stop Button Activated",
                last_heartbeat_age_ms=heartbeat_age_ms,
            )

        if heartbeat_age > self.timeout_s:
            return SafetyStatus(
                is_safe=False,
                estop_active=True,
                reason=f"Safety Watchdog Timeout ({heartbeat_age_ms:.1f}ms > {self.timeout_s*1000}ms)",
                last_heartbeat_age_ms=heartbeat_age_ms,
            )

        # Check freshness of critical camera and sensor inputs
        for sub, ts in self.subsystem_timestamps.items():
            if (now - ts) > 0.50:  # Sensor data older than 500ms
                return SafetyStatus(
                    is_safe=False,
                    estop_active=True,
                    reason=f"Sensor Stale: '{sub}' has not updated for {(now-ts)*1000:.1f}ms",
                    last_heartbeat_age_ms=heartbeat_age_ms,
                )

        return SafetyStatus(
            is_safe=True,
            estop_active=False,
            reason="All Safety Systems Nominal",
            last_heartbeat_age_ms=heartbeat_age_ms,
        )

    def ping(self):
        self.last_heartbeat_time = time.time()
