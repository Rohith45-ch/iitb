# Technical Design Document (TDD)
## Urban Autonomous Mobility Challenge (UAMC) — Techfest, IIT Bombay

**Team Name:** Autonomous Mobility Lab (AML)  
**Vehicle Model:** AML-Rover-V1  
**Category:** 1:10 Scaled Autonomous Electric Vehicle  

---

### 1. Executive Summary & System Overview
AML-Rover-V1 is an autonomous scaled robotic vehicle developed for the Urban Autonomous Mobility Challenge (UAMC) at Techfest, IIT Bombay. The system is designed to autonomously navigate complex urban tabletop environments, executing lane-keeping, traffic sign/signal compliance, pedestrian safety stops, static/dynamic obstacle avoidance, and precision bay parking without human intervention. The architecture decouples high-level perception and planning (hosted on a Linux Single Board Computer) from low-level real-time actuation and safety watchdogs (hosted on a deterministic microcontroller).

---

### 2. Hardware Architecture & Sensor Suite

```mermaid
graph TD
    subgraph Power System
        BATT[7.4V / 11.1V LiPo Battery]
        FUSE[15A Fast-Blow Fuse & Master Kill Switch]
        BUCK[5V/5A Switching Regulator]
    end

    subgraph Compute Stack
        SBC[High-Level SBC: Raspberry Pi 4 / Jetson Nano<br/>Linux OS + Python Perception & Planning Stack]
        MCU[Low-Level MCU: ESP32 / Arduino Nano<br/>Real-Time PID & Actuator PWM Driver]
    end

    subgraph Sensor Suite
        CAM[Wide-Angle USB / CSI Camera - 120° FOV, 60 FPS]
        US_FRONT[Ultrasonic Sensor Array - Front HC-SR04 / ToF]
        US_SIDE[Ultrasonic Sensor - Lateral Parking Bay Scanner]
        IMU[6-DOF IMU: MPU-6050 / BNO055]
        ENC[Optical Wheel Encoders - Dual Channel Quadrature]
    end

    subgraph Actuation Stack
        STEER[High-Torque Metal Gear Steering Servo]
        ESC[Electronic Speed Controller / H-Bridge Motor Driver]
        MOTOR[Brushed / Brushless DC Drive Motor]
    end

    BATT --> FUSE
    FUSE --> BUCK
    FUSE --> ESC
    BUCK --> SBC
    BUCK --> MCU

    CAM -->|USB / CSI| SBC
    IMU -->|I2C| MCU
    ENC -->|Interrupts| MCU
    US_FRONT -->|GPIO| MCU
    US_SIDE -->|GPIO| MCU

    SBC <-->|High-Speed UART / Serial 115200 bps| MCU
    MCU -->|PWM 50Hz| STEER
    MCU -->|PWM / Direction| ESC
    ESC --> MOTOR
```

- **Compute Unit**: Raspberry Pi 4B (4GB) running Ubuntu Linux / Raspberry Pi OS. High-level vision processing and decision planning run at 30+ FPS.
- **Microcontroller**: ESP32 / Arduino running embedded C++ firmware responsible for 100 Hz PID motor control, servo angle modulation, sensor polling, and hardware watchdog fail-safes.
- **Sensors**: Wide-angle low-distortion camera (60 FPS, 1080p scaled to 640x480), three ultrasonic distance sensors (front-left, front-center, front-right) with 2 cm–400 cm range, side ToF/ultrasonic sensor for bay detection, and quadrature optical wheel encoders.
- **Chassis & Drive**: 1:10 scale Ackermann steering chassis with rear-wheel drive and differential gearing, providing realistic non-holonomic vehicle kinematics.

---

### 3. Perception Stack

