# UAMC Hardware Tuning & Calibration Blocks (Raspberry Pi & ESP32)

To make calibrating and tuning your autonomous vehicle fast and intuitive, all tunable parameters are cleanly isolated into two separate blocks:

1. **Raspberry Pi Block**: [`config/rpi_tuning.py`](file:///home/rohith/iitb/config/rpi_tuning.py) (High-Level Vision, Planning, and AI)
2. **ESP32 Block**: [`firmware/esp32_firmware/esp32_config.h`](file:///home/rohith/iitb/firmware/esp32_firmware/esp32_config.h) (Low-Level Actuation, PWM, Sonars, and Safety)

---

## **Block 1: Raspberry Pi Tuning Profile ([`config/rpi_tuning.py`](file:///home/rohith/iitb/config/rpi_tuning.py))**

Modify these settings when adjusting vision, camera angles, colors, AI models, or driving behavior.

### 1. Camera & Perspective Warp (IPM)
```python
# In config/rpi_tuning.py -> CameraConfig
src_trapezoid_fractions = [
    (0.12, 0.95),  # Bottom-Left
    (0.88, 0.95),  # Bottom-Right
    (0.62, 0.52),  # Top-Right
    (0.38, 0.52),  # Top-Left
]
```
* **When to tune**: If the bird's-eye view lane lines appear converging or curved on a straight road, adjust the top width `(0.38, 0.62)`. Run `python3 scripts/calibrate_camera.py` for live interactive trapezoid tuning.

### 2. Track & Lighting Color Thresholds (HSV)
```python
# In config/rpi_tuning.py -> ColorThresholdConfig
lane_white_min_hsv = (0, 0, 180)     # Increase V if bright arena reflections cause noise
lane_yellow_min_hsv = (18, 90, 120)  # Tweak Hue [18-35] to match arena center yellow line
light_debounce_frames = 4            # Number of frames of consensus before confirming Red/Green
```

### 3. Lateral Steering & Longitudinal Speed Control
```python
# In config/rpi_tuning.py -> VehicleControlConfig
wheelbase_m = 0.260           # Exact distance between front and rear axles (m)
lookahead_min_m = 0.28        # Lookahead distance at low speed (m)
lookahead_gain = 0.40         # Lookahead speed coefficient (l_d = k * v + l_d0)
kp_velocity = 1.80            # Motor speed PID Proportional gain
ki_velocity = 0.45            # Motor speed PID Integral gain
```
* **Steering Oscillation (Hunting)**: If the car violently wobbles side-to-side on straight paths, **increase `lookahead_min_m`** to `0.35`.
* **Cutting Corners**: If the car cuts inside corners too early, **decrease `lookahead_min_m`** to `0.24`.

### 4. Behavior Planning & Velocities
```python
# In config/rpi_tuning.py -> BehaviorPlannerConfig
v_cruise_ms = 0.45            # Main cruising speed (~1.6 km/h)
v_approach_ms = 0.25          # Slowdown speed near intersections & crosswalks
stop_sign_hold_time_s = 3.0   # Mandatory pause duration at stop line (seconds)
obstacle_emergency_dist_m = 0.25  # E-Stop trigger distance (meters)
```

---

## **Block 2: ESP32 Hardware Tuning Block ([`firmware/esp32_firmware/esp32_config.h`](file:///home/rohith/iitb/firmware/esp32_firmware/esp32_config.h))**

Modify these settings when trimming the steering servo, adjusting motor starting power, or tuning ultrasonic filters.

### 1. Steering Servo Center Trim
```cpp
// In firmware/esp32_firmware/esp32_config.h
#define SERVO_MIN_US             1000      // Full Left Steering (-28.0 deg)
#define SERVO_MID_US             1500      // Neutral Center Trim (0.0 deg)
#define SERVO_MAX_US             2000      // Full Right Steering (+28.0 deg)
```
* **Car Pulls to the Left when Driving Straight**: Increase `SERVO_MID_US` (e.g. `1530`).
* **Car Pulls to the Right when Driving Straight**: Decrease `SERVO_MID_US` (e.g. `1470`).

### 2. ESC Throttle Calibration (1/10 RC Drivetrain)
```cpp
// In firmware/esp32_firmware/esp32_config.h
#define USE_ESC_MOTOR_DRIVER     1         // 1 = RC ESC (Default), 0 = Dual H-Bridge
#define ESC_NEUTRAL_US           1500      // Neutral / stopped pulse width (us)
#define ESC_FORWARD_SAFE_CAP_US  1700      // Safe forward speed limiter for indoor testing (1500-2000 us)
#define ESC_DEADBAND_NORM        0.04f     // Throttle deadband around zero
```
* **Car Moves Too Fast Indoors**: Decrease `ESC_FORWARD_SAFE_CAP_US` to `1620` (gentler acceleration).
* **Motor Doesn't Move at Low Throttle**: Increase `ESC_DEADBAND_NORM` slightly or calibrate the ESC throttle range.

### 3. Ultrasonic Outlier & Multipath Filter
```cpp
// In firmware/esp32_firmware/esp32_config.h
#define US_FILTER_WINDOW_SIZE    5         // Median filter window (samples)
#define US_EMA_SMOOTHING_ALPHA   0.35f     // Exponential moving average weight
#define US_MAX_PHYSICAL_DELTA_M  0.30f     // Rate-of-change rejection threshold per cycle
```
* **Acoustic False Alarms**: If sonar triggers false stops from floor reflections, decrease `US_EMA_SMOOTHING_ALPHA` to `0.20f`.

### 4. TinyML Motion & Rollover Thresholds
```cpp
// In firmware/esp32_firmware/esp32_config.h
#define TINYML_COLLISION_G       2.8f      // Sudden jerk G-force for crash stop
#define TINYML_ROLLOVER_DEG      35.0f     // Chassis tilt angle threshold for rollover stop
#define WATCHDOG_TIMEOUT_MS      150       // Time before automatic safe stop if RPi disconnects
```

---

## **Quick Calibration Playbook**

| Symptom | Device | File to Open | Parameter to Change |
| :--- | :--- | :--- | :--- |
| **Car drifts left or right when given 0 steering** | ESP32 | [`esp32_config.h`](file:///home/rohith/iitb/firmware/esp32_firmware/esp32_config.h) | Adjust `SERVO_MID_US` by $\pm 20$–$50\mu s$ |
| **Car moves too fast during testing** | ESP32 | [`esp32_config.h`](file:///home/rohith/iitb/firmware/esp32_firmware/esp32_config.h) | Lower `ESC_FORWARD_SAFE_CAP_US` to `1620` |
| **Steering wiggles rapidly on straight track** | Raspberry Pi | [`rpi_tuning.py`](file:///home/rohith/iitb/config/rpi_tuning.py) | Increase `lookahead_min_m` to `0.32` |
| **Vehicle cuts corners too tight** | Raspberry Pi | [`rpi_tuning.py`](file:///home/rohith/iitb/config/rpi_tuning.py) | Decrease `lookahead_min_m` to `0.24` |
| **Traffic light red/green not recognized** | Raspberry Pi | [`rpi_tuning.py`](file:///home/rohith/iitb/config/rpi_tuning.py) | Adjust `light_red1_hsv` or `light_green_hsv` |
| **Vehicle stops too far from the stop line** | Raspberry Pi | [`rpi_tuning.py`](file:///home/rohith/iitb/config/rpi_tuning.py) | Decrease `stop_sign_trigger_dist_m` from `0.40` to `0.30` |
