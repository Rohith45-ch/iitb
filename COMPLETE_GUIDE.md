# 🚗 UAMC Autonomous RC Car — COMPLETE MASTER GUIDE
### Techfest IIT Bombay | Raspberry Pi 5 + ESP32 + ESC Architecture

---

> [!IMPORTANT]
> This is your **single source of truth**. Everything you need — hardware list, what software exists, what's missing, and every step to follow when you get the devices.

---

## 📦 PART 1 — YOUR HARDWARE LIST (from your note)

| # | Component | Do We Have Software? | Notes |
|---|-----------|----------------------|-------|
| ✅ | Compatible Camera Module | **YES** — fully coded | Use USB webcam OR Pi Camera with CSI adapter |
| ✅ | Ultrasonic Distance Sensors (1–2 units) | **YES** — fully coded | HC-SR04 recommended |
| ✅ | Rechargeable Battery + Charger | No software needed | 7.4V 2S LiPo (Motor) + 2500–3500 mAh LiPo (Pi 5) |
| ⚠️ | **Raspberry Pi 5** | **YES (fully installed & tested)** | Cloned to ~/iitb, running on 10.94.129.58 |
| ✅ | MicroSD Card | No software needed | 64GB Samsung Evo Plus with Pi OS 64-bit |
| ✅ | 1/10-scale On-Road RC Chassis | **YES** — geometry coded | All params in `rpi_tuning.py` |
| ✅ | Steering Servo (Micro Servo 9g) | **YES** — fully coded | 50 Hz PWM on Pin 18 in `esp32_config.h` |
| ✅ | Drive Motor (compatible with chassis) | **YES** — fully coded | |
| ✅ | **Electronic Speed Controller (ESC)** | **YES** — firmware updated for ESC** | Single PWM wire like servo |

### ❌ MISSING COMPONENTS — Buy These!

| Component | Why Needed | Where to Buy | Cost |
|-----------|-----------|--------------|------|
| **ESP32 DevKit v1** | The brain for motor/servo/sensors | Amazon/Robocraze | ₹400–600 |
| **MPU6050 IMU** | Rollover/collision detection | Amazon/Robocraze | ₹100–150 |
| **USB-A to Micro-USB cable** | For ESP32 programming | Already have? | ₹50 |
| **Logic Level Shifter 3.3V↔5V** | ESP32 is 3.3V, ESC signal may be 5V | Amazon | ₹50–100 |
| **Jumper wires (M-M, M-F, F-F)** | For all connections | Any electronics shop | ₹100 |
| **Breadboard (optional)** | For prototyping connections | Any electronics shop | ₹100 |

---

## 💻 PART 2 — WHAT SOFTWARE WE'VE ALREADY BUILT

Everything is committed and pushed to: `https://github.com/Rohith45-ch/iitb.git`

### Raspberry Pi Software Stack (Python)
```
uamc/
├── perception/
│   ├── lane_detector.py          ← Detects road lanes using camera
│   ├── ai_detector.py            ← YOLO object detection (signs, obstacles)
│   ├── traffic_lights.py         ← Red/Green/Yellow light detection
│   ├── traffic_signs.py          ← Stop sign, speed limit detection
│   ├── pedestrian.py             ← Person detection at crosswalks
│   ├── obstacle_detector.py      ← Obstacle avoidance logic
│   └── parking_detector.py       ← Parking space detection
├── planning/
│   ├── behavior_planner.py       ← 8-state FSM (go/stop/turn/park...)
│   └── motion_planner.py         ← Path planning (quintic splines)
├── control/
│   ├── pure_pursuit.py           ← Steering control algorithm
│   ├── longitudinal_controller.py← Speed PID controller
│   └── pilotnet_controller.py    ← AI end-to-end steering (backup)
├── hal/
│   ├── serial_bridge.py          ← UART communication with ESP32
│   ├── camera_interface.py       ← Camera capture wrapper
│   └── mock_hal.py               ← Simulated hardware (for testing)
└── safety/
    └── emergency_stop.py         ← Watchdog safety system
```

### ESP32 Firmware (Arduino/C++)
```
firmware/esp32_firmware/
├── esp32_vehicle_controller.ino  ← Main firmware (FreeRTOS dual-core)
├── tinyml_motion.h               ← Collision/rollover AI classifier
├── ultrasonic_filter.h           ← Sensor noise filtering
└── esp32_config.h                ← ALL TUNING PARAMETERS (pins, speeds, etc.)
```

