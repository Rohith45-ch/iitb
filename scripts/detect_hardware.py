#!/usr/bin/env python3
"""
Hardware Plug-and-Play Diagnostic & Verification Tool.
Run this script as soon as you plug the ESP32 and USB Camera into your laptop or Raspberry Pi.
Automatically scans USB ports, tests camera capture, and verifies live telemetry.
"""

import sys
import time
from pathlib import Path
import cv2

try:
    import serial
    import serial.tools.list_ports
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False


def print_banner():
    print("=" * 65)
    print("  UAMC IIT Bombay — Hardware Diagnostic & Connection Tool")
    print("  Scanning USB Ports, Cameras, and ESP32 Microcontroller...")
    print("=" * 65)


def scan_cameras():
    print("\n[1/3] Scanning for Connected Cameras...")
    found_cams = []
    # Test indices 0 to 4
    for idx in range(5):
        cap = cv2.VideoCapture(idx)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                h, w, c = frame.shape
                found_cams.append((idx, w, h))
                print(f"  \033[92m[FOUND]\033[0m Camera index {idx}: Resolution {w}x{h} (Active)")
            cap.release()

    if not found_cams:
        print("  \033[93m[WARNING]\033[0m No physical USB camera detected on /dev/video*.")
        print("            (Stack will run in synthetic simulation mode).")
    return found_cams


def scan_serial_ports():
    print("\n[2/3] Scanning USB Serial Ports for ESP32...")
    if not HAS_SERIAL:
        print("  \033[91m[ERROR]\033[0m 'pyserial' not installed. Run: pip install pyserial")
        return None

    usb_ports = [
        p for p in ports
        if "usb" in p.device.lower() or "acm" in p.device.lower() or "com" in p.device.lower()
    ]
    target_ports = usb_ports if usb_ports else ports

    if not usb_ports:
        print("  \033[93m[INFO]\033[0m No USB serial devices detected (/dev/ttyUSB* or /dev/ttyACM*).")
        print("         Make sure the ESP32 is plugged into a USB port with a data cable.")
        return None

    for p in usb_ports:
        desc = p.description or ""
        hwid = p.hwid or ""
        print(f"  Found Port: {p.device} | Description: {desc}")
        if any(chip in (desc + hwid).lower() for chip in ["cp210", "ch340", "ch341", "ftdi", "uart", "esp32", "usb"]):
            esp32_port = p.device
            print(f"  \033[92m[IDENTIFIED]\033[0m ESP32 Microcontroller on: {esp32_port}")

    if esp32_port is None and len(usb_ports) > 0:
        esp32_port = usb_ports[0].device
        print(f"  \033[94m[SELECTED]\033[0m Using USB port: {esp32_port}")

    return esp32_port


def test_esp32_telemetry(port: str):
    print(f"\n[3/3] Testing Live 115200 Baud Telemetry on {port}...")
    try:
        ser = serial.Serial(port, 115200, timeout=1.0)
        time.sleep(1.5)  # Allow ESP32 boot reset to settle

        # Read up to 20 lines to find a #TEL packet
        received_tel = False
        start_t = time.time()
        while time.time() - start_t < 3.0:
            if ser.in_waiting > 0:
                line = ser.readline().decode("ascii", errors="ignore").strip()
                if line.startswith("#TEL,") and line.endswith("*"):
                    print(f"  \033[92m[SUCCESS]\033[0m Live Telemetry Packet Received:")
                    print(f"    Raw: {line}")
                    parts = line[5:-1].split(",")
                    if len(parts) >= 8:
                        print(f"    Sonars: Left={parts[0]}m | Center={parts[1]}m | Right={parts[2]}m | Side={parts[3]}m")
                        print(f"    Encoders: Left={parts[4]} | Right={parts[5]} | E-Stop={parts[7]}")
                    received_tel = True
                    break

        # Send test ping command
        ser.write(b"#CMD,0.000,0.000,0*\n")
        ser.close()

        if not received_tel:
            print("  \033[93m[NOTE]\033[0m Connected to port, but no #TEL packet received within 3s.")
            print("         If ESP32 is new, flash firmware from: firmware/esp32_firmware/esp32_vehicle_controller.ino")
        return received_tel

    except Exception as e:
        print(f"  \033[91m[ERROR]\033[0m Failed to communicate on {port}: {e}")
        return False


def main():
    print_banner()
    cams = scan_cameras()
    esp_port = scan_serial_ports()

    if esp_port:
        test_esp32_telemetry(esp_port)

    print("\n" + "=" * 65)
    print("  SUMMARY:")
    print(f"  • Cameras Detected: {len(cams)}")
    print(f"  • ESP32 Port:       {esp_port if esp_port else 'Not Connected (or not yet flashed)'}")
    print("=" * 65)
    print("  Next Step: Follow START_HERE_HARDWARE_SETUP.md when you are ready!")


if __name__ == "__main__":
    main()
