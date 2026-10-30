# Urban Autonomous Mobility Challenge (UAMC) — Self-Driving Car System Architecture

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Hardware](https://img.shields.io/badge/Compute-Raspberry%20Pi%204%20%2B%20ESP32-blue.svg)]()

> **Core Theme:** *"A self-driving car navigating a smart city street."*  
> An autonomous 1:10 scaled vehicle engineered to navigate a miniature tabletop urban street network with **100% onboard physical AI** and zero live remote control.

> [!IMPORTANT]
> **Received your Raspberry Pi 4B & ESP32 hardware?**  
> Follow the master checklist: **[START_HERE_HARDWARE_SETUP.md](START_HERE_HARDWARE_SETUP.md)** to plug in, test, and launch the vehicle step-by-step.

---

## 1. Problem Statement & Scope

Design and build a scaled autonomous vehicle capable of navigating a miniature urban street network:
- **Lane Discipline**: Following road lanes smoothly with minimal lateral deviation.
- **Intersection Rules**: Obeying octagonal Stop signs (mandatory full stop and right-of-way hold) and 3-lamp traffic lights (Red stop, Green go).
- **Pedestrian Safety**: Detecting zebra crossings and yielding to pedestrian figures.
- **Obstacle Handling**: Sensing static obstacles and dynamic traffic, executing deceleration, stopping, or safe overtaking.
- **Autonomous Parking**: Detecting marked parking bays and executing alignment maneuvers within boundary lines.
- **Zero Human Intervention**: Completely self-contained perception, state estimation, and actuation during operation.

### Architectural Approaches Supported by the Stack
1. **Classical Computer Vision**: Inverse Perspective Mapping (IPM), color-space thresholding (HSV/LAB), and sliding-window polynomial fitting for lane-keeping and sign recognition.
2. **Multi-Sensor Fusion**: Fusing camera bounding boxes with a multi-transducer ultrasonic array for blind-spot-free obstacle detection.
3. **End-to-End / Neural Perception Ready**: Lightweight CNN/MobileNet hook points for direct steering angle prediction and sign classification.
4. **Dedicated Ultrasonic Parking Routine**: Flank-scanning ultrasonic ranging for open-bay localization and geometric parking trajectory execution.

---

## 2. General Elements Expected Across the Build

| Element | Requirement | Implementation in this Repository |
| :--- | :--- | :--- |
| **Hardware** | Single-board computer + microcontroller paired with cameras, ultrasonic, wheel encoders, IMU | **Raspberry Pi 4B (SBC)** paired with **ESP32 Dual-Core (MCU)**, wide-angle 120° camera, 4× HC-SR04 ultrasonic array, and dual quadrature optical wheel encoders |
| **Autonomy ("Physical AI")** | Genuine onboard perception and decision-making with zero remote control | Real-time OpenCV pipeline, Behavioral Finite State Machine (FSM), Pure Pursuit lateral tracking, and discrete PID longitudinal control running locally |
| **Engineering Documentation** | Clear account of system architecture, perception approach, and control stack | Comprehensive [Technical Design Document (TDD)](docs/TECHNICAL_DESIGN_DOCUMENT.md) and [Engineering Calculations](docs/ENGINEERING_CALCULATIONS.md) with full mathematical derivations |
| **Safety Compliance** | Demonstrable working emergency stop, fused battery output, safe wiring | Hardwired mechanical latching kill switch, 15A inline fuse, 3.3V logic level shifting, and a dual-watchdog system (RPi software ping + ESP32 150 ms hardware timer watchdog) |
| **Scalability & Usability** | Cost-effective, clean engineering that generalizes beyond a fixed arena | Modular Python package (`uamc/`), deterministic FreeRTOS C++ firmware, hardware abstraction layer (HAL), and closed-loop SITL simulator |

---

## 3. System Hardware Architecture (Raspberry Pi + ESP32)

Workload is decoupled between high-level perception/planning (Linux SBC) and deterministic real-time actuation/safety (Dual-Core FreeRTOS MCU):

```
+-----------------------------------------------------------------------------------+
|                            HIGH-LEVEL COMPUTE (Raspberry Pi 4B)                   |
|                                                                                   |
|  [ Wide-Angle Camera ]                                                            |
|          |                                                                        |
|          v                                                                        |
|  +--------------------+   +---------------------+   +--------------------------+  |
|  | Lane Detector      |   | Sign & Light Vision |   | Pedestrian & Crossings   |  |
|  | (IPM + Polyfit)    |   | (Stop, Red/Yellow/G)|   | (Zebra Band Filter)      |  |
|  +---------+----------+   +----------+----------+   +------------+-------------+  |
|            |                         |                           |                |
|            +-------------------------+---------------------------+                |
|                                      v                                            |
|                       +-------------------------------+                           |
|                       | Behavioral State Machine (FSM)|                           |
|                       | (LaneFollow, Stop, Park, EStop|                           |
|                       +---------------+---------------+                           |
|                                       v                                           |
|                       +-------------------------------+                           |
|                       | Lateral Control (Pure Pursuit)|                           |
|                       | Longitudinal Control (PID)    |                           |
|                       +---------------+---------------+                           |
+---------------------------------------|-------------------------------------------+
                                        | UART Link (115,200 baud)
                                        | Commands: #CMD,<steer>,<throttle>,<estop>*
                                        | Telemetry: #TEL,<us...>,<enc...>,<yaw>*
+---------------------------------------v-------------------------------------------+
|                          LOW-LEVEL CONTROLLER (ESP32 MCU)                         |
|                                                                                   |
|    CORE 0 (Sensor Engine):                         CORE 1 (Actuation & Safety):   |
|    • Staggered 10ms Ultrasonic Polling             • Serial Packet Parser         |
|    • Optical Encoder Interrupts (IRAM_ATTR)        • 50 Hz LEDC Steering Servo PWM|
|    • Hardware E-Stop Monitoring                    • 20 kHz Silent Motor PWM      |
|                                                    • 150 ms Hardware Watchdog     |
+---------------------------------------+-------------------------------------------+
                                        |
               +------------------------+------------------------+
               |                                                 |
               v                                                 v
    [ Metal Gear Steering Servo ]                     [ DC Drive Motor & Driver ]
    (Range: +/- 28 deg)                               (Active Dynamic Braking)
```

---

## 4. Software Repository Structure

```
uamc/
├── perception/             # Physical AI Vision & Sensor Fusion
│   ├── lane_detector.py    # Inverse Perspective Mapping (IPM) & polynomial curve fitting
│   ├── traffic_signs.py    # STOP, Yield, and Speed Limit sign recognition
│   ├── traffic_lights.py   # Red / Yellow / Green detection with temporal debouncing
│   ├── pedestrian.py       # Zebra crossing and pedestrian tracking
│   ├── obstacle_detector.py# Multi-sensor fusion (camera + ultrasonic array)
│   └── parking_detector.py # Autonomous parking bay scanning
│
├── planning/               # Decision Making & Trajectory Generation
│   ├── behavior_planner.py # Behavioral Finite State Machine (FSM)
│   └── motion_planner.py   # Quintic polynomial overtaking splines & speed profiler
│
├── control/                # Lateral & Longitudinal Controllers
│   ├── pure_pursuit.py     # Pure pursuit steering geometry with dynamic lookahead
│   └── longitudinal_controller.py # PID velocity controller with anti-windup & braking
│
├── safety/                 # Watchdog & Fail-safe Systems
│   └── emergency_stop.py   # 150ms heartbeat watchdog & kill switch monitor
│
├── hal/                    # Hardware Abstraction Layer
│   ├── camera_interface.py # Multithreaded low-latency camera acquisition
│   ├── serial_bridge.py    # UART protocol to Arduino/ESP32 (115200 baud)
│   └── mock_hal.py         # Virtual vehicle simulator for desktop testing
│
└── simulation/             # Simulation Environment
    └── synthetic_track.py  # 2D/3D perspective synthetic camera renderer

firmware/
└── esp32_firmware/
    └── esp32_vehicle_controller.ino # Dual-Core FreeRTOS firmware for ESP32

docs/
├── TECHNICAL_DESIGN_DOCUMENT.md # Official Technical Design Document (TDD)
├── ENGINEERING_CALCULATIONS.md  # Detailed kinematic, optical, and braking math
├── ESP32_RPI_WIRING_GUIDE.md    # Electrical schematic, pinouts, and 3.3V logic dividers
├── PROBLEM_STATEMENT_ANALYSIS.md# In-depth problem statement and rules breakdown
└── ROUND1_ACTION_PLAN.md        # Track construction and qualification video storyboard

scripts/
├── run_autonomous.py           # Main physical autonomous vehicle runtime
├── run_sim.py                  # Closed-loop Software-in-the-Loop (SITL) simulator
├── record_qualification_run.py # Telemetry HUD video recorder
└── calibrate_camera.py         # Perspective IPM coordinate tuner
```

---

## 5. Engineering Calculations & Mathematical Models

Detailed derivations are documented in [docs/ENGINEERING_CALCULATIONS.md](docs/ENGINEERING_CALCULATIONS.md).

### A. Ackermann Steering Kinematics & Turning Radius
The kinematic bicycle model governs turning:
$$\tan(\delta) = \frac{L}{R} \implies R_{min} = \frac{L}{\tan(\delta_{max})}$$
- Wheelbase: $L = 0.260\text{ m}$ ($26.0\text{ cm}$)
- Maximum steering angle: $\delta_{max} = 28.0^\circ$ ($0.4886\text{ rad}$)
- Minimum turning radius:
  $$R_{min} = \frac{0.260}{\tan(28.0^\circ)} = \mathbf{0.489\text{ m}} \quad (48.9\text{ cm})$$
- *Arena Compatibility*: The arena roundabout inner radius is $R_{island} \ge 40\text{ cm}$ with lane center at $R_{lane} \approx 57.5\text{ cm}$. Since $R_{min} = 48.9\text{ cm} < 57.5\text{ cm}$, the vehicle easily negotiates the sharpest curve without crossing lane boundaries.

### B. Longitudinal Dynamics & Stopping Distance
$$d_{stopping} = d_{reaction} + d_{braking} = v \cdot t_{reaction} + \frac{v^2}{2 \cdot a_{decel}}$$
- Reaction time: $t_{reaction} \approx 0.06\text{ s}$ ($16.7\text{ ms}$ camera $+ 25\text{ ms}$ inference $+ 2\text{ ms}$ UART $+ 15\text{ ms}$ ESC response)
- Deceleration: $a_{decel} = 2.2\text{ m/s}^2$ (active dynamic motor braking)
- At cruising speed ($v = 0.45\text{ m/s}$):
  $$d_{stopping} = (0.45 \times 0.06) + \frac{0.45^2}{2 \times 2.2} = 0.027 + 0.046 = \mathbf{7.3\text{ cm}}$$
- **Safety Trigger Threshold**: Emergency halt set at **$25.0\text{ cm}$** ($> 3\times$ stopping distance margin); advisory slowdown set at **$45.0\text{ cm}$**.

### C. Lateral Control: Pure Pursuit Algorithm
Front-wheel steering target angle $\delta$:
$$\delta = \arctan\left(\frac{2 L \sin(\alpha)}{l_d}\right)$$
Where:
- $\alpha$: Heading error from vehicle centerline to the lookahead point on the lane center.
- $l_d(v)$: Speed-adaptive lookahead distance:
  $$l_d(v) = k_{look} \cdot v + l_{d,0} = 0.15 \cdot v + 0.22\text{ m}$$

---

## 6. Safety Systems & Electrical Protection

1. **Hardware Kill Switch (E-Stop)**: Red latching emergency switch wired to physically disconnect motor driver power. Monitored on ESP32 GPIO 27.
2. **Dual-Watchdog Fail-Safe**:
   - High-level Python watchdog flags stale camera frames ($> 500\text{ ms}$).
   - ESP32 hardware watchdog shuts down motor PWM if no valid `#CMD` arrives within **$150\text{ ms}$**.
3. **Logic Level Shifting**: HC-SR04 echo pins output $5\text{V}$, which are divided down to safe $3.3\text{V}$ via $1\text{ k}\Omega$ and $2\text{ k}\Omega$ resistor dividers before entering ESP32 input-only GPIOs.
4. **Fused Battery Rail**: 15A fast-acting inline fuse on the primary LiPo output.

---

## 7. Quick Start & Execution

### Setup Environment
```bash
git clone https://github.com/Rohith45-ch/iitb.git
cd iitb
pip install -r requirements.txt
pip install -e .
```

### Run Software-in-the-Loop (SITL) Simulator
Simulate lane tracking, stop sign holds, and obstacle braking on your laptop:
```bash
# Headless
python3 scripts/run_sim.py --duration 10.0

# With OpenCV visual HUD
python3 scripts/run_sim.py --duration 10.0 --gui
```

### Run Automated Unit Test Suite
```bash
python3 -m unittest discover tests
```

### Record Telemetry Video
Record the vehicle's run with on-screen HUD (detected lane curves, obstacle distances, state machine, speed):
```bash
# On physical car
python3 scripts/record_qualification_run.py --duration 30.0 --output run.mp4

# In simulation mode
python3 scripts/record_qualification_run.py --sim --duration 15.0 --output sim_run.mp4
```

### Start Autonomous Physical Car
```bash
python3 scripts/run_autonomous.py --camera-id 0 --serial-port /dev/ttyAMA0
```