### AI Models (Downloaded & Ready)
```
models/
├── yolov8n.onnx         ← 12.2 MB — object detection
├── yolo11n.onnx         ← 5.1 MB  — object detection (faster)
├── pilotnet_steering.onnx ← 1 MB  — AI steering
└── mobilenet_v1_ssd.onnx ← 28 MB  — backup detector
```

### Configuration / Tuning Files
```
config/rpi_tuning.py              ← Pi-side tuning (camera, speeds, PID values)
firmware/esp32_firmware/esp32_config.h ← ESP32 hardware tuning (pins, PWM values)
```

### Scripts
```
scripts/
├── run_autonomous.py             ← MAIN: Start the car autonomously
├── run_sim.py                    ← Test without hardware (simulation)
├── verify_system_ready.py        ← Pre-flight check (run before connecting hardware)
├── detect_hardware.py            ← Auto-find ESP32 and camera USB ports
├── calibrate_camera.py           ← Camera angle calibration tool
└── fetch_ai_models.py            ← Download AI models if missing
```

### Documentation
```
docs/
├── PHYSICAL_BRINGUP_AND_INTEGRATION_GUIDE.md  ← Hardware connection guide
├── ESP32_RPI_WIRING_GUIDE.md                  ← Pin-by-pin wiring diagram
├── DEVICE_TUNING_BLOCKS.md                    ← How to tune after hardware is connected
└── SIMILAR_PROJECTS_RESEARCH.md               ← Comparison with other projects
START_HERE_HARDWARE_SETUP.md                   ← 7-step quick-start checklist
```

---

## 🔌 PART 3 — HOW RASPBERRY PI AND ESP32 ARE CONNECTED

```
  ┌─────────────────────────────┐        ┌─────────────────────────────┐
  │       RASPBERRY PI 5         │        │          ESP32 DevKit        │
  │   (High-Level AI Brain)      │        │  (Low-Level Hardware Control)│
  │                              │        │                              │
  │  ┌─────────────────────┐     │        │  ┌────────────────────────┐  │
  │  │  Camera → AI Models  │     │        │  │  Servo PWM → Steering  │  │
  │  │  Lane Detection       │     │        │  │  ESC PWM  → Motor      │  │
  │  │  Traffic Lights       │     │        │  │  Ultrasonic Sensors    │  │
  │  │  Object Detection     │     │        │  │  Encoder (if present)  │  │
  │  │  Behavior Planner     │     │        │  │  IMU (MPU6050)         │  │
  │  │  Motion Planner       │     │        │  │  Emergency Stop        │  │
  │  └─────────────────────┘     │        │  └────────────────────────┘  │
  │                              │        │                              │
  │  serial_bridge.py            │◄──────►│  esp32_vehicle_controller   │
  │  (UART at 115200 baud)        │  USB   │  .ino                        │
  │                              │  Cable │                              │
  └─────────────────────────────┘        └─────────────────────────────┘

  Pi sends: #CMD,<steering>,<throttle>,<emergency_stop>*\n   (30 times/sec)
  ESP32 sends: #TEL,<dist_left>,<dist_center>,<dist_right>,<yaw>,<estop>*\n
```

**Simple English**: Pi looks at the camera, runs AI, decides what to do → sends commands to ESP32 over USB cable → ESP32 physically moves the steering servo and motor via ESC.

---

## 🗺️ PART 4 — STEP-BY-STEP: WHAT TO DO WHEN YOU GET THE HARDWARE

---

### 📌 PHASE 1: Prepare Your Laptop (Do This NOW, Before Hardware Arrives)

**Step 1.1 — Clone/pull the latest code**
```bash
cd /home/rohith/iitb
git pull origin main
```

**Step 1.2 — Install Python dependencies**
```bash
pip install -r requirements.txt
```

**Step 1.3 — Install Arduino IDE (for ESP32 programming)**
```bash
# Download from: https://www.arduino.cc/en/software
# OR use the snap package:
sudo snap install arduino
```

**Step 1.4 — Add ESP32 board to Arduino IDE**
1. Open Arduino IDE
2. Go to `File → Preferences`
3. In "Additional Board Manager URLs", add:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Go to `Tools → Board → Board Manager`
5. Search "esp32" → Install **"esp32 by Espressif Systems"**

**Step 1.5 — Verify simulation works (no hardware needed)**
```bash
cd /home/rohith/iitb
python scripts/run_sim.py
# Should run for 30 seconds and show no errors
```

---

### 📌 PHASE 2: When Raspberry Pi 5 Arrives

