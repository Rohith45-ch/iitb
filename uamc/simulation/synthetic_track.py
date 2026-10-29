"""
Synthetic Track and Virtual Camera Generator.
Renders synthetic 3D perspective camera frames of a miniature urban road network
with white boundaries, yellow centerlines, stop signs, and obstacles.
Enables full closed-loop simulation on a developer laptop without physical hardware!
"""

from typing import Optional
import cv2
import numpy as np


class SyntheticTrackSimulator:
    """
    Renders realistic camera frames corresponding to the vehicle's position on the track.
    """

    def __init__(self, width: int = 640, height: int = 480):
        self.width = width
        self.height = height

    def render_frame(
        self,
        lateral_offset_m: float = 0.0,
        heading_angle_deg: float = 0.0,
        curve_curvature: float = 0.0,
        show_stop_sign: bool = False,
        show_obstacle_dist_m: Optional[float] = None,
        traffic_light_color: Optional[str] = None,  # "red", "yellow", "green"
    ) -> np.ndarray:
        # Create dark road asphalt canvas
        frame = np.full((self.height, self.width, 3), (35, 35, 35), dtype=np.uint8)

        # Offsets in pixels (320px per 0.35m lane)
        px_per_m = 320.0 / 0.35
        dx_px = int(lateral_offset_m * px_per_m)
        heading_shift_px = int(np.tan(np.radians(heading_angle_deg)) * 200)

        # Draw perspective lanes
        # Vanishing point
        vp_y = int(self.height * 0.40)
        vp_x = int(self.width / 2.0) - heading_shift_px

        # Base lane positions at bottom of image
        center_x = int(self.width / 2.0) - dx_px
        lane_half_width = int(0.175 * px_per_m)

        left_bottom = center_x - lane_half_width
        right_bottom = center_x + lane_half_width

        # Perspective line drawing
        # Left boundary (white solid line)
        cv2.line(frame, (left_bottom, self.height), (vp_x - 40, vp_y), (240, 240, 240), 8)

        # Right boundary (white solid line)
        cv2.line(frame, (right_bottom, self.height), (vp_x + 40, vp_y), (240, 240, 240), 8)

        # Center line (yellow dashed)
        for y_step in range(self.height, vp_y + 20, -45):
            t1 = (y_step - vp_y) / float(self.height - vp_y)
            t2 = (y_step - 25 - vp_y) / float(self.height - vp_y)
            x1 = int(vp_x + (center_x - vp_x) * t1)
            x2 = int(vp_x + (center_x - vp_x) * t2)
            cv2.line(frame, (x1, y_step), (x2, y_step - 25), (0, 215, 255), 6)

        # Render Stop Sign if requested
        if show_stop_sign:
            sign_x, sign_y = int(self.width * 0.75), int(self.height * 0.45)
            # Octagon
            pts = np.array([
                [sign_x - 15, sign_y - 35],
                [sign_x + 15, sign_y - 35],
                [sign_x + 35, sign_y - 15],
                [sign_x + 35, sign_y + 15],
                [sign_x + 15, sign_y + 35],
                [sign_x - 15, sign_y + 35],
                [sign_x - 35, sign_y + 15],
                [sign_x - 35, sign_y - 15],
            ], np.int32)
            cv2.fillPoly(frame, [pts], (0, 0, 220))
            cv2.polylines(frame, [pts], True, (255, 255, 255), 2)
            cv2.putText(frame, "STOP", (sign_x - 22, sign_y + 6), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 2)

        # Render Obstacle if present
        if show_obstacle_dist_m is not None and show_obstacle_dist_m < 2.0:
            # Scale box height and position based on distance
            d_norm = max(0.1, min(2.0, show_obstacle_dist_m)) / 2.0
            obs_y = int(self.height * 0.85 - (1.0 - d_norm) * (self.height * 0.35))
            obs_w = int(70 * (1.1 - d_norm))
            obs_h = int(60 * (1.1 - d_norm))
            obs_x = center_x - obs_w // 2

            cv2.rectangle(frame, (obs_x, obs_y - obs_h), (obs_x + obs_w, obs_y), (0, 140, 255), -1)
            cv2.rectangle(frame, (obs_x, obs_y - obs_h), (obs_x + obs_w, obs_y), (0, 0, 0), 2)

        # Render Traffic Light if specified
        if traffic_light_color:
            tl_x, tl_y = int(self.width * 0.20), int(self.height * 0.35)
            cv2.rectangle(frame, (tl_x - 12, tl_y - 30), (tl_x + 12, tl_y + 30), (20, 20, 20), -1)
            # Red light
            r_col = (0, 0, 255) if traffic_light_color == "red" else (0, 0, 60)
            cv2.circle(frame, (tl_x, tl_y - 18), 7, r_col, -1)
            # Yellow light
            y_col = (0, 220, 255) if traffic_light_color == "yellow" else (0, 60, 60)
            cv2.circle(frame, (tl_x, tl_y), 7, y_col, -1)
            # Green light
            g_col = (0, 255, 0) if traffic_light_color == "green" else (0, 60, 0)
            cv2.circle(frame, (tl_x, tl_y + 18), 7, g_col, -1)

        return frame
