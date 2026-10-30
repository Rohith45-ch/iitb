# START HERE — Hardware Integration & Setup Checklist
## Urban Autonomous Mobility Challenge (UAMC) — 1:10 Autonomous Vehicle

Follow this checklist the moment your **Raspberry Pi 4B** and **ESP32** arrive. 
You can run automated scripts in this repository to test each step.

---

## **Action Checklist (Follow in Order)**

```
[ ] Step 1: Plug ESP32 into Laptop -> Flash Firmware & Test
[ ] Step 2: Plug MicroSD Card into Laptop -> Flash Pi OS 64-bit (with Wi-Fi & SSH)
[ ] Step 3: Power up Raspberry Pi -> SSH into Pi from Laptop
[ ] Step 4: Clone Repo on Pi -> Run `pip install -r requirements.txt`
[ ] Step 5: Connect ESP32 to Pi with USB Cable -> Run `python3 scripts/detect_hardware.py`
[ ] Step 6: Run Pre-Flight Verification (`python3 scripts/verify_system_ready.py`)
[ ] Step 7: Launch Autonomous Vehicle (`python3 scripts/run_autonomous.py --use-yolo`)
```

---

## **Step 1: Setting up the ESP32 (Plug into Laptop)**

1. **Plug the ESP32 into your laptop USB port** using a micro-USB or USB-C data cable.
2. **Open Arduino IDE**:
   - In **File $\to$ Preferences**, ensure the ESP32 Board URL is added:
     `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
   - In **Tools $\to$ Board**, select **ESP32 Dev Module**.
   - In **Tools $\to$ Port**, select the port where your ESP32 appears (`COM3`, `COM4`, etc.).
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

## **Step 2: Preparing the Raspberry Pi 4B MicroSD Card**

1. Insert your MicroSD card (32GB / 64GB) into your laptop.
2. Open **Raspberry Pi Imager**:
   - Operating System: **Raspberry Pi OS (64-bit)** (Bookworm).
   - Storage: Select your MicroSD card.
3. Click **Next** $\to$ **Edit Settings**:
   - **Hostname**: `uamc-rover`
   - **User/Password**: (e.g. `pi` / `raspberry`)
   - **Wireless LAN**: Enter your Wi-Fi name & password.
   - **Services Tab**: Check **Enable SSH** (Password authentication).
4. Click **Write**. Once complete, eject the MicroSD card and insert it into the Raspberry Pi 4B.

---

## **Step 3: Booting the Raspberry Pi & Connecting via SSH**

1. Power the Raspberry Pi using a 5V 3A USB-C power bank or charger.
2. Wait 60 seconds for it to boot and connect to your Wi-Fi.
3. Open a terminal on your laptop (PowerShell, Command Prompt, or bash) and run:
   ```bash
   ssh pi@uamc-rover.local
   ```
   *(Password is whatever you set in Step 2, e.g. `raspberry`).*

---

## **Step 4: Installing the Autonomous Vehicle Stack on the Pi**

In the Pi's SSH terminal, copy and run these commands:

```bash
# 1. Update system packages
sudo apt update && sudo apt install -y git python3-pip python3-opencv

# 2. Clone the vehicle repository
git clone https://github.com/Rohith45-ch/iitb.git
cd iitb

# 3. Install AI & Robotics dependencies
pip install -r requirements.txt --break-system-packages
```

---

## **Step 5: Connecting the Hardware Together**

1. Plug the **USB Camera** into a USB port on the Raspberry Pi.
2. Plug the **ESP32** into any USB port on the Raspberry Pi using a short USB cable.
3. In your SSH terminal, run the diagnostic tool:
   ```bash
   python3 scripts/detect_hardware.py
   ```
   *It will automatically detect the camera resolution (640x480) and the ESP32 port (`/dev/ttyUSB0`), verify sensor telemetry, and print a green status report!*

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