**Step 2.1 — Flash the microSD card**
1. Download **Raspberry Pi Imager**: https://www.raspberrypi.com/software/
2. Select: `Raspberry Pi OS (64-bit)` (NOT Lite — you need the full version)
3. Click ⚙️ settings gear BEFORE flashing:
   - Enable SSH ✅
   - Set username: `pi`, password: `uamc2024`
   - Set WiFi: your laptop's hotspot SSID + password
4. Flash to microSD → Insert into Pi

**Step 2.2 — First boot + SSH into Pi**
```bash
# On your laptop, create a mobile hotspot (Settings → WiFi → Hotspot)
# Boot the Pi (it will auto-connect to hotspot)
# Find Pi's IP address in your phone hotspot settings
ssh pi@<PI_IP_ADDRESS>
# Password: uamc2024
```

**Step 2.3 — Update Pi and install dependencies**
```bash
# On the Pi (via SSH):
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-opencv git libatlas-base-dev
pip3 install onnxruntime numpy scipy pyserial
```

**Step 2.4 — Clone repo onto the Pi**
```bash
# On the Pi:
git clone https://github.com/Rohith45-ch/iitb.git
cd iitb
```

**Step 2.5 — Connect camera to Pi**
- **USB Webcam**: Just plug it in → it will appear as `/dev/video0`
- **Pi Camera Module**: Connect via CSI ribbon cable (Pi 5 needs the SHORT 22-pin connector end)
  - Enable camera: `sudo raspi-config → Interface Options → Camera → Enable`

**Step 2.6 — Test camera on Pi**
```bash
# On the Pi:
python3 -c "import cv2; cap=cv2.VideoCapture(0); ret,frame=cap.read(); print('Camera OK!' if ret else 'FAIL'); cap.release()"
```

**Step 2.7 — Test AI models on Pi**
```bash
cd /home/pi/iitb
python3 scripts/verify_system_ready.py
# All checks should PASS (ESP32 check will show "not connected" — that's OK for now)
```

---

### 📌 PHASE 3: When ESP32 Arrives

**Step 3.1 — Connect ESP32 to your LAPTOP via USB**
```bash
# Check it's detected:
ls /dev/ttyUSB* /dev/ttyACM*
# Should show: /dev/ttyUSB0 or /dev/ttyACM0
```

**Step 3.2 — Give permission to use the port**
```bash
sudo usermod -a -G dialout $USER
# Log out and log back in for this to take effect
```

**Step 3.3 — Open firmware in Arduino IDE**
1. Open Arduino IDE
2. `File → Open → /home/rohith/iitb/firmware/esp32_firmware/esp32_vehicle_controller.ino`

**Step 3.4 — Select your ESP32 board**
1. `Tools → Board → ESP32 Arduino → ESP32 Dev Module`
2. `Tools → Port → /dev/ttyUSB0` (or whatever appeared in Step 3.1)

**Step 3.5 — Upload firmware to ESP32**
1. Click the **→ Upload** button (right arrow)
2. Wait for "Done uploading" message
3. Open `Tools → Serial Monitor`, set baud to `115200`
4. You should see: `[ESP32] System ready. Waiting for Pi commands...`

---

### 📌 PHASE 4: Wiring Everything Together

**Step 4.1 — ESP32 to Servo (Steering)**
```
ESP32 Pin 18  →  Servo Signal (Yellow/White wire)
ESP32 GND     →  Servo GND (Brown/Black wire)
5V Power      →  Servo VCC (Red wire)  ← Use battery, NOT ESP32 5V
```

**Step 4.2 — ESP32 to ESC (Motor)**
```
ESP32 Pin 19  →  ESC Signal wire (usually White)
ESP32 GND     →  ESC GND (Black wire)
Battery       →  ESC Power wires (Red/Black — this powers the motor)
```

> [!CAUTION]
> NEVER power the motor from the Pi or ESP32! The motor draws too much current and will damage them. Always use the battery via the ESC.

**Step 4.3 — ESP32 to Single Front Ultrasonic Sensor (HC-SR04)**
```
Front-Center Sensor:
  ESP32 Pin 5   → TRIG (10µs Trigger pulse)
  ESP32 Pin 35  → ECHO (via 1kΩ/2kΩ voltage divider to protect 3.3V GPIO)
  VIN / 5V      → VCC
  GND           → GND
```

**Step 4.4 — ESP32 to Raspberry Pi (UART/USB)**
```
Simply: USB-A (Pi) ←→ USB-Micro (ESP32)
That's it! No extra wiring needed.
```