1. **Lane Detection & Inverse Perspective Mapping (IPM)**:
   - Input frames are transformed using a calibrated homography matrix into a planar bird’s-eye perspective (ground plane representation).
   - Adaptive color segmentation in HSV and LAB color spaces extracts lane boundaries (yellow centerlines and white boundary markers) across varying arena illumination.
   - A sliding-window algorithm clusters lane pixels, fitting second-order polynomials:
     $$x = a \cdot y^2 + b \cdot y + c$$
   - Lane center offset $e_{lat}$ and heading error $e_{\theta}$ are derived relative to the camera optical axis.

2. **Traffic Sign & Light Recognition**:
   - Region of Interest (ROI) extraction based on color-space thresholding (octagonal red for Stop signs, triangular red for yields, circular for speed limits).
   - State verification using template correlation and contour geometry verification.
   - Traffic light state (Red / Yellow / Green) classified via circular Hough transform and luminance ratio analysis across vertical bounding boxes.

3. **Obstacle & Pedestrian Detection**:
   - Forward camera optical flow and contour bounding boxes identify obstacles and zebra-crossing textures.
   - Sensor fusion layer merges vision bounding boxes with ultrasonic rangefinder measurements to ensure high-confidence object distance estimates with zero blind spots.

---

### 4. Planning & Control Stack

1. **Behavioral Finite State Machine (FSM)**:
   - States: `LANE_FOLLOWING`, `STOP_SIGN_WAIT`, `TRAFFIC_LIGHT_WAIT`, `PEDESTRIAN_STOP`, `ROUNDABOUT_TRANSIT`, `OBSTACLE_AVOIDANCE`, `PARKING_MANEUVER`, and `EMERGENCY_STOP`.
   - Guaranteed transition debouncing prevents state chatter in noisy detection environments.

2. **Lateral Control (Pure Pursuit & Stanley)**:
   - Computes target front wheel steering angle $\delta$:
     $$\delta = \arctan\left(\frac{2 L \sin(\alpha)}{l_d}\right)$$
   - Adaptive lookahead distance $l_d(v) = k \cdot v + l_{d,0}$ stabilizes steering across both straightaways and sharp roundabout corners.

3. **Longitudinal Control**:
   - Discrete PID speed governor:
     $$u(t) = K_p e(t) + K_i \int e(t) dt + K_d \frac{de(t)}{dt}$$
   - Trapezoidal velocity profiling handles smooth deceleration approaching intersections, stopping lines, and parking slots.

---

### 5. Safety Systems & Failure Handling

1. **Emergency Stop (E-Stop)**:
   - **Hardware Level**: Prominently mounted latching push-button kill switch directly isolates the battery supply from the motor driver, immediately disabling all kinetic motion while keeping SBC telemetry powered.
   - **Software Watchdog**: The low-level MCU implements a 150 ms heartbeat timeout. If serial communication from the SBC drops, actuator outputs are instantly clamped to zero.
2. **Electrical Isolation & Fusing**:
   - 15A fast-acting inline fuse on primary battery rail; separate high-current DC-DC converter with reverse polarity and overcurrent protection for compute boards.
3. **Graceful Degradation**:
   - If lane detection drops momentarily due to glare, the vehicle maintains steering dead reckoning using encoder odometry and IMU gyro integration for up to 1.5 seconds before bringing the car to a controlled soft halt.

---

### 6. Physical Specifications Summary
| Parameter | Value |
| :--- | :--- |
| **Dimensions (L × W × H)** | 420 mm × 195 mm × 160 mm |
| **Wheelbase ($L$)** | 260 mm |
| **Track Width ($W$)** | 165 mm |
| **Gross Weight** | 1.85 kg |
| **Max Steering Angle ($\delta_{max}$)** | $\pm 28^\circ$ |
| **Min Turning Radius ($R_{min}$)** | 488 mm (48.8 cm) |
| **Cruising Speed ($v$)** | 0.40 m/s – 0.65 m/s |
| **Stopping Distance from Max Speed** | < 12 cm |
| **Compute Power Draw** | 5V @ 2.2A (~11W peak) |
