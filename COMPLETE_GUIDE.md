# 🚗 UAMC Autonomous Vehicle — COMPLETE MASTER MANUAL
### Techfest IIT Bombay | Raspberry Pi 5 + ESP32 + ESC Architecture
**Repository:** [https://github.com/Rohith45-ch/iitb.git](https://github.com/Rohith45-ch/iitb.git)  
**Hardware Revision:** Final Confirmed Hardware Inventory (Raspberry Pi 5 + ESP32 DevKit V1 + Micro Servo 9g + 2500–3500 mAh LiPo + 1x Front Ultrasonic + ESC)  
**Last Updated:** October 31, 2026  

---

> [!IMPORTANT]
> This is your **single source of truth** for the entire project. It contains everything: verified physical inventory, master pin-to-pin wiring diagrams, CAD 3D-printing specifications, firmware flashing steps, Raspberry Pi 5 setup, and calibration playbooks.

---

## 📦 PART 1 — VERIFIED HARDWARE INVENTORY

### ✅ Confirmed Components In Hand

| # | Component | Exact Model / Specification | Role in System | Software & Wiring Status |
|---|-----------|-----------------------------|----------------|--------------------------|
| 1 | **High-Level SBC** | **Raspberry Pi 5 (8GB)** | Vision perception, YOLO/PilotNet AI, FSM Behavior Planner | **100% READY** (OS installed, repo cloned to `~/iitb`, live at `rohith@10.94.129.58`) |
| 2 | **Microcontroller** | **ESP32 DevKit V1 (30-pin)** | Real-time dual-core FreeRTOS controller, 50 Hz PWM actuator generator, 150ms watchdog | **100% READY** (Firmware in `firmware/esp32_firmware/`) |
| 3 | **Camera Module** | **Raspberry Pi Camera Rev 1.3** (OV5647 5MP) | Road lane tracking, traffic light detection, traffic signs | Supported via standard 15-to-22 pin RPi 5 CSI adapter cable |
| 4 | **Steering Servo** | **Micro Servo 9g (SG90 / MG90S)** | Front-wheel Ackermann steering angle control | 50 Hz PWM on ESP32 **GPIO 18** (`PIN_STEER_SERVO`) |
| 5 | **Drivetrain & Motor**| **RC Motor + Electronic Speed Controller (ESC)** | Vehicle propulsion & proportional braking | 50 Hz PWM on ESP32 **GPIO 19** (`PIN_MOTOR_PWM`) |
| 6 | **Proximity Sensor** | **1× HC-SR04 Ultrasonic Sensor** | Center front bumper obstacle detection & emergency braking | Trig: ESP32 **GPIO 5** \| Echo: ESP32 **GPIO 35** (via 1kΩ/2kΩ divider) |
| 7 | **Pi 5 Power Supply**| **2500–3500 mAh LiPo Power Bank (5V $\ge$ 3A)** | Dedicated isolated power for Raspberry Pi 5 | Plugs into Raspberry Pi 5 USB-C port |
| 8 | **Motor Power Supply**| **7.4V 2S LiPo / 7.2V NiMH Battery Pack** | High-current power for ESC, motor, and servo BEC | Plugs into ESC battery input (XT60 / Deans / Tamiya) |
| 9 | **Chassis Platform** | **1/10-Scale On-Road RC Chassis** | Wheelbase $\approx 260\text{ mm}$, front Ackermann steering tie rods | Tuned in `config/rpi_tuning.py` (`wheelbase_m = 0.260`) |
| 10| **Interconnect Data** | **USB-A to Micro-USB Cable** | High-speed 115200 baud serial bridge between Pi 5 and ESP32 | Pi USB-A port $\longleftrightarrow$ ESP32 Micro-USB port |
| 11| **Breadboard** | **400 Tie-Point Solderless Breadboard** | ESP32 carrier, common ground rail, sensor distribution | Layer 1 Mid-Deck |
| 12| **Ground Line Sensor**| **SmartElex RLS-06 (6-IR Array)** | Under-nose emergency line recovery | Optional add-on; camera handles primary lane tracking |

### 🟡 Optional / Deferred for Round 1
* **MPU6050 IMU:** Optional for Round 1. Firmware TinyML safety classifier safely falls back to nominal 1G acceleration without errors.
* **Optical Wheel Encoders:** Optional for Round 1. Throttle is commanded via calibrated open-loop cruising speeds.

---

## 🔌 PART 2 — MASTER PIN-TO-PIN WIRING MAP

Every wire in the autonomous vehicle connects according to this authoritative map:

```
                         ┌──────────────────────────────────┐
                         │   2500–3500 mAh LiPo Powerbank   │
                         └────────────────┬─────────────────┘
                                          │ 5V / 3A (USB-C)
                                          ▼
                                 [ Raspberry Pi 5 ]
                                          │
                             USB Cable    │   15-to-22 Pin Ribbon
                           (Serial Data)  │
                                          ▼
                   ┌──────────────────────┴──────────────────────┐
                   │                                             │
                   ▼                                             ▼
         [ ESP32 DevKit V1 ]                          [ RPi Cam Rev 1.3 ]
      (on 400-pt Breadboard)                         (on Layer 3 Mast)
       ├── Pin 18 (PWM 50Hz) ──────► Micro Servo 9g (Signal)
       ├── Pin 19 (PWM 50Hz) ──────► ESC Throttle (Signal)
       ├── Pin 5  (Trigger)  ──────► HC-SR04 Center Sonar Trig
       ├── Pin 35 (Echo Center)◄──── HC-SR04 Center Sonar Echo (via 1k/2k Divider)
       └── Pin 27 (Input Pullup)◄─── Hardware E-Stop Kill Switch
```

### 📋 Detailed Pin Allocation Table

| Hardware Component | Device Wire / Terminal | ESP32 DevKit V1 Pin | Parameter in `esp32_config.h` | Signal Description & Level |
| :--- | :--- | :--- | :--- | :--- |
| **Micro Servo 9g** | Signal (Orange or Yellow) | **GPIO 18** | `PIN_STEER_SERVO` | 50 Hz PWM (`LEDC Channel 0`, 1000–2000 µs) |
| **Micro Servo 9g** | Power (Red) & Ground (Brown) | ESC BEC 5V & Common GND | — | 5V / GND (powered from ESC BEC, NOT ESP32!) |
| **Drive Motor ESC** | Throttle Signal (White or Yellow)| **GPIO 19** | `PIN_MOTOR_PWM` | 50 Hz PWM (`LEDC Channel 1`, 1000–2000 µs) |
| **Drive Motor ESC** | Reference Ground (Black) | **ESP32 GND** | — | Must connect to common breadboard GND |
| **Drive Motor ESC** | Battery Input (Thick Red/Black)| **7.4V 2S LiPo Battery** | — | High-current main motor supply |
| **HC-SR04 Sonar** | VCC | **5V Power Rail** | — | 5V Power |
| **HC-SR04 Sonar** | GND | **Common Ground** | — | Ground |
| **HC-SR04 Sonar** | Trigger | **GPIO 5** | `PIN_US_TRIG` | 10 µs digital pulse from ESP32 |
| **HC-SR04 Sonar** | Echo | **GPIO 35** (via divider) | `PIN_US_ECHO_CENTER` | 3.3V safe divided logic input |
| **Hardware E-Stop** | Switch Terminals | **GPIO 27** & **GND** | `PIN_ESTOP_INPUT` | Active-LOW latching button |
| **Pi 5 Data Bridge** | USB Data Cable | **Micro-USB Port** | Serial UART | 115200 Baud (`/dev/ttyUSB0`) |

### ⚡ Ultrasonic 3.3V Voltage Divider Circuit
Because HC-SR04 echo pins output 5V and ESP32 GPIOs are strictly 3.3V rated, wire this simple 2-resistor voltage divider on the breadboard:
$$\text{Echo (5V)} \longrightarrow [1\text{ k}\Omega] \longrightarrow \text{ESP32 GPIO 35} \longrightarrow [2\text{ k}\Omega] \longrightarrow \text{GND}$$
$$V_{out} = 5\text{V} \times \frac{2\text{ k}\Omega}{1\text{ k}\Omega + 2\text{ k}\Omega} = 3.33\text{V} \quad \text{(100% Safe for ESP32)}$$

---

## 🖨️ PART 3 — 3D PRINTING & MECHANICAL CHASSIS SPECIFICATIONS

If you are 3D-printing decks, brackets, or a custom chassis plate, use these exact dimensions:

```
                           ┌───────────────────────────────┐
                           │ LAYER 3: PERCEPTION MAST      │
                           │ Raspberry Pi Camera Rev 1.3   │
                           │ (Elevated @ 130mm, 18° tilt)  │
                           └───────────────┬───────────────┘
                                           │
  ┌────────────────────────────────────────┴────────────────────────────────────────┐
  │ LAYER 2: COMPUTE & SENSOR DECK (Top Plate)                                      │
  │ • Front Bumper: 1x HC-SR04 Center Sonar Pod (0°, GPIO 35 - Round 1 Baseline)   │
  │ • Raspberry Pi 5 (M2.5 standoffs, active cooler intake & MicroSD egress)        │
  └────────────────────────────────────────┬────────────────────────────────────────┘
                   ▲                       │ (4x M3 × 35mm Hex Standoffs)
                   │                       ▼
  ┌─────────────────────────────────────────────────────────────────────────────────┐
  │ LAYER 1: POWER & CONTROLLER DECK (Middle Plate)                                 │
  │ • 400-Point Breadboard with ESP32 DevKit V1 seated                              │
  │ • 2500–3500 mAh LiPo Power Bank (dedicated Raspberry Pi 5 power)                │
  │ • RC ESC Tray with bottom airflow grill                                         │
  └────────────────────────────────────────┬────────────────────────────────────────┘
                   ▲                       │ (4x M3 × 30mm Hex Standoffs)
                   │                       ▼
  ┌─────────────────────────────────────────────────────────────────────────────────┐
  │ LAYER 0: BASE CHASSIS DECK (Ground Plate)                                       │
  │ • Front Lip Underside: SmartElex RLS-06 6-IR Line Sensor (5-10 mm above track)  │
  │ • Front Topside: Micro Servo 9g pocket (23.5 × 12.5 mm) & Ackermann tie-rods     │
  │ • Center Bay: 7.4V 2S LiPo Drive Battery Tray (lowest Center of Gravity)       │
  │ • Rear Axle: Drive Motor, Differential, and Gearbox                             │
  └─────────────────────────────────────────────────────────────────────────────────┘
```

### 📐 Master CAD Dimensioning Table

| Component | Physical Dimensions (L × W × H) | Mounting Hole Pattern | Fastener Size | CAD Modeling Tolerance / Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Micro Servo 9g (SG90 / MG90S)**| 23.0 × 12.2 × 29.0 mm | 2 holes: **28.0 mm** center-to-center | M2 or M2.5 screws | Pocket cutout: **23.5 × 12.5 mm**, depth 18.0 mm. |
| **2500–3500 mAh LiPo Power Bank**| ~96.0 × 65.0 × 16.0 mm | Flat enclosure (no screw holes) | 2× 15 mm Velcro straps | Bay: **100.0 × 68.0 mm** with strap slots (18 × 3 mm). |
| **Raspberry Pi 5** | 85.0 × 56.0 × 17.0 mm | 4 holes: **58.0 × 49.0 mm** rectangle | M2.5 × 10 mm standoffs | Hole diameter: **Ø 2.8 mm**. Leave SD slot accessible. |
| **Raspberry Pi Cam Rev 1.3** | 25.0 × 24.0 × 9.0 mm | 4 holes: **21.0 × 12.5 mm** rectangle | M2 nylon screws | Lens hole: Ø 8.5 mm; ribbon slot: 17.0 × 2.0 mm. |
| **HC-SR04 Ultrasonic Module** | 45.0 × 20.0 × 15.0 mm | Transducer center spacing: **26.0 mm**| Front friction fit / clip | Cut 2 barrel holes: **Ø 16.4 mm** spaced 26.0 mm apart. |
| **400-Point Breadboard** | 82.0 × 55.0 × 9.0 mm | Flat base (adhesive tape back) | Snap-fit border / lip | Recessed deck tray: **83.5 × 56.5 × 3.0 mm**. |
| **SmartElex RLS-06 (6-IR Array)** | 135.0 × 20.0 × 12.0 mm | 2 holes: **125.0 mm** apart | M3 screws + nuts | Ground clearance: **5.0 – 10.0 mm** from track surface. |
| **7.4V Motor LiPo Battery** | ~135.0 × 45.0 × 24.0 mm | Battery cradle | 20 mm Velcro strap | Centerline bottom deck tray: **140.0 × 48.0 mm**. |

---

## 💻 PART 4 — SOFTWARE STACK & REPOSITORY STRUCTURE

Everything is tracked and maintained in your repository: `https://github.com/Rohith45-ch/iitb.git`

```
iitb/
├── config/
│   └── rpi_tuning.py                  ← Central Pi-side tuning (camera, speeds, PID, lookahead)
├── docs/
│   ├── 3D_PRINTING_CHASSIS_AND_COMPONENTS_ARCHITECTURE.md ← Full mechanical blueprints
│   ├── ESP32_RPI_WIRING_GUIDE.md      ← Detailed electrical wiring guide
│   ├── DEVICE_TUNING_BLOCKS.md        ← Parameter tuning playbook
│   ├── ROUND1_ACTION_PLAN.md          ← Video submission script & track build
│   └── ROUND1_ARCHITECTURE_AND_BUILD_GUIDE.md ← Full system architecture
├── firmware/
│   └── esp32_firmware/
│       ├── esp32_vehicle_controller.ino ← Dual-core FreeRTOS firmware
│       ├── esp32_config.h             ← Master pin assignments & actuator trims
│       ├── ultrasonic_filter.h        ← Median-of-5 + EMA outlier filter
│       └── tinyml_motion.h            ← Collision & rollover classifier
├── models/
│   ├── yolov8n.onnx                   ← Real-time object detection (signs, obstacles)
│   ├── yolo11n.onnx                   ← Lightweight secondary detector
│   └── pilotnet_steering.onnx         ← End-to-end neural steering model
├── scripts/
│   ├── run_autonomous.py              ← MAIN PRODUCTION ENTRY POINT
│   ├── verify_system_ready.py         ← Automated pre-flight system diagnostic
│   ├── detect_hardware.py             ← Auto-detection of camera & ESP32 USB ports
│   ├── calibrate_camera.py            ← Interactive perspective warp (IPM) calibration
│   └── run_sim.py                     ← Software-in-the-loop (SITL) simulator
└── uamc/                              ← Core Python autonomy package
    ├── perception/ (lane, sign, traffic light, obstacle detectors)
    ├── planning/   (behavior FSM, motion trajectory generator)
    ├── control/    (pure pursuit steering, longitudinal PID speed)
    └── hal/        (serial bridge, camera interface)
```

---

## 🚀 PART 5 — STEP-BY-STEP BRING-UP GUIDE

### Step 1: Flash & Test the ESP32
1. Plug the ESP32 DevKit into your laptop using a micro-USB data cable.
2. Open **Arduino IDE**:
   * In **File $\to$ Preferences**, ensure the ESP32 Board URL is added:
     `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
   * Under **Tools $\to$ Board**, select **ESP32 Dev Module**.
   * Under **Tools $\to$ Port**, select your ESP32's COM port (`COM3`, `COM4`, `/dev/ttyUSB0`, etc.).
3. Open `firmware/esp32_firmware/esp32_vehicle_controller.ino`.
4. Click **Upload** ($\rightarrow$). *(If terminal says "Connecting...", hold down physical **BOOT** button for 2 seconds).*
5. Open **Serial Monitor** at **115200 baud**. You will see live telemetry:
   `#TEL,2.00,2.00,2.00,0.20,0,0,0.0,0*`

### Step 2: Power Up & Connect to Raspberry Pi 5
*(Your Pi 5 is already installed and verified!)*
1. Power the Pi 5 from the **2500–3500 mAh LiPo power bank**.
2. Connect your laptop to the hotspot (`Heisenberg`).
3. Open terminal and log in via SSH:
   ```bash
   ssh rohith@10.94.129.58
   ```
4. Pull the latest code:
   ```bash
   cd ~/iitb && git pull origin main
   ```

### Step 3: Connect Hardware & Run Pre-Flight Diagnostics
1. Plug the **ESP32** into any USB-A port on the Raspberry Pi 5 using the USB cable.
2. Connect the **Raspberry Pi Camera Rev 1.3** to port `CAM1` on the Pi 5 using the 22-to-15 pin adapter ribbon cable.
3. Wire the **Micro Servo 9g** to ESP32 Pin 18 and **ESC** to ESP32 Pin 19.
4. Wire the **HC-SR04** to ESP32 Pin 5 (Trig) and Pin 35 (Echo via divider).
5. In your Pi 5 SSH terminal, run the hardware detector:
   ```bash
   python3 scripts/detect_hardware.py
   ```
6. Run the master pre-flight test:
   ```bash
   python3 scripts/verify_system_ready.py
   ```
   *Expected output: ALL PRE-FLIGHT CHECKS PASSED!*

---

## ⚙️ PART 6 — TUNING & CALIBRATION QUICK-REFERENCE

### ESP32 Parameters: [`firmware/esp32_firmware/esp32_config.h`](file:///home/rohith/iitb/firmware/esp32_firmware/esp32_config.h)

| Constant | Default | Purpose / How to Tune |
| :--- | :--- | :--- |
| `SERVO_MID_US` | `1500` | **Steering Neutral Trim:** Increase if car pulls left; decrease if it pulls right. |
| `SERVO_MIN_US` | `1000` | Full Left steering lock pulse width (-28.0°). |
| `SERVO_MAX_US` | `2000` | Full Right steering lock pulse width (+28.0°). |
| `ESC_NEUTRAL_US` | `1500` | ESC neutral stop pulse width ($1500\ \mu\text{s}$). |
| `ESC_FORWARD_SAFE_CAP_US` | `1700` | Safe maximum forward speed cap for indoor practice. Reduce to 1620 for slower testing. |
| `PIN_STEER_SERVO` | `18` | Micro Servo 9g PWM GPIO pin. |
| `PIN_MOTOR_PWM` | `19` | ESC throttle PWM GPIO pin. |
| `PIN_US_TRIG` | `5` | Ultrasonic trigger pulse GPIO pin. |
| `PIN_US_ECHO_CENTER` | `35` | Ultrasonic center echo GPIO pin. |
| `PIN_ESTOP_INPUT` | `27` | Physical emergency kill switch GPIO pin. |

### Raspberry Pi Parameters: [`config/rpi_tuning.py`](file:///home/rohith/iitb/config/rpi_tuning.py)

| Constant | Default | Purpose / How to Tune |
| :--- | :--- | :--- |
| `wheelbase_m` | `0.260` | Distance between front and rear axles in meters ($26.0\text{ cm}$). |
| `lookahead_min_m`| `0.28` | Pure pursuit lookahead. Increase if car wiggles; decrease if cutting corners. |
| `v_cruise_ms` | `0.45` | Main cruising speed ($\approx 1.6\text{ km/h}$). Set to `0.35` for slower, safer testing. |
| `obstacle_emergency_dist_m` | `0.25` | Obstacle distance trigger for emergency stop ($25\text{ cm}$). |

---

## 🏆 PART 7 — LAUNCHING FOR ROUND 1 QUALIFICATION

Place your vehicle on your practice track, turn on the motor battery, and run:

```bash
# Production launch with YOLOv8 obstacle detection in headless mode:
python3 scripts/run_autonomous.py --serial-port /dev/ttyUSB0 --use-yolo --no-gui
```

To record the official qualification run video with telemetry overlay:
```bash
python3 scripts/record_qualification_run.py --output-video round1_submission.mp4
```

---
*Single Source of Truth Manual — Maintained & committed directly in [Rohith45-ch/iitb](https://github.com/Rohith45-ch/iitb).*