**Step 4.5 — Power everything**
```
Battery (7.4V LiPo) → ESC → Powers motor
Battery → BEC (Battery Eliminator Circuit, built into most ESC) → 5V for servo
Raspberry Pi → Power via its USB-C port (5V 3A power bank)
ESP32 → Powered via USB from Raspberry Pi (once connected)
```

---

### 📌 PHASE 5: Software Connection Between Pi and ESP32

**Step 5.1 — Connect ESP32 to Raspberry Pi via USB**
(The USB cable from Phase 4 Step 4.4 — same cable you used for programming)

**Step 5.2 — Detect the ESP32 on the Pi**
```bash
# On the Pi:
cd /home/pi/iitb
python3 scripts/detect_hardware.py
# Output: Found ESP32 at /dev/ttyUSB0
```

**Step 5.3 — Run the pre-flight check**
```bash
python3 scripts/verify_system_ready.py
# All 23 checks should PASS including ESP32 connection
```

**Step 5.4 — Run a communication test**
```bash
python3 -c "
from uamc.hal.serial_bridge import SerialBridge
bridge = SerialBridge('/dev/ttyUSB0', 115200)
bridge.start()
import time; time.sleep(2)
tel = bridge.get_telemetry()
print('Telemetry from ESP32:', tel)
bridge.stop()
"
# Should print ultrasonic distances + other sensor data
```

---

### 📌 PHASE 6: Calibration (Tune Before Full Run)

**Step 6.1 — Calibrate steering center**
```
1. Open: firmware/esp32_firmware/esp32_config.h
2. Find: SERVO_CENTER_US  (currently 1500)
3. Change the value and re-upload firmware
4. Check if front wheels are perfectly straight
5. Keep adjusting until straight → that's your center value
```

**Step 6.2 — Calibrate ESC (VERY IMPORTANT — Do This First!)**
```
1. Turn on ESC with no battery to motor
2. Plug in battery
3. The ESC will beep to indicate it's in calibration mode
4. Open Arduino Serial Monitor
5. ESP32 will automatically send neutral throttle (1500 µs)
6. Most ESCs need you to set max then min then neutral
   (check your ESC manual)
```

**Step 6.3 — Calibrate camera (IPM trapezoid)**
```bash
# On the Pi, with camera mounted on car:
python3 scripts/calibrate_camera.py
# This opens a window — drag the 4 corners to match the road edge
# Press 'S' to save when happy
```

**Step 6.4 — Tune PID speed controller**
```
Open: config/rpi_tuning.py
Find: PID_KP, PID_KI, PID_KD
Start with: KP=0.8, KI=0.01, KD=0.05
Run the car at slow speed, observe behavior:
- If it overshoots: reduce KP
- If it's sluggish: increase KP
- If it oscillates: increase KD
```

---

### 📌 PHASE 7: First Full Autonomous Run

**Step 7.1 — Put car on test track**
- Make sure area is clear
- Have someone ready to pull the power plug if something goes wrong
- Start on a straight road section

**Step 7.2 — SSH into Pi from laptop**
```bash
ssh pi@<PI_IP>
cd /home/pi/iitb
```

**Step 7.3 — Run the autonomous system**
```bash
# Basic run (no YOLO, fastest):
python3 scripts/run_autonomous.py

# With YOLO object detection (recommended for competition):
python3 scripts/run_autonomous.py --use-yolo

# With AI steering (experimental):
python3 scripts/run_autonomous.py --use-yolo --use-pilotnet
```

**Step 7.4 — Monitor in real-time**
```
The terminal will print:
[PERCEPTION] Lane detected | Curvature: 0.02
[BEHAVIOR]   State: LANE_FOLLOW | Speed: 0.3 m/s
[CONTROL]    Steer: 0.12 | Throttle: 0.35
[ESP32-TEL]  Front: 85cm | Left: 120cm | Right: 110cm
```

**Step 7.5 — Emergency stop**
```
Press Ctrl+C in terminal → car stops immediately
OR
Disconnect the USB between Pi and ESP32 → ESP32 watchdog triggers, car stops in 200ms
```

---

## 📊 PART 5 — COMPLETE COMPONENT TO SOFTWARE MAP

