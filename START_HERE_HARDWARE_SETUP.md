# START HERE — Hardware Integration & Setup Checklist
## Urban Autonomous Mobility Challenge (UAMC) — 1:10 Autonomous Vehicle

Follow this checklist for your **Raspberry Pi 5** and **ESP32** hardware setup. 
You can run automated scripts in this repository to test each step.

---

## **Action Checklist (Follow in Order)**

```
[ ] Step 1: Plug ESP32 into Laptop -> Flash Firmware & Test
[ ] Step 2: Plug MicroSD Card into Laptop -> Flash Pi OS 64-bit (with Wi-Fi & SSH) [DONE]
[ ] Step 3: Power up Raspberry Pi 5 -> SSH into Pi from Laptop (rohith@10.94.129.58) [DONE]
[ ] Step 4: Clone Repo on Pi -> Run `pip install -r requirements.txt` [DONE]
[ ] Step 5: Connect ESP32 to Pi with USB Cable -> Run `python3 scripts/detect_hardware.py`
[ ] Step 6: Run Pre-Flight Verification (`python3 scripts/verify_system_ready.py`) [DONE]
[ ] Step 7: Launch Autonomous Vehicle (`python3 scripts/run_autonomous.py --use-yolo`)
```

---

## **Step 1: Setting up the ESP32 (Plug into Laptop)**

1. **Plug the ESP32 into your laptop USB port** using a micro-USB or USB-C data cable.
2. **Open Arduino IDE**:
   - In **File $\to$ Preferences**, ensure the ESP32 Board URL is added:
     `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
   - In **Tools $\to$ Board**, select **ESP32 Dev Module**.
   - In **Tools $\to$ Port**, select the port where your ESP32 appears (`COM3`, `COM4`, `/dev/ttyUSB0`, etc.).
3. **Open the Firmware**:
   - In Arduino IDE, open:
     `firmware/esp32_firmware/esp32_vehicle_controller.ino`
4. **Click Upload ($\rightarrow$)**:
   - *(If the terminal says "Connecting...", hold down the physical **BOOT** button on the ESP32 for 2 seconds until uploading begins).*
5. **Verify Live Output**:
   - Open **Serial Monitor** at **115200 baud**.
   - You should see continuous 30 Hz telemetry:
     `#TEL,2.00,2.00,2.00,0.20,0,0,0.0,0*`
   - Unplug the ESP32 from your laptop. *(ESP32 is 100% ready).*

---

## **Step 2: Preparing the Raspberry Pi 5 MicroSD Card**

*(Already completed!)*
* OS: **Raspberry Pi OS (64-bit)**
* Username: `rohith`
* Hostname: `raspberrypi`

---

## **Step 3: Booting the Raspberry Pi 5 & Connecting via SSH**

1. Power the Raspberry Pi 5 using a 5V 3A LiPo power bank or USB-C supply.
2. The Pi automatically associates with the mobile hotspot (`Heisenberg`).
3. Connect directly via SSH from your laptop:
   ```bash
   ssh rohith@10.94.129.58
   ```

---

## **Step 4: Installing the Autonomous Vehicle Stack on the Pi**

*(Already completed! Cloned to `~/iitb` on the Pi and pre-flight tested).*

---

## **Step 5: Connecting the Hardware Together**

1. **Camera:** Attach the Raspberry Pi Camera Rev 1.3 to Pi 5 port `CAM1` using the 22-pin to 15-pin adapter ribbon cable.
2. **ESP32:** Plug the ESP32 into any USB port on the Raspberry Pi 5 using a USB cable.
3. **Actuators, Motor Driver & Single Ultrasonic Sensor:**
   - **Steering Servo (SG90/MG90S):** ESP32 `GPIO 18` (Signal) — 50 Hz, 1000–2000 µs
   - **L298N ENA + ENB:** ESP32 `GPIO 19` (20 kHz PWM speed — jumpers removed from L298N)
   - **L298N IN1 + IN3:** ESP32 `GPIO 22` (motor direction A)
   - **L298N IN2 + IN4:** ESP32 `GPIO 23` (motor direction B)
   - **L298N +12V(VS):** 7V buck converter output (set with meter before connecting)
   - **L298N +5V logic:** 5V buck converter output (remove 5V jumper from L298N board)
   - **Left TT motor:** L298N OUT1 / OUT2
   - **Right TT motor:** L298N OUT3 / OUT4
   - **HC-SR04 TRIG:** `GPIO 5` | **HC-SR04 ECHO:** `GPIO 35` via 1kΩ/2kΩ voltage divider
   - **Servo (+):** 5V buck (+) with 470–1000 µF capacitor across the rail
   - **E-stop NC contact:** In series with 3S LiPo battery (+) before the 10A fuse
   - **E-stop NO contact:** `GPIO 27` to GND, 10kΩ pull-up from GPIO 27 to 3.3V
4. In your Pi 5 SSH terminal, run the diagnostic tool:
   ```bash
   python3 scripts/detect_hardware.py
   ```
   *It will automatically detect the camera, ESP32 USB port (`/dev/ttyUSB0`), and sensor telemetry!*

---

## **Step 6: Running the Pre-Flight Verification**

Run the end-to-end integration test:

```bash
python3 scripts/verify_system_ready.py
```

*Expected output:*
```text
  [PASS] YOLOv8-Nano Object Detector
  [PASS] NVIDIA PilotNet Steering Model
  [PASS] YOLOv8n Forward Inference
  [PASS] Behavior FSM State Transition
  [PASS] Internal Serial Bridge (RPi <-> ESP32 Link)
  [PASS] ESP32 Firmware Artifacts
  ALL PRE-FLIGHT CHECKS PASSED!
```

---

## **Step 7: Launching Autonomous Driving**

Place the vehicle on the track, power on the motor battery, and launch the vehicle software:

```bash
# Launch with YOLOv8 object detection in headless mode:
python3 scripts/run_autonomous.py --serial-port /dev/ttyUSB0 --use-yolo --no-gui
```

---

## **Quick Tuning & Calibration Cheatsheet**

* **If the car pulls slightly left/right on straightaways**:
  Open [`firmware/esp32_firmware/esp32_config.h`](file:///home/rohith/iitb/firmware/esp32_firmware/esp32_config.h), adjust `SERVO_MID_US` (default `1500`) by $\pm 20$–$50\mu s$, and re-flash.
* **If the motor buzzes or needs a push to start**:
  Open [`firmware/esp32_firmware/esp32_config.h`](file:///home/rohith/iitb/firmware/esp32_firmware/esp32_config.h), increase `MOTOR_MIN_START_PWM` from `35` to `45`.
* **If you want to change vehicle speed**:
  Open [`config/rpi_tuning.py`](file:///home/rohith/iitb/config/rpi_tuning.py), edit `v_cruise_ms = 0.45` (set to `0.35` for slower, precision driving).
* **Detailed Troubleshooting Guide**:
  Read [`docs/DEVICE_TUNING_BLOCKS.md`](file:///home/rohith/iitb/docs/DEVICE_TUNING_BLOCKS.md).
