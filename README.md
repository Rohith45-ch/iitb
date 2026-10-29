# Urban Autonomous Mobility Challenge (UAMC) — Techfest, IIT Bombay

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Platform: Raspberry Pi / Jetson](https://img.shields.io/badge/Platform-RPi4%20%7C%20Jetson%20Nano%20%7C%20ESP32-orange.svg)]()

> Official Autonomous Vehicle Software Stack developed for the **Urban Autonomous Mobility Challenge (UAMC)** at **Techfest, IIT Bombay**.

---

## 1. Challenge & Competition Overview

The **Urban Autonomous Mobility Challenge (UAMC)**, inspired by international benchmarks like the Bosch Future Mobility Challenge (BFMC), challenges student teams to design, build, and program a 1:10 scaled autonomous vehicle navigating a miniature smart-city street network without remote control or human intervention.

### Important Timeline & Milestones
- **Registration Deadline**: October 31st
- **Round 1 (Remote Qualification)**: **November 10th** (3–5 min video + Technical Design Document)
- **Round 1 Results**: November 17th / 24th (Top 25 teams advance)
- **Arena Layout Release**: November 24th / 31st
- **Round 2 (Elimination Heats at IIT Bombay)**: December 16–17th
- **Round 3 (Semifinal & Grand Finale)**: December 18th

---

## 2. Software Architecture

```
uamc/
├── perception/             # Computer Vision & Sensor Fusion
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
```

---

## 3. Engineering Documentation

Complete engineering specifications, derivations, and guides are located in the `docs/` folder:
- [Technical Design Document (TDD)](docs/TECHNICAL_DESIGN_DOCUMENT.md) — *Official 1–2 page submission document for Round 1*
- [ESP32 & Raspberry Pi Wiring Guide](docs/ESP32_RPI_WIRING_GUIDE.md) — *Detailed pinouts, 3.3V logic level shifting, and power distribution*
- [Problem Statement Analysis](docs/PROBLEM_STATEMENT_ANALYSIS.md) — *Breakdown of competition rounds, scoring system, and penalty mitigations*
- [Engineering Calculations & Math Models](docs/ENGINEERING_CALCULATIONS.md) — *Ackermann turning radius, braking distance, IPM, and controller tuning*
- [Round 1 Action Plan & Video Guide](docs/ROUND1_ACTION_PLAN.md) — *Step-by-step guide to construct the practice track and film the 3–5 min video*

---

## 4. Quick Start & Execution

### Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/Rohith45-ch/iitb.git
cd iitb
pip install -r requirements.txt
pip install -e .
```

### Running Software-in-the-Loop (SITL) Simulation
Test the complete perception, planning, and control stack on any developer laptop without hardware:
```bash
# Headless simulation
python3 scripts/run_sim.py --duration 10.0

# With OpenCV graphical telemetry HUD
python3 scripts/run_sim.py --duration 10.0 --gui
```

### Running the Test Suite
Run the automated test suite verifying lane detection, FSM transitions, and controllers:
```bash
python3 -m unittest discover tests
```

### Using Gemini from the Terminal
Create a new key in Google AI Studio after revoking any key shared in chat, then set it only in your current shell:
```bash
export GEMINI_API_KEY='paste-the-new-key-here'
python3 scripts/gemini_chat.py "Explain the current vehicle architecture"
python3 scripts/gemini_chat.py
```
The interactive client accepts prompts until `/exit`. The key is read from the environment and is not stored in this repository.

### Deploying on the Physical Vehicle
To start autonomous driving on the physical Raspberry Pi / Jetson car:
```bash
python3 scripts/run_autonomous.py --camera-id 0 --serial-port /dev/ttyUSB0
```

---

## 5. Microcontroller Firmware (Arduino / ESP32)
The real-time actuator driver sketch is located in [firmware/arduino_vehicle_controller.ino](firmware/arduino_vehicle_controller.ino). Flash it to your Arduino/ESP32 via the Arduino IDE or PlatformIO. It handles:
- 50 Hz PWM steering servo actuation
- Motor PWM and active electronic braking
- Real-time ultrasonic pulse timing
- Quadrature optical wheel encoder interrupts
- 200 ms safety watchdog auto-shutdown

---

## 6. License & Team
Developed for **Techfest, IIT Bombay — Urban Autonomous Mobility Challenge (UAMC)**.  
Released under the MIT License.