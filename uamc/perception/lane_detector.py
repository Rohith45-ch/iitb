"""
Lane Detection and Inverse Perspective Mapping (IPM) Module.
Extracts left and right lane boundaries, fits 2nd order polynomials,
and computes vehicle lateral offset and road curvature.
"""

from dataclasses import dataclass
from typing import Optional, Tuple
import cv2
import numpy as np


@dataclass
class LaneResult:
    """Stores the output of lane detection for one frame."""
    is_valid: bool
    lateral_offset_m: float  # Negative: vehicle is right of center; Positive: left of center
    curvature_radius_m: float
    heading_error_rad: float
    debug_frame: np.ndarray
    left_fit: Optional[np.ndarray] = None
    right_fit: Optional[np.ndarray] = None


class LaneDetector:
    """
    Performs Bird's-Eye View (IPM) transformation, color/edge thresholding,
    sliding-window polynomial fitting, and lane state estimation.
    """

    def __init__(
        self,
        image_width: int = 640,
        image_height: int = 480,
        lane_width_m: float = 0.35,
        meters_per_pixel_x: float = 0.35 / 320.0,
        meters_per_pixel_y: float = 0.60 / 480.0,
    ):
        self.width = image_width
        self.height = image_height
        self.lane_width_m = lane_width_m
        self.xm_per_pix = meters_per_pixel_x
        self.ym_per_pix = meters_per_pixel_y

        # Perspective Transform Setup (IPM)
        # Source points in perspective camera image (trapezoid on ground)
        src = np.float32([
            [int(self.width * 0.15), int(self.height * 0.95)],  # Bottom-left
            [int(self.width * 0.85), int(self.height * 0.95)],  # Bottom-right
            [int(self.width * 0.60), int(self.height * 0.55)],  # Top-right
            [int(self.width * 0.40), int(self.height * 0.55)],  # Top-left
        ])

        # Destination points in top-down bird's-eye view (rectangle)
        dst = np.float32([
            [int(self.width * 0.25), self.height],
            [int(self.width * 0.75), self.height],
            [int(self.width * 0.75), 0],
            [int(self.width * 0.25), 0],
        ])

        self.M = cv2.getPerspectiveTransform(src, dst)
        self.Minv = cv2.getPerspectiveTransform(dst, src)

        # Sliding window parameters
        self.n_windows = 9
        self.margin = 50
        self.min_pixels = 40

        # Memory / Filtering for temporal stability
        self.prev_left_fit = None
        self.prev_right_fit = None

    def warp_to_birds_eye(self, image: np.ndarray) -> np.ndarray:
        """Transforms camera perspective view into top-down bird's-eye view."""
        return cv2.warpPerspective(image, self.M, (self.width, self.height), flags=cv2.INTER_LINEAR)

    def threshold_road(self, warped: np.ndarray) -> np.ndarray:
        """
        Extracts white lane boundaries and yellow dividing markings using HSV and Sobel filtering.
        """
        hsv = cv2.cvtColor(warped, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)

        # White lane mask (high brightness, low saturation)
        lower_white = np.array([0, 0, 180], dtype=np.uint8)
        upper_white = np.array([180, 50, 255], dtype=np.uint8)
        mask_white = cv2.inRange(hsv, lower_white, upper_white)

        # Yellow lane mask (Hue ~ 15-35, high saturation)
        lower_yellow = np.array([15, 80, 100], dtype=np.uint8)
        upper_yellow = np.array([35, 255, 255], dtype=np.uint8)
        mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)

        # Horizontal gradient (Sobel X) to capture line edges
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        abs_sobel64f = np.absolute(sobelx)
        scaled_sobel = np.uint8(255 * abs_sobel64f / (np.max(abs_sobel64f) + 1e-6))
        _, mask_sobel = cv2.threshold(scaled_sobel, 50, 255, cv2.THRESH_BINARY)

        combined = cv2.bitwise_or(mask_white, mask_yellow)
        combined = cv2.bitwise_or(combined, mask_sobel)

        # Morphological noise removal
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        filtered = cv2.morphologyEx(combined, cv2.MORPH_OPEN, kernel)
        return filtered

    def detect_lanes(self, frame: np.ndarray) -> LaneResult:
        """
        Main pipeline: Takes input camera BGR frame and returns estimated lane parameters.
        """
        warped = self.warp_to_birds_eye(frame)
        binary_warped = self.threshold_road(warped)

        # Find base starting points using bottom half histogram
        histogram = np.sum(binary_warped[self.height // 2 :, :], axis=0)
        midpoint = int(histogram.shape[0] // 2)

        leftx_base = np.argmax(histogram[:midpoint])
        rightx_base = np.argmax(histogram[midpoint:]) + midpoint

        # If histogram is mostly empty, fallback
        if histogram[leftx_base] < 100 and histogram[rightx_base] < 100:
            return LaneResult(
                is_valid=False,
                lateral_offset_m=0.0,
                curvature_radius_m=1000.0,
                heading_error_rad=0.0,
                debug_frame=frame,
            )

        # Identify non-zero pixel coordinates
        nonzero = binary_warped.nonzero()
        nonzeroy = np.array(nonzero[0])
        nonzerox = np.array(nonzero[1])

        leftx_current = leftx_base
        rightx_current = rightx_base

        window_height = int(self.height // self.n_windows)
        left_lane_inds = []
        right_lane_inds = []

        out_img = np.dstack((binary_warped, binary_warped, binary_warped))

        for window in range(self.n_windows):
            win_y_low = self.height - (window + 1) * window_height
            win_y_high = self.height - window * window_height

            win_xleft_low = leftx_current - self.margin
            win_xleft_high = leftx_current + self.margin
            win_xright_low = rightx_current - self.margin
            win_xright_high = rightx_current + self.margin

            cv2.rectangle(
                out_img,
                (win_xleft_low, win_y_low),
                (win_xleft_high, win_y_high),
                (0, 255, 0),
                2,
            )
            cv2.rectangle(
                out_img,
                (win_xright_low, win_y_low),
                (win_xright_high, win_y_high),
                (0, 255, 0),
                2,
            )

            good_left_inds = (
                (nonzeroy >= win_y_low)
                & (nonzeroy < win_y_high)
                & (nonzerox >= win_xleft_low)
                & (nonzerox < win_xleft_high)
            ).nonzero()[0]
            good_right_inds = (
                (nonzeroy >= win_y_low)
                & (nonzeroy < win_y_high)
                & (nonzerox >= win_xright_low)
                & (nonzerox < win_xright_high)
            ).nonzero()[0]

            left_lane_inds.append(good_left_inds)
            right_lane_inds.append(good_right_inds)

            if len(good_left_inds) > self.min_pixels:
                leftx_current = int(np.mean(nonzerox[good_left_inds]))
            if len(good_right_inds) > self.min_pixels:
                rightx_current = int(np.mean(nonzerox[good_right_inds]))

        left_lane_inds = np.concatenate(left_lane_inds)
        right_lane_inds = np.concatenate(right_lane_inds)

        leftx = nonzerox[left_lane_inds]
        lefty = nonzeroy[left_lane_inds]
        rightx = nonzerox[right_lane_inds]
        righty = nonzeroy[right_lane_inds]

        left_fit = None
        right_fit = None

        if len(leftx) > 100:
            left_fit = np.polyfit(lefty, leftx, 2)
            self.prev_left_fit = left_fit
        elif self.prev_left_fit is not None:
            left_fit = self.prev_left_fit

        if len(rightx) > 100:
            right_fit = np.polyfit(righty, rightx, 2)
            self.prev_right_fit = right_fit
        elif self.prev_right_fit is not None:
            right_fit = self.prev_right_fit

        if left_fit is None and right_fit is None:
            return LaneResult(
                is_valid=False,
                lateral_offset_m=0.0,
                curvature_radius_m=1000.0,
                heading_error_rad=0.0,
                debug_frame=frame,
            )

        # Synthesize missing line if only one side is detected using known lane width
        expected_lane_px = int(self.lane_width_m / self.xm_per_pix)
        if left_fit is not None and right_fit is None:
            right_fit = left_fit.copy()
            right_fit[2] += expected_lane_px
        elif right_fit is not None and left_fit is None:
            left_fit = right_fit.copy()
            left_fit[2] -= expected_lane_px

        # Compute lateral offset from vehicle center (camera center at bottom of image)
        y_eval = float(self.height)
        left_x_bottom = left_fit[0] * (y_eval**2) + left_fit[1] * y_eval + left_fit[2]
        right_x_bottom = right_fit[0] * (y_eval**2) + right_fit[1] * y_eval + right_fit[2]
        lane_center_x = (left_x_bottom + right_x_bottom) / 2.0
        vehicle_center_x = self.width / 2.0

        lateral_offset_px = lane_center_x - vehicle_center_x
        lateral_offset_m = float(lateral_offset_px * self.xm_per_pix)

        # Heading error from tangent of polynomial at bottom of image
        center_poly = (left_fit + right_fit) / 2.0
        tangent_slope = 2 * center_poly[0] * y_eval + center_poly[1]
        heading_error_rad = float(np.arctan(tangent_slope))

        # Radius of curvature in meters
        y_eval_m = y_eval * self.ym_per_pix
        fit_cr = np.polyfit(
            np.linspace(0, self.height, 10) * self.ym_per_pix,
            (
                center_poly[0] * (np.linspace(0, self.height, 10) ** 2)
                + center_poly[1] * np.linspace(0, self.height, 10)
                + center_poly[2]
            )
            * self.xm_per_pix,
            2,
        )
        curverad = (
            (1 + (2 * fit_cr[0] * y_eval_m + fit_cr[1]) ** 2) ** 1.5
        ) / (np.absolute(2 * fit_cr[0]) + 1e-6)

        # Render debug overlay on original perspective frame
        debug_frame = self._render_overlay(frame, left_fit, right_fit, lateral_offset_m, curverad)

        return LaneResult(
            is_valid=True,
            lateral_offset_m=lateral_offset_m,
            curvature_radius_m=float(curverad),
            heading_error_rad=heading_error_rad,
            debug_frame=debug_frame,
            left_fit=left_fit,
            right_fit=right_fit,
        )

    def _render_overlay(
        self,
        frame: np.ndarray,
        left_fit: np.ndarray,
        right_fit: np.ndarray,
        lateral_offset: float,
        radius: float,
    ) -> np.ndarray:
        """Draws detected lane boundary polygon and metrics on top of the original image."""
        ploty = np.linspace(0, self.height - 1, self.height)
        left_fitx = left_fit[0] * ploty**2 + left_fit[1] * ploty + left_fit[2]
        right_fitx = right_fit[0] * ploty**2 + right_fit[1] * ploty + right_fit[2]

        warp_zero = np.zeros((self.height, self.width), dtype=np.uint8)
        color_warp = np.dstack((warp_zero, warp_zero, warp_zero))

        pts_left = np.array([np.transpose(np.vstack([left_fitx, ploty]))])
        pts_right = np.array([np.flipud(np.transpose(np.vstack([right_fitx, ploty])))])
        pts = np.hstack((pts_left, pts_right))

        # Fill drivable lane corridor in green
        cv2.fillPoly(color_warp, np.int_([pts]), (0, 180, 0))

        # Unwarp back to original camera view
        newwarp = cv2.warpPerspective(color_warp, self.Minv, (self.width, self.height))
        result = cv2.addWeighted(frame, 1.0, newwarp, 0.4, 0)

        # Text overlay
        cv2.putText(
            result,
            f"Offset: {lateral_offset:+.3f}m | Curve: {radius:.1f}m",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2,
        )
        return result
