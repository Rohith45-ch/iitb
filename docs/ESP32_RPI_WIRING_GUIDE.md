# ESP32 & Raspberry Pi — Complete Hardware Wiring Guide
### UAMC Techfest IIT Bombay | Based on `Wiring_and_Pin_Map.pdf`

> [!IMPORTANT]
> This guide is derived directly from **`Wiring_and_Pin_Map.pdf`** (team hardware spec document). All pins, resistor values, and wiring instructions here are the authoritative source for this build.

---

## 1. System Overview

```
                    ┌────────────────────────────┐
                    │   Power Bank (5V / 3A)     │
                    └────────────┬───────────────┘
                                 │ USB-C
                                 ▼
                        [ Raspberry Pi 5 ]
                                 │
                       USB-A to Micro-USB
                       (115200 baud, /dev/ttyUSB0)
                                 │
                        [ ESP32 DevKit V1 ]
                       /         |           \
                  GPIO 18    GPIO 19      GPIO 5 / 35
                  Servo      L298N ENA/ENB   HC-SR04
                             GPIO 22/23       Sonar
                             L298N IN1-4      

┌──────────────────────────────────────────────────────┐
│              3S LiPo (11.1V / 2200mAh)               │
└──┬───────────────────────────────────────────────────┘
   │
   ▼ NC contact
 [ E-Stop ] ── NO contact ──► GPIO 27 (+ 10kΩ to 3.3V)
   │
   ▼
 [10A Fuse]
   │
   ├──► [7V Buck] ──► L298N +12V(VS) ──► TT Motors
   │
   └──► [5V Buck] ──► Servo (+) + 470-1000µF cap
                  ──► HC-SR04 VCC
                  ──► L298N +5V logic (5V jumper removed)

All GNDs ──► Single common GND point
```

> [!WARNING]
> **Common Ground is essential.** Every device — ESP32, L298N, both bucks, servo, HC-SR04 — must share one common GND point. A missing GND link causes random resets, servo jitter, and corrupt sonar data.

---

## 2. Pi 5 ↔ ESP32 Communication

The **only** link between Pi 5 and ESP32 is a USB-A to Micro-USB data cable. No UART GPIO wires needed.

| Raspberry Pi 5 | ESP32 | Note |
|---------------|-------|------|
| USB-A port | Micro-USB port | Data + ESP32 power |
| — | GPIO 16 (RX2) | Unused when USB active |
| — | GPIO 17 (TX2) | Unused when USB active |

- Pi 5 sees ESP32 as **`/dev/ttyUSB0`** at **115200 baud**
- Pi 5 powered **separately** from power bank → USB-C port
- Do **NOT** also connect ESP32 5V pin when using USB power

---

## 3. Complete Pin Assignment (per PDF §3)

### A. Motor Control — L298N H-Bridge

> [!IMPORTANT]
> `USE_ESC_MOTOR_DRIVER` must be set to **`0`** in `esp32_config.h` for L298N mode.

| ESP32 GPIO | L298N Terminal | Direction | Firmware Name | Notes |
|-----------|----------------|-----------|---------------|-------|
| **GPIO 19** | ENA **and** ENB (tied together) | PWM out, 20 kHz | `PIN_MOTOR_PWM` | Remove ENA/ENB jumpers from board first |
| **GPIO 22** | IN1 **and** IN3 (tied together) | Digital out | `PIN_MOTOR_DIR_A` | HIGH = both motors forward |
| **GPIO 23** | IN2 **and** IN4 (tied together) | Digital out | `PIN_MOTOR_DIR_B` | LOW = both motors forward |

**L298N Power Rails:**

| L298N Terminal | Source | Note |
|---------------|--------|------|
| +12V (VS) | 7 V buck output (+) | Motor supply — set buck to 7V with meter |
| GND | Common GND | |
| +5V | 5 V buck output (+) | **Remove** the 5V jumper on L298N board |

**Motor Outputs:**

| L298N Terminal | Goes To |
|---------------|---------|
| OUT1 / OUT2 | Left TT gear motor (two wires) |
| OUT3 / OUT4 | Right TT gear motor (two wires) |

> [!TIP]
> If one motor turns backwards, **swap that motor's own two output wires** at the L298N OUT terminals. Do not change the GPIO logic.

**Direction truth table:**
```
Forward:  GPIO22 (DIR_A) = HIGH,  GPIO23 (DIR_B) = LOW
Reverse:  GPIO22 (DIR_A) = LOW,   GPIO23 (DIR_B) = HIGH
Stop:     GPIO19 (PWM)   = 0
```

### B. Steering Servo (SG90 / MG90S)

| ESP32 GPIO | Servo Wire | Source | Notes |
|-----------|-----------|--------|-------|
| **GPIO 18** | Signal (yellow / orange) | — | 50 Hz PWM, 1000–2000 µs; mid = 1500 µs |
| — | Red (+) | 5 V buck (+) | **+ 470–1000 µF cap across this rail** |
| GND | Brown / Black (−) | Common GND | |

> [!CAUTION]
> Never power servo from ESP32 3.3 V or 5 V pin — it will cause resets under load. Always use the 5 V buck with the capacitor.

