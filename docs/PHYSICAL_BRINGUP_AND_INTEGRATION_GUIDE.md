# Complete Physical Bring-Up, Integration & Tuning Guide
## Urban Autonomous Mobility Challenge (UAMC) — 1:10 Autonomous Vehicle

This step-by-step guide walks you from unboxing your **Raspberry Pi 5** and **ESP32** to having a fully working, self-driving autonomous vehicle on the track.

---

## **Overview of the 5 Bring-Up Phases**

```
┌────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: Flash the ESP32 (Plug into Laptop via USB)                    │
│   • Install Arduino IDE + ESP32 Board Core                             │
│   • Open firmware/esp32_firmware/esp32_vehicle_controller.ino          │
│   • Click Upload -> Verify #TEL packet output in Serial Monitor        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ PHASE 2: Setup Raspberry Pi 5 (Plug SD Card into Laptop)              │
│   • Flash Raspberry Pi OS 64-bit using Raspberry Pi Imager             │
│   • SSH from Laptop into Pi via Wi-Fi                                  │
│   • Clone repo -> run `pip install -r requirements.txt`                │
│   • Test camera with OpenCV                                            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ PHASE 3: Link Raspberry Pi and ESP32 Together                          │
│   • Plug ESP32 into Raspberry Pi USB port (/dev/ttyUSB0)               │
│   • Run `python3 scripts/verify_system_ready.py` (Verify live handshake)│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ PHASE 4: Mount on Chassis & Run Autonomous Vehicle                     │
│   • Power up motor battery (7.4V (2S LiPo)) & Pi Power Bank (5V 3A)        │
│   • Run `python3 scripts/run_autonomous.py --use-yolo --use-pilotnet`  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ PHASE 5: Field Calibration & Track Tuning Playbook                     │
│   • Center Steering Servo Trim in firmware/esp32_firmware/esp32_config.h│
│   • Tune IPM Camera Trapezoid in config/rpi_tuning.py                  │
│   • Fine-tune Speed, PID & Lookahead Distance                          │
└────────────────────────────────────────────────────────────────────────┘
```

---

## **Phase 1: Setting up the ESP32 (via Laptop)**

The ESP32 manages all motor PWM, steering servo angles, ultrasonic sonars, and hardware safety. You configure and flash it directly from your laptop.