| Hardware Component | Software File | What It Does |
|-------------------|---------------|-------------|
| USB Camera / Pi Cam | `uamc/hal/camera_interface.py` | Captures frames at 30fps |
| Camera frames | `uamc/perception/lane_detector.py` | Finds lane lines |
| Camera frames | `uamc/perception/ai_detector.py` | Detects signs/obstacles |
| Camera frames | `uamc/perception/traffic_lights.py` | Detects red/green lights |
| HC-SR04 Ultrasonic | `firmware/esp32_firmware/ultrasonic_filter.h` | Filtered distance measurement |
| Steering Servo | `firmware/esp32_firmware/esp32_config.h` (SERVO_* params) | PWM steering control |
| ESC + Motor | `firmware/esp32_firmware/esp32_config.h` (ESC_* params) | PWM speed control |
| MPU6050 IMU | `firmware/esp32_firmware/tinyml_motion.h` | Rollover/collision detection |
| Pi ↔ ESP32 USB | `uamc/hal/serial_bridge.py` | Command/telemetry bridge |
| All sensors combined | `uamc/planning/behavior_planner.py` | Decides what to do |
| Behavior output | `uamc/control/pure_pursuit.py` | Calculates steering angle |
| Speed control | `uamc/control/longitudinal_controller.py` | PID throttle control |

---

## ⚙️ PART 6 — ALL TUNING PARAMETERS (Quick Reference)

### Raspberry Pi Side → `config/rpi_tuning.py`
| Parameter | Default | What to change |
|-----------|---------|----------------|
| `CAMERA_INDEX` | 0 | Change to 1 if wrong camera |
| `TARGET_SPEED_MS` | 0.4 | Competition driving speed |
| `SLOW_SPEED_MS` | 0.2 | Near obstacles/turns |
| `PID_KP` | 0.8 | Speed control aggressiveness |
| `LOOKAHEAD_DIST` | 0.3 | Steering lookahead (bigger = smoother) |
| `STOP_DISTANCE_M` | 0.4 | Emergency stop distance |

### ESP32 Side → `firmware/esp32_firmware/esp32_config.h`
| Parameter | Default | What to change |
|-----------|---------|----------------|
| `SERVO_CENTER_US` | 1500 | Steering center (calibrate!) |
| `SERVO_LEFT_US` | 1100 | Full left turn |
| `SERVO_RIGHT_US` | 1900 | Full right turn |
| `ESC_NEUTRAL_US` | 1500 | Motor stop position |
| `ESC_MAX_US` | 1700 | Maximum forward speed |
| `PIN_SERVO` | 18 | Servo signal wire GPIO pin |
| `PIN_ESC` | 19 | ESC signal wire GPIO pin |

---

## 🚨 PART 7 — COMMON PROBLEMS AND FIXES

| Problem | Cause | Fix |
|---------|-------|-----|
| Car doesn't move | ESC not calibrated | Do ESC calibration (Phase 6.2) |
| Car steers in wrong direction | Servo wired backwards or center wrong | Adjust `SERVO_CENTER_US` |
| ESP32 not detected | Permission issue | Run `sudo usermod -a -G dialout $USER` then logout/login |
| Camera not found | Wrong index | Change `CAMERA_INDEX` from 0 to 1 in `rpi_tuning.py` |
| Car goes too fast | Speed too high | Reduce `TARGET_SPEED_MS` in `rpi_tuning.py` |
| Car doesn't detect obstacles | Sensors wired wrong | Check wiring, measure with Serial Monitor |
| AI model error | Missing model file | Run `python3 scripts/fetch_ai_models.py` |
| Import error on Pi | Missing library | Run `pip3 install -r requirements.txt` |

---

## 📅 PART 8 — RECOMMENDED TIMELINE

```
TODAY          → Buy missing components (ESP32, MPU6050, jumper wires)
Day 1 (Pi)    → Flash Pi OS, install software, test camera
Day 1 (ESP32) → Upload firmware, test via Serial Monitor
Day 2         → Wire everything together, test communication
Day 3         → Calibrate servo, ESC, camera
Day 4         → First autonomous run (small area, slow speed)
Day 5–7       → Tune parameters, test all competition scenarios
Competition   → UAMC at Techfest, IIT Bombay 🏆
```

---

## 🔗 IMPORTANT LINKS

- **GitHub Repo**: https://github.com/Rohith45-ch/iitb.git
- **Arduino IDE**: https://www.arduino.cc/en/software
- **Raspberry Pi Imager**: https://www.raspberrypi.com/software/
- **ESP32 Board Package URL**: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
- **HC-SR04 Datasheet**: https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf

---

*Last updated: 2026-10-30 | Version 3.0 — Combined Pi5 + ESC Architecture*