### C. Ultrasonic Sensor HC-SR04 (Front Centre Only)

**Voltage divider (required — HC-SR04 ECHO outputs 5 V, ESP32 max is 3.3 V):**

```
HC-SR04 ECHO (5V) ──[1 kΩ]──┬──► ESP32 GPIO 35
                              │
                           [2 kΩ]
                              │
                             GND

Result: V_GPIO35 = 5V × 2000/(1000+2000) = 3.33V ✅
```

| ESP32 GPIO | HC-SR04 Pin | Notes |
|-----------|-------------|-------|
| **GPIO 5** | TRIG | Direct connection, 10 µs pulse out |
| **GPIO 35** | ECHO (via 1kΩ/2kΩ divider) | Input-only pin — must use divider |
| — | VCC | 5 V buck (+) |
| GND | GND | Common GND |

**Unused sonar pins — leave completely unconnected:**

| GPIO | Firmware Name | Status |
|------|--------------|--------|
| 34 | `PIN_US_ECHO_LEFT` | No sensor — leave floating |
| 32 | `PIN_US_ECHO_RIGHT` | No sensor — leave floating |
| 33 | `PIN_US_ECHO_SIDE` | No sensor — leave floating |

### D. E-Stop Button (22 mm latching, 2-contact)

The E-stop has **two separate contacts** — wire them differently:

| Contact | Wired To | Effect When Pressed |
|---------|----------|---------------------|
| **NC (Normally Closed)** | Battery (+) line, before the 10A fuse | **Opens** → cuts ALL motor power |
| **NO (Normally Open)** | GPIO 27 to GND; 10 kΩ from GPIO 27 to 3.3V | **Closes** → pulls GPIO 27 LOW |

ESP32 reads `PIN_ESTOP_INPUT` (GPIO 27):
- **HIGH** = E-stop released → normal operation
- **LOW** = E-stop pressed → firmware emergency stop

### E. Unused Encoder Pins

| GPIO | Firmware Name | Status |
|------|--------------|--------|
| 25 | `PIN_ENCODER_LEFT` | No encoder — leave **unconnected** |
| 26 | `PIN_ENCODER_RIGHT` | No encoder — leave **unconnected** |

---

## 4. Firmware Settings to Apply

Open `firmware/esp32_firmware/esp32_config.h` and verify:

```c
#define USE_ESC_MOTOR_DRIVER     0      // ← MUST BE 0 for L298N

#define PIN_STEER_SERVO          18     // Servo signal
#define PIN_MOTOR_PWM            19     // L298N ENA+ENB
#define PIN_MOTOR_DIR_A          22     // L298N IN1+IN3
#define PIN_MOTOR_DIR_B          23     // L298N IN2+IN4
#define PIN_US_TRIG              5      // HC-SR04 Trig
#define PIN_US_ECHO_CENTER       35     // HC-SR04 Echo (via divider)
#define PIN_ESTOP_INPUT          27     // E-Stop

#define MOTOR_LEDC_FREQ          20000  // 20 kHz PWM for L298N
#define MOTOR_MIN_START_PWM      35     // Min PWM to move TT motors
#define MOTOR_MAX_SAFE_PWM       220    // Max PWM cap
```

Open `config/rpi_tuning.py` and verify:

```python
wheelbase_m = 0.170    # 17.0 cm — THIS car (NOT 0.260 — that was a different car)
serial_port = "/dev/ttyUSB0"
baudrate    = 115200
```

---

## 5. Serial Packet Protocol

### Command Packet (Pi → ESP32, sent at 30 Hz)
```
#CMD,<steer>,<throttle>,<estop>*
```
- `<steer>`: −1.0 (full left) to +1.0 (full right), 0.0 = straight
- `<throttle>`: −1.0 (reverse) to +1.0 (forward), 0.0 = stop
- `<estop>`: 0 = normal, 1 = emergency stop

### Telemetry Packet (ESP32 → Pi, sent at 30 Hz)
```
#TEL,<us_l>,<us_c>,<us_r>,<us_s>,<enc_l>,<enc_r>,<yaw>,<estop>*
```
- `<us_c>` is the only live sonar reading; others will be at max range (no sensor)
- `<enc_l>`, `<enc_r>`: 0 (no encoders fitted)
- `<yaw>`: 0.0 (no IMU fitted)

---

## 6. Fault Finder (per PDF §9)

| Symptom | Check |
|---------|-------|
| Motors hum but don't turn | ENA/ENB jumpers still on L298N; or PWM < `MOTOR_MIN_START_PWM` |
| Motors very hot | 7V buck too high — re-measure and re-adjust before running |
| Servo jitters | Missing 470–1000 µF capacitor; or servo on ESP32 pin, not buck |
| Sonar reads 0 or 2.5m always | ECHO divider missing (5V into GPIO); TRIG and ECHO swapped |
| ESP32 resets at motor start | GND not common; or 5V buck sagging — check capacitor |
| Car moves after E-stop | NC contact not in battery line; or NO/NC contacts swapped at GPIO 27 |
| `/dev/ttyUSB0` not found | Charge-only USB cable; or ESP32 not powered |
