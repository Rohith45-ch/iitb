# ESP32 & Raspberry Pi Hardware Wiring & Interface Guide

This guide details the exact electrical connections, level-shifting, pinouts, and communication protocols between the **Raspberry Pi** (High-Level Perception & Planning) and the **ESP32** (Real-Time Actuation & Sensor Fusion) for the **AML-Rover-V1** vehicle.

---

## 1. System Block Diagram & Power Architecture

```
                       +-----------------------------+
                       |    2S / 3S LiPo Battery     |
                       |      (7.4V - 11.1V)         |
                       +--------------+--------------+
                                      |
                      [ 15A Master Kill Switch / E-Stop ]
                                      |
              +-----------------------+-----------------------+
              |                                               |
     +--------v--------+                             +--------v--------+
     |   High-Current  |                             | Motor Driver    |
     | 5V / 5A Buck IC |                             | (TB6612/BTS7960)|
     +--------+--------+                             +--------+--------+
              |                                               |
    +---------+---------+                            [ DC Drive Motor ]
    |                   |
+---v-------------+ +---v-------------+
| Raspberry Pi 4B | |  ESP32 DevKit   |
| (Perception/FSM)| | (Actuator/Sens) |
+--------+--------+ +---+-------------+
         |              |
         +---[ UART ]---+
       (115200 bps Serial)
```

> [!WARNING]
> **Common Ground Requirement**: The Ground (GND) of the LiPo Battery, Buck Converter, Raspberry Pi, ESP32, and Motor Driver **MUST all be tied together**. Without a common ground reference, serial signals will suffer framing errors and sensor readings will drift.

---

## 2. Raspberry Pi $\leftrightarrow$ ESP32 Inter-Board Communication

Communication runs over a high-speed, direct hardware UART link.

| Raspberry Pi Pin (40-Pin Header) | RPi Function | ESP32 Pin | ESP32 Function | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Pin 8 (GPIO 14)** | UART TXD | **GPIO 16** | Serial2 RXD | RPi transmits commands (`#CMD`) |
| **Pin 10 (GPIO 15)**| UART RXD | **GPIO 17** | Serial2 TXD | RPi receives telemetry (`#TEL`) |
| **Pin 6, 9, or 14** | GND | **GND** | GND | Common reference ground |

*Note: Alternatively, you can connect the ESP32 to the Raspberry Pi using a standard USB-to-MicroUSB cable (which appears as `/dev/ttyUSB0` or `/dev/ttyACM0` on the Pi).*

---

## 3. ESP32 Pin Allocation & Sensor Wiring

### A. Ultrasonic (HC-SR04) Wiring & 3.3V Voltage Divider
HC-SR04 sensors run on **5V VCC**, meaning their **ECHO** pin outputs a **5V digital pulse**. Because the ESP32 GPIO pins are strictly **3.3V logic**, connecting 5V directly will destroy the GPIO port!

Use a simple 2-resistor voltage divider on the ECHO line:
$$\text{ECHO (5V)} \longrightarrow [1\text{ k}\Omega] \longrightarrow \text{ESP32 GPIO 35} \longrightarrow [2\text{ k}\Omega] \longrightarrow \text{GND}$$
$$V_{out} = 5\text{V} \times \frac{2\text{k}\Omega}{1\text{k}\Omega + 2\text{k}\Omega} = 3.33\text{V} \quad \text{(Safe for ESP32)}$$

| Sensor Position | Trig Pin (ESP32) | Echo Pin (ESP32) | Status | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Front Center** | **GPIO 5** | **GPIO 35** (via divider) | **Required (Round 1)** | Emergency Stop obstacle brake |
| **Front Left** | **GPIO 5** | **GPIO 34** | Unused / Optional | Leave disconnected |
| **Front Right** | **GPIO 5** | **GPIO 32** | Unused / Optional | Leave disconnected |
| **Side (Parking)** | **GPIO 5** | **GPIO 33** | Unused / Optional | Leave disconnected |

### B. Steering Servo & ESC (Electronic Speed Controller) Wiring