### **Step 1.1: Install Arduino IDE on your Laptop**
1. Download and install [Arduino IDE (v2.x)](https://www.arduino.cc/en/software).
2. Open Arduino IDE $\to$ Go to **File $\to$ Preferences**.
3. In *Additional Boards Manager URLs*, paste:
   ```text
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Go to **Tools $\to$ Board $\to$ Boards Manager**, search for **esp32** (by Espressif Systems), and click **Install**.

### **Step 1.2: Open and Flash the Firmware**
1. Connect the ESP32 to your laptop using a micro-USB or USB-C data cable.
2. In Arduino IDE, click **File $\to$ Open**, navigate to your cloned repository, and select:
   ```text
   firmware/esp32_firmware/esp32_vehicle_controller.ino
   ```
3. Go to **Tools $\to$ Board** and select **ESP32 Dev Module** (or your specific ESP32 board).
4. Go to **Tools $\to$ Port** and select the COM port (Windows: `COM3`, `COM4` / Linux: `/dev/ttyUSB0`).
5. Click the **Upload** button ($\rightarrow$).
   *(If the terminal says "Connecting...", hold down the physical **BOOT** button on the ESP32 board for 2 seconds until uploading begins).*

### **Step 1.3: Verify ESP32 is Working**
1. Open the **Serial Monitor** in Arduino IDE (top right magnifying glass).
2. Set the baud rate to **115200 baud**.
3. You should see 30 Hz live telemetry streaming continuously:
   ```text
   #TEL,2.00,2.00,2.00,0.20,0,0,0.0,0*
   #TEL,2.00,2.00,2.00,0.20,0,0,0.0,0*
   ```
   *Wave your hand in front of the ultrasonic sensors—you should see the distance numbers change in real time!*
4. Disconnect the ESP32 from your laptop. **Phase 1 is complete.**

---

## **Phase 2: Setting up the Raspberry Pi 5 (via Laptop)**

The Raspberry Pi runs the high-level brain: camera frame processing, YOLOv8 object detection, lane tracking, and behavioral decision planning.

### **Step 2.1: Flash the MicroSD Card**
1. Insert your MicroSD card (32GB or 64GB recommended) into your laptop.
2. Download and open [Raspberry Pi Imager](https://www.raspberrypi.com/software/).
3. Choose OS: **Raspberry Pi OS (64-bit)** (Debian Bookworm).
4. Choose Storage: Select your MicroSD card.
5. Click **Next**, then click **Edit Settings**:
   * Set hostname: `uamc-rover`
   * Set username and password: e.g. `pi` / `raspberry` (or your preferred credentials)
   * Check **Configure wireless LAN**: Enter your home/mobile hotspot Wi-Fi SSID and Password.
   * Go to the **Services** tab $\to$ Check **Enable SSH** (Use password authentication).
6. Click **Save** and **Write**. Once complete, eject the MicroSD card and insert it into the Raspberry Pi 5.

### **Step 2.2: Power Up & Connect via SSH**
1. Power the Raspberry Pi with a 5V 3A USB-C power supply or power bank.
2. Wait 60 seconds for it to boot and connect to your Wi-Fi.
3. On your laptop, open a terminal (PowerShell, Command Prompt, or bash) and connect:
   ```bash
   ssh rohith@10.94.129.58
   # (Enter the password you created in Step 2.1)
   ```
   *(If `uamc-rover.local` is not found, check your mobile hotspot or Wi-Fi router for the Pi's IP address, e.g., `ssh pi@192.168.1.105`).*

### **Step 2.3: Clone the Repository & Install Dependencies**
Run these exact commands in your SSH terminal:

```bash
# 1. Update system packages
sudo apt update && sudo apt install -y git python3-pip python3-opencv

# 2. Clone your vehicle repository
git clone https://github.com/Rohith45-ch/iitb.git
cd iitb

# 3. Install Python dependencies (ONNX Runtime, SciPy, PySerial)
pip install -r requirements.txt --break-system-packages
```

### **Step 2.4: Test the Camera**
1. Plug your USB camera (or CSI ribbon camera) into the Raspberry Pi.
2. Verify the device exists:
   ```bash
   ls -l /dev/video*
   ```
   *(You should see `/dev/video0`).*
3. Test a quick 5-second capture:
   ```bash
   python3 -c "import cv2; cap=cv2.VideoCapture(0); ret, frame=cap.read(); print('Camera Capture OK:', ret, frame.shape if ret else 'FAILED')"
   ```
   *Expected output: `Camera Capture OK: True (480, 640, 3)`.*

---

## **Phase 3: Interconnecting Raspberry Pi and ESP32**

Now you link both brains together.

### **Option A: USB Connection (Recommended)**
* Connect a short USB cable from the ESP32 directly into any of the **blue USB 3.0 ports** on the Raspberry Pi.
* Check that the Pi recognizes it:
  ```bash
  ls -l /dev/ttyUSB* /dev/ttyACM*
  ```
  *You will see `/dev/ttyUSB0` or `/dev/ttyACM0`.*

### **Option B: Direct GPIO UART Connection**
If you are wiring via pin headers instead of USB:
* Raspberry Pi **GPIO 14 (TXD)** $\longrightarrow$ ESP32 **GPIO 16 (RX2)**
* Raspberry Pi **GPIO 15 (RXD)** $\longleftarrow$ ESP32 **GPIO 17 (TX2)**
* Raspberry Pi **GND** $\longleftrightarrow$ ESP32 **GND**

---

## **Phase 4: Pre-Flight Verification & Running Autonomously**

### **Step 4.1: Run the Automated Pre-Flight Check**
Inside the Raspberry Pi SSH terminal, run:
```bash
cd ~/iitb
python3 scripts/verify_system_ready.py
```
This tests all 5 subsystems in 3 seconds:
```text
  [PASS] YOLOv8-Nano Object Detector
  [PASS] NVIDIA PilotNet Steering Model
  [PASS] YOLOv8n Forward Inference
  [PASS] Behavior FSM State Transition
  [PASS] Internal Serial Bridge (RPi <-> ESP32 Link)
  [PASS] ESP32 Firmware Artifacts
  ALL PRE-FLIGHT CHECKS PASSED!
```

### **Step 4.2: Start the Autonomous Vehicle**

Run the autonomous vehicle driving loop:

```bash
# 1. Full Autonomous Stack with YOLOv8 Object Detection:
python3 scripts/run_autonomous.py --serial-port /dev/ttyUSB0 --use-yolo

# 2. Or with End-to-End PilotNet Neural Steering:
python3 scripts/run_autonomous.py --serial-port /dev/ttyUSB0 --use-yolo --use-pilotnet

# 3. If running headless without an HDMI monitor:
python3 scripts/run_autonomous.py --serial-port /dev/ttyUSB0 --use-yolo --no-gui
```

---

## **Phase 5: Field Calibration & Tuning Playbook**

When your car is physically sitting on the track, you will tune specific behaviors. Because we separated the parameters into two dedicated files, tuning is quick and organized:

```
┌──────────────────────────────────────┐     ┌─────────────────────────────────────┐
│ FOR VISION, LIGHTS, AND SPEEDS       │     │ FOR SERVO TRIM & MOTOR POWER        │
│ Edit: config/rpi_tuning.py           │     │ Edit: firmware/esp32_firmware/      │
│ (No compile needed, edit & re-run)   │     │       esp32_config.h                │
└──────────────────────────────────────┘     └─────────────────────────────────────┘
```

### **Scenario A: Steering Servo Calibration (Straight Line Trim)**
* **Symptom**: You place the car on a straight line, but it slowly drifts to the left or right.
* **Fix**:
  1. Open [`firmware/esp32_firmware/esp32_config.h`](file:///home/rohith/iitb/firmware/esp32_firmware/esp32_config.h) on your laptop.
  2. Find line 33: `#define SERVO_MID_US 1500`.
  3. If drifting **left**: Increase `SERVO_MID_US` to `1520` or `1540`.
  4. If drifting **right**: Decrease `SERVO_MID_US` to `1480` or `1460`.
  5. Re-flash the ESP32.

### **Scenario B: Motor Starting Power (Deadband Tuning)**
* **Symptom**: Motor buzzes or whines when given low speed commands, but wheels don't turn until pushed.
* **Fix**:
  1. Open [`firmware/esp32_firmware/esp32_config.h`](file:///home/rohith/iitb/firmware/esp32_firmware/esp32_config.h).
  2. Increase `#define MOTOR_MIN_START_PWM 35` to `45` or `50` (to overcome initial gearbox static friction).

### **Scenario C: Camera Perspective (IPM Bird's-Eye View)**
* **Symptom**: Lane curvature looks distorted or lanes don't look parallel on straightaways.
* **Fix**:
  1. Run the interactive calibration tuner:
     ```bash
     python3 scripts/calibrate_camera.py --camera-id 0
     ```
  2. Note down the four corner points and paste them into `CameraConfig.src_trapezoid_fractions` in [`config/rpi_tuning.py`](file:///home/rohith/iitb/config/rpi_tuning.py).

### **Scenario D: Adjusting Cruise Speed & Stop Pause Time**
* **To change driving speeds**:
  Open [`config/rpi_tuning.py`](file:///home/rohith/iitb/config/rpi_tuning.py) $\to$ `BehaviorPlannerConfig`:
  * `v_cruise_ms = 0.45`: Change to `0.35` for slower, safer precision driving, or `0.60` for higher speed.
  * `stop_sign_hold_time_s = 3.0`: Change the stationary hold time at stop signs.

### **Scenario E: Adjusting Steering Responsiveness**
* **If car oscillates/wobbles side-to-side on straightaways**:
  * In [`config/rpi_tuning.py`](file:///home/rohith/iitb/config/rpi_tuning.py), increase `lookahead_min_m = 0.28` to `0.34`.
* **If car cuts sharp corners too late and leaves the lane**:
  * Decrease `lookahead_min_m = 0.28` to `0.23`.

---

## **Emergency Stop & Safety Checklist**

1. **Hardware Kill Switch**: Connected to ESP32 **GPIO 27** (Active LOW). Pressing it immediately disables motor drive and clamps dynamic braking.
2. **Software Watchdog**: If the Raspberry Pi freezes for $>150\text{ ms}$, the ESP32 hardware watchdog automatically halts the vehicle.
3. **TinyML Collision Guard**: If the vehicle impacts an obstacle ($>2.8\text{G}$) or rolls over ($>35^\circ$), the ESP32 halts the vehicle instantly on Core 0.
