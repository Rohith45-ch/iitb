"""
Autonomous Parking Bay Detection Module.
Detects perpendicular and parallel parking bay boundaries and open slots
using lateral sensor ranging and camera boundary line geometry.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional
import numpy as np


class ParkingSlotState(Enum):
    SEARCHING = "searching"
    SLOT_FOUND = "slot_found"
    ALIGNING = "aligning"
    PARKED = "parked"


@dataclass
class ParkingDetection:
    state: ParkingSlotState
    slot_depth_m: float
    slot_length_m: float
    is_slot_open: bool


class ParkingDetector:
    """
    Scans the right flank of the vehicle as it drives past parking bays,
    measuring the opening width and verifying absence of parked vehicles.
    """

    def __init__(
        self,
        min_slot_length_m: float = 0.50,  # Min length for 1:10 scale car (~42cm car)
        required_slot_depth_m: float = 0.25,
    ):
        self.min_length = min_slot_length_m
        self.required_depth = required_slot_depth_m
        self.slot_start_odom = None

    def evaluate_flank(
        self,
        side_range_m: float,
        current_odometry_m: float,
    ) -> ParkingDetection:
        # A free parking bay shows an abrupt jump in lateral distance (> 25cm opening)
        in_gap = side_range_m >= self.required_depth

        if in_gap:
            if self.slot_start_odom is None:
                self.slot_start_odom = current_odometry_m
            gap_length = current_odometry_m - self.slot_start_odom
            if gap_length >= self.min_length:
                return ParkingDetection(
                    state=ParkingSlotState.SLOT_FOUND,
                    slot_depth_m=side_range_m,
                    slot_length_m=gap_length,
                    is_slot_open=True,
                )
        else:
            self.slot_start_odom = None

        return ParkingDetection(
            state=ParkingSlotState.SEARCHING,
            slot_depth_m=side_range_m,
            slot_length_m=0.0,
            is_slot_open=False,
        )
