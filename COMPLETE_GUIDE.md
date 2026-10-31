# 🚗 UAMC Autonomous Vehicle — COMPLETE MASTER MANUAL
### Techfest IIT Bombay | Raspberry Pi 5 + ESP32 + L298N + TT Motors
**Repository:** [https://github.com/Rohith45-ch/iitb.git](https://github.com/Rohith45-ch/iitb.git)  
**Hardware Source:** `Wiring_and_Pin_Map.pdf` (team document — authoritative hardware reference)  
**Firmware Source:** `firmware/esp32_firmware/esp32_config.h` + `esp32_vehicle_controller.ino`  
**Last Updated:** October 31, 2026

> [!IMPORTANT]
> This is your **single source of truth**. Every pin, every wire, every component, every firmware value here is taken **directly from `Wiring_and_Pin_Map.pdf`** and cross-checked against the firmware. Do not use values from any older document.

---

## 📦 PART 1 — VERIFIED HARDWARE INVENTORY (per PDF §1)

| # | Component | Exact Spec / Model | Role | Qty |
|---|-----------|-------------------|------|-----|
| 1 | **ESP32 DevKit V1 (30-pin)** | Espressif, standard 30-pin layout | Motor, servo, sonar, E-stop control | 1 |
| 2 | **Raspberry Pi 5** | 8GB RAM, Pi OS 64-bit (Bookworm) | Vision and planner; live at `rohith@10.94.129.58` | 1 |
| 3 | **Pi Camera Rev 1.3** | OV5647 5MP; **15-to-22 pin CSI cable** to Pi 5 CAM port | Road lane, traffic light, sign, pedestrian detection | 1 |
| 4 | **L298N Motor Driver** | Dual H-bridge module, one board | Drives **both** TT gear motors | 1 |
| 5 | **TT Gear Motor** | 3–9 V rated (use 3–9V type; plain 6V TT is rated lower than our 7V supply) | Left and right wheel drive | 2 |
| 6 | **3S LiPo Battery** | **2200 mAh, 11.1 V nominal / 12.6 V full** | Main drive power source | 1 |
| 7 | **Buck Converter — 7 V** | 3 A+ output capacity | Steps 3S LiPo down to 7 V for motor supply | 1 |
| 8 | **Buck Converter — 5 V** | 3 A+ output capacity | Powers servo, HC-SR04, and L298N logic | 1 |
| 9 | **Steering Servo SG90 / MG90S** | 9 g micro servo, 5 V | Front-wheel Ackermann steering | 1 |
| 10 | **HC-SR04 Ultrasonic Sensor** | Front centre only | Obstacle detection and emergency braking | 1 |
| 11 | **E-stop Button** | 22 mm latching, **2 contacts** (1× NC + 1× NO) | Cuts main battery line (NC); signals ESP32 (NO) | 1 |
| 12 | **10 A Inline Fuse + Holder** | — | Battery positive lead protection | 1 |
| 13 | **Resistors** | 1 kΩ, 2 kΩ, 10 kΩ | Sonar echo voltage divider (1k+2k); E-stop pull-up (10k) | 1 each |
| 14 | **Capacitor** | 470–1000 µF, 16 V | Across servo 5 V supply rail | 1 |
| 15 | **USB-A to Micro-USB Cable** | Data cable (NOT charge-only) | Pi 5 USB-A ↔ ESP32 Micro-USB — only Pi↔ESP32 link | 1 |
| 16 | **Power Bank** | 5 V / 3 A output | Raspberry Pi 5 dedicated power via USB-C | 1 |
| 17 | **400-Point Breadboard** | Solderless | ESP32 carrier + common ground rail | 1 |

### 🟡 Optional / Not Used in Round 1
- **SmartElex RLS-06 (6-IR Array):** No firmware code for it yet. Do not wire for Round 1.
- **Wheel Encoders:** Pins 25/26 defined but leave **unconnected**. Speed is open-loop.
- **MPU6050 IMU:** Not required for Round 1.

---

## ⚡ PART 2 — POWER TREE (per PDF §2)

```
3S LiPo (+) ──► E-stop NC contact ──► 10 A fuse ──┬──► 7 V buck ──► L298N +12V (VS) ──► motors
                                                    │
                                                    └──► 5 V buck ──┬──► Servo (+) + 470–1000 µF cap
                                                                    ├──► HC-SR04 VCC
                                                                    └──► L298N +5V logic (5V jumper REMOVED)

3S LiPo (−) ──► common GND ──► ESP32 GND ──► L298N GND ──► Servo (−) ──► HC-SR04 GND ──► buck GNDs

Power bank (5 V / 3 A) ──► Pi 5 USB-C                  (Pi ONLY — never from motor battery)
Pi 5 USB-A              ──► ESP32 Micro-USB              (powers ESP32; do NOT also feed ESP32 5V pin)
```

> [!WARNING]
> **Why 7 V for motors:** TT motors are rated 3–9 V. A 3S LiPo gives 11–12.6 V. The L298N drops ~2 V internally, so motors see ~5 V. **Adjust the 7 V buck with a multimeter before connecting anything.** Set it to exactly 7 V.

> [!CAUTION]
> **Common ground is mandatory.** Every GND in the system — ESP32, L298N, servo, HC-SR04, both bucks — must connect at **one point**. A missing ground link causes random ESP32 resets, servo jitter, and bad sonar readings.

> [!IMPORTANT]
> **Do NOT connect the ESP32 5 V pin** when it is already powered via USB from the Pi. Dual-feeding the 5 V rail will damage the ESP32.

---

## 🔌 PART 3 — PIN MAP (per PDF §3 — every used pin)

| GPIO | Connected To | Direction | Firmware Constant | Notes |
|------|-------------|-----------|-------------------|-------|
| **18** | Servo signal wire (yellow / orange) | PWM out, 50 Hz | `PIN_STEER_SERVO` | 1000–2000 µs; mid = 1500 µs |
| **19** | L298N ENA **and** ENB (both, tied together) | PWM out, 20 kHz | `PIN_MOTOR_PWM` | Remove ENA/ENB jumpers first |
| **22** | L298N IN1 **and** IN3 | Digital out | `PIN_MOTOR_DIR_A` | HIGH = both motors forward |
| **23** | L298N IN2 **and** IN4 | Digital out | `PIN_MOTOR_DIR_B` | LOW = both motors forward |
| **5**  | HC-SR04 TRIG | Digital out, 10 µs pulse | `PIN_US_TRIG` | Shared trigger pulse |
| **35** | HC-SR04 ECHO via **1 kΩ / 2 kΩ divider** | Input-only pin | `PIN_US_ECHO_CENTER` | Only sonar fitted. Divider gives 3.33 V |
| **27** | E-stop NO contact to GND; 10 kΩ pull-up to 3.3 V | Input, active-LOW | `PIN_ESTOP_INPUT` | LOW = button pressed |
| **16** | (Unused when USB connected) | UART2 RX | `PIN_UART_RX` | Serial2 — only if UART active |
| **17** | (Unused when USB connected) | UART2 TX | `PIN_UART_TX` | Serial2 — only if UART active |
| **34** | Leave **unconnected** | Input | `PIN_US_ECHO_LEFT` | No sensor fitted |
| **32** | Leave **unconnected** | Input | `PIN_US_ECHO_RIGHT` | No sensor fitted |
| **33** | Leave **unconnected** | Input | `PIN_US_ECHO_SIDE` | No sensor fitted |
| **25** | Leave **unconnected** | Input, pull-up | `PIN_ENCODER_LEFT` | No encoder fitted |
| **26** | Leave **unconnected** | Input, pull-up | `PIN_ENCODER_RIGHT` | No encoder fitted |
| USB  | Pi 5 USB-A port | Serial, 115200 baud | `Serial` | Pi sees it as `/dev/ttyUSB0` |

> [!NOTE]
> Pins 13, 14, 21 are free if the optional IR array (RLS-06) is added later. The firmware has no code for it yet — do not wire it for Round 1.

---

## 🔗 PART 4 — COMPLETE CONNECTION TABLE (per PDF §4, every wire)

### A. Motor Driver (L298N) Connections

| From | To | Wire / Note |
|------|----|-------------|
| ESP32 GPIO 19 | L298N ENA **and** ENB | Remove the ENA/ENB jumpers first |
| ESP32 GPIO 22 | L298N IN1 **and** IN3 | Both motors move forward together |
| ESP32 GPIO 23 | L298N IN2 **and** IN4 | Swap a motor's two wires if it turns backwards |
| L298N OUT1 / OUT2 | Left TT motor | Two motor wires |
| L298N OUT3 / OUT4 | Right TT motor | Two motor wires |
| 7 V buck out (+) | L298N +12V (VS) | Motor supply — after the fuse |
| 5 V buck out (+) | L298N +5V logic | Only with the 5 V jumper **removed** from L298N board |
| Common GND | L298N GND | Must join all other GNDs |

### B. Steering Servo Connections

| From | To | Wire / Note |
|------|----|-------------|
| ESP32 GPIO 18 | Servo signal wire | Yellow or orange wire |
| 5 V buck out (+) | Servo red (+) wire | **+ 470–1000 µF capacitor across this rail** |
| Common GND | Servo brown / black (−) wire | |

### C. Ultrasonic Sensor (HC-SR04) Connections

| From | To | Wire / Note |
|------|----|-------------|
| ESP32 GPIO 5 | HC-SR04 TRIG pin | Direct connection |
| HC-SR04 ECHO pin | 1 kΩ resistor → GPIO 35 | Voltage divider |
| GPIO 35 node | 2 kΩ resistor → GND | Gives ≈3.33 V at GPIO 35 |
| 5 V buck out (+) | HC-SR04 VCC | 5 V sensor |
| Common GND | HC-SR04 GND | |

**Voltage divider diagram:**
```
HC-SR04 ECHO (5V) ──[1 kΩ]──┬── ESP32 GPIO 35
                              │
                           [2 kΩ]
                              │
                             GND

V_GPIO35 = 5V × 2kΩ/(1kΩ+2kΩ) = 3.33 V  ✅ Safe for ESP32
```

### D. E-Stop Connections

| From | To | Wire / Note |
|------|----|-------------|
| E-stop NO contact | GPIO 27 to GND | When pressed: closes to GND = LOW |
| 10 kΩ resistor | GPIO 27 to 3.3 V | External pull-up |
| E-stop NC contact | Battery (+) line, before the fuse | When pressed: opens = cuts ALL power |

### E. Pi 5 ↔ ESP32 Link

| From | To | Note |
|------|----|------|
| Pi 5 USB-A port | ESP32 Micro-USB | **Only** link between Pi and ESP32 |
| Pi 5 CAM port | Pi Camera Rev 1.3 | 15-to-22 pin CSI ribbon cable |
| Power bank (5V/3A) | Pi 5 USB-C | Pi 5 dedicated power — never from motor battery |

---

## 🛠️ PART 5 — L298N TERMINAL REFERENCE (per PDF §5)

| L298N Terminal | Connect To | Note |
|---------------|------------|------|
| +12V (VS) | 7 V buck (+) | Motor supply — NOT battery direct |
| GND | Common GND | |
| +5V | 5 V buck (+), or leave unused | **Remove the 5V jumper** on the L298N board if feeding logic from buck |
| ENA / ENB | ESP32 GPIO 19 | PWM speed control — **jumpers removed** |
| IN1 / IN2 | ESP32 GPIO 22 / 23 | Motor A direction (IN1/IN2 tied to IN3/IN4) |
| IN3 / IN4 | ESP32 GPIO 22 / 23 | Motor B direction |
| OUT1 / OUT2 | Left TT motor | |
| OUT3 / OUT4 | Right TT motor | |

**Forward logic:** `IN1 HIGH + IN2 LOW` → both motors forward  
**Reverse logic:** `IN1 LOW + IN2 HIGH` → both motors reverse  
Both motors follow the same pins. If one motor turns backwards, **swap that motor's own two wires** at OUT1/OUT2 or OUT3/OUT4.

---

## ⚙️ PART 6 — FIRMWARE CONFIG CHANGES (per PDF §6 — MUST DO)

### 1. `firmware/esp32_firmware/esp32_config.h`

| Setting | Correct Value | Why |
|---------|--------------|-----|
| `USE_ESC_MOTOR_DRIVER` | **`0`** | Selects L298N path (20 kHz PWM). Default `1` selects RC ESC path which will NOT drive L298N. |

All other firmware pin constants are already correct — see Part 3.

### 2. `config/rpi_tuning.py`

| Setting | Correct Value | Why |
|---------|--------------|-----|
| `wheelbase_m` | **`0.170`** | This car's actual wheelbase is 170 mm. Old docs had 0.260 for a different car — do NOT use. |
| `serial_port` | **`/dev/ttyUSB0`** | USB cable appears as ttyUSB0 on Pi. Already correct. |
| `baudrate` | **`115200`** | Matches firmware `UART_BAUDRATE`. Already correct. |

### 3. Sonar: Pins 34, 32, 33 (per PDF §6 item 4)
The firmware reads all four sonar echo pins. Confirm the firmware treats a missing echo as **"no obstacle"** (≥ max range), **not** as "0 cm" (which would trigger a false emergency stop). CHECK in `esp32_vehicle_controller.ino`.

### 4. Encoder: Pins 25, 26 (per PDF §6 item 5)
The firmware may attach interrupts to encoder pins. Confirm the drive **does not block or wait** on encoder counts. If it does, the car will not move. CHECK in `esp32_vehicle_controller.ino`.

### 5. E-stop Pin 27 (per PDF §6 item 6)
Confirm `PIN_ESTOP_INPUT` is configured as `INPUT_PULLUP` **or** has the external 10 kΩ pull-up wired. CHECK.

---

## 🚀 PART 7 — BRING-UP ORDER (per PDF §8 — follow exactly)

1. **Fuse out. Battery disconnected.** Power Pi from power bank, ESP32 from Pi USB-A only. Confirm Pi sees ESP32 at `/dev/ttyUSB0`.
2. **Check every connection** with battery disconnected: continuity, no short between + and −, correct polarity everywhere.
3. **Fit the fuse.** Connect 3S LiPo with **wheels off the ground**.
4. **Press E-stop:** Motors and servo must stop immediately. Release before next step.
5. **Measure buck outputs:** 7 V buck on motor rail, 5 V buck on logic rail. Adjust with a multimeter before connecting L298N.
6. **Small forward throttle:** Both wheels turn forward. Reverse one motor's two wires at OUT terminals if it runs backwards.
7. **Sweep steering:** Both front wheels turn same direction, nothing binds at full lock.
8. **Sonar test:** Hold a hand in front — distance reading changes sensibly. **Only then drive on the track.**

---

## 🔧 PART 8 — TUNING QUICK-REFERENCE

### ESP32 Parameters: [`firmware/esp32_firmware/esp32_config.h`](firmware/esp32_firmware/esp32_config.h)

| Constant | Value | Purpose / How to Tune |
|----------|-------|----------------------|
| `USE_ESC_MOTOR_DRIVER` | **`0`** | L298N mode — **do not change** |
| `SERVO_MID_US` | `1500` | Steering neutral trim. +50 µs if pulls left, −50 µs if pulls right |
| `SERVO_MIN_US` | `1000` | Full left lock |
| `SERVO_MAX_US` | `2000` | Full right lock |
| `MOTOR_MIN_START_PWM` | `35` | Minimum PWM to overcome TT gearbox friction (0–255) |
| `MOTOR_MAX_SAFE_PWM` | `220` | Maximum PWM cap |
| `PIN_STEER_SERVO` | `18` | Servo signal GPIO |
| `PIN_MOTOR_PWM` | `19` | L298N ENA/ENB GPIO |
| `PIN_MOTOR_DIR_A` | `22` | L298N IN1+IN3 GPIO |
| `PIN_MOTOR_DIR_B` | `23` | L298N IN2+IN4 GPIO |
| `PIN_US_TRIG` | `5` | HC-SR04 trigger GPIO |
| `PIN_US_ECHO_CENTER` | `35` | HC-SR04 echo GPIO (via divider) |
| `PIN_ESTOP_INPUT` | `27` | E-stop GPIO |

### Raspberry Pi Parameters: [`config/rpi_tuning.py`](config/rpi_tuning.py)

| Constant | Value | Purpose / How to Tune |
|----------|-------|----------------------|
| `wheelbase_m` | **`0.170`** | 17.0 cm wheelbase — this car. Do NOT use 0.260 |
| `lookahead_min_m` | `0.28` | Pure pursuit lookahead. Increase if car wiggles |
| `v_cruise_ms` | `0.45` | Cruising speed. Reduce to `0.30` for first runs |
| `obstacle_emergency_dist_m` | `0.25` | Emergency stop trigger distance (25 cm) |
| `serial_port` | `/dev/ttyUSB0` | USB serial port to ESP32 |
| `baudrate` | `115200` | Must match `UART_BAUDRATE` in firmware |

---

## 🔍 PART 9 — FAULT FINDER (per PDF §9)

| Symptom | Likely Cause |
|---------|-------------|
| Motors hum but do not turn | ENA/ENB not wired to GPIO 19, or PWM below `MOTOR_MIN_START_PWM` (try increasing from 35) |
| Motors very hot after a minute | Motor supply too high — check 7 V buck; 3S LiPo must NOT reach L298N directly |
| Servo jitters | Missing 470–1000 µF capacitor on servo supply, or servo powered from ESP32 3.3 V pin |
| Sonar reads 0 or max constantly | ECHO not divided (5 V going into ESP32), TRIG and ECHO swapped, or unfitted sonar pins picked up |
| ESP32 resets when motors start | Shared ground missing, or supply sagging under load — add the cap, check the 5 V buck |
| Car moves after E-stop press | E-stop NC contact not in battery line, or GPIO 27 wired to NC contact instead of NO contact |
| Pi cannot open `/dev/ttyUSB0` | USB cable is charge-only (no data lines), or ESP32 not powered |

---

## 📁 PART 10 — SOFTWARE ARCHITECTURE

```
iitb/
├── firmware/esp32_firmware/
│   ├── esp32_config.h               ← All pin & tuning constants (this is your bible)
│   └── esp32_vehicle_controller.ino ← FreeRTOS dual-core main firmware
├── config/
│   └── rpi_tuning.py                ← All Pi-side tuning (wheelbase=0.170, port, speeds)
├── scripts/
│   ├── run_autonomous.py            ← Main autonomy launcher
│   ├── verify_system_ready.py       ← Pre-flight diagnostic
│   ├── detect_hardware.py           ← Auto-detect camera & ESP32 ports
│   └── record_qualification_run.py  ← Round 1 video recorder
└── uamc/
    ├── perception/  (lane, sign, traffic light, obstacle detectors)
    ├── planning/    (behavior FSM)
    ├── control/     (pure pursuit steering, PID speed)
    └── hal/         (serial bridge, camera interface)
```

---

## 🏆 PART 11 — ROUND 1 LAUNCH COMMANDS

```bash
# SSH into Pi 5 (hotspot: Heisenberg)
ssh rohith@10.94.129.58

# Pull latest code
cd ~/iitb && git pull origin main

# Run pre-flight checks
python3 scripts/verify_system_ready.py

# Launch autonomous run
python3 scripts/run_autonomous.py --serial-port /dev/ttyUSB0 --use-yolo --no-gui

# Record qualification video
python3 scripts/record_qualification_run.py --output-video round1_submission.mp4
```

---

*Single Source of Truth — Built from `Wiring_and_Pin_Map.pdf` + `esp32_config.h` · [Rohith45-ch/iitb](https://github.com/Rohith45-ch/iitb)*