| Device | Signal Description | ESP32 Pin | Signal Type |
| :--- | :--- | :--- | :--- |
| **Steering Servo (Micro Servo 9g)** | PWM Signal (Orange/Yellow wire) | **GPIO 18** | LEDC Channel 0 (50 Hz, 16-bit) |
| **ESC Throttle** | PWM Throttle Signal (White wire) | **GPIO 19** | LEDC Channel 1 (50 Hz RC ESC servo signal) |
| **ESC Ground** | Common Reference Ground (Black wire) | **GND** | Must share common ground with ESP32 |

*(Note: The ESC is powered by the 7.4V 2S LiPo drive battery. The ESC's internal BEC provides 5V to the steering servo. The ESP32 is powered via USB from the Raspberry Pi 5).*

### C. Wheel Encoders & Safety Kill Switch

| Device | Pin Description | ESP32 Pin | Configuration |
| :--- | :--- | :--- | :--- |
| **Left Wheel Encoder** | Signal Output | **GPIO 25** | Hardware Interrupt (`RISING`), Pullup |
| **Right Wheel Encoder** | Signal Output | **GPIO 26** | Hardware Interrupt (`RISING`), Pullup |
| **Hardware E-Stop Button** | Emergency Kill Sense | **GPIO 27** | Digital Input (`INPUT_PULLUP`, Active LOW) |

---

## 4. Raspberry Pi Setup Instructions

### 1. Enable Hardware Serial on Raspberry Pi
By default, the Raspberry Pi uses its primary UART for the Linux Bluetooth controller. To redirect it to GPIO 14/15:

1. Open `/boot/firmware/config.txt` (or `/boot/config.txt`):
   ```bash
   sudo nano /boot/firmware/config.txt
   ```
2. Add or ensure the following lines exist:
   ```ini
   enable_uart=1
   dtoverlay=disable-bt
   ```
3. Disable Linux serial console on the port:
   ```bash
   sudo systemctl stop serial-getty@ttyAMA0.service
   sudo systemctl disable serial-getty@ttyAMA0.service
   ```
4. Reboot the Raspberry Pi:
   ```bash
   sudo reboot
   ```
5. The direct serial port is now available at `/dev/ttyAMA0` (or symlinked to `/dev/serial0`).

### 2. Grant Serial Permissions
Ensure the current user has access to dialout:
```bash
sudo usermod -a -G dialout $USER
```

---

## 5. Packet Communication Protocol Specification

### Command Packet (Raspberry Pi $\rightarrow$ ESP32)
Sent at 30 Hz – 50 Hz from `uamc/hal/serial_bridge.py`:
```
#CMD,<steer>,<throttle>,<estop>*
```
- `<steer>`: Floating point in range `[-1.000, +1.000]` (`-1.0` = full left $28^\circ$, `+1.0` = full right $28^\circ$, `0.0` = straight ahead).
- `<throttle>`: Floating point in range `[-1.000, +1.000]` (`+0.5` = forward cruising, `-0.5` = active dynamic braking, `0.0` = neutral/idle).
- `<estop>`: Integer flag (`0` = normal operation, `1` = instant emergency stop).
- *Example*: `#CMD,-0.125,0.450,0*\n`

### Telemetry Packet (ESP32 $\rightarrow$ Raspberry Pi)
Sent at 30 Hz from Core 1 of the ESP32:
```
#TEL,<us_l>,<us_c>,<us_r>,<us_s>,<enc_l>,<enc_r>,<yaw>,<estop>*
```
- `<us_l>`, `<us_c>`, `<us_r>`, `<us_s>`: Distances in meters with 2 decimal precision (e.g. `0.85,1.20,0.92,0.18`).
- `<enc_l>`, `<enc_r>`: Cumulative encoder tick count since boot.
- `<yaw>`: Heading yaw angle in degrees.
- `<estop>`: Hardware kill switch status (`0` = safe, `1` = triggered).
- *Example*: `#TEL,1.15,1.20,1.18,0.18,450,452,0.0,0*\n`
