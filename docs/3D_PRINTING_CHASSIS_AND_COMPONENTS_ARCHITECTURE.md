# 🖨️ 3D-Printed Multi-Deck Chassis & Component Architecture Blueprint
### Urban Autonomous Mobility Challenge (UAMC) — Techfest, IIT Bombay
**Repository:** [Rohith45-ch/iitb](https://github.com/Rohith45-ch/iitb)  
**Document:** `docs/3D_PRINTING_CHASSIS_AND_COMPONENTS_ARCHITECTURE.md`  
**Date:** October 31, 2026  
**Hardware Revision:** Final Confirmed Hardware Inventory (9g Micro Servo + 2500–3000 mAh LiPo Powerbank + SmartElex RLS-06 + RPi Cam Rev 1.3 + 400-Point Breadboard)

---

## 📌 1. Executive Hardware Specification

This architecture document provides the exact mechanical dimensions, mounting patterns, tolerances, and multi-layer structural design required to 3D print the custom chassis decks and mounting brackets for the autonomous vehicle.

### 📋 Reconciled Component Inventory & Roles

| Component | Model / Specs | Placement | Function |
| :--- | :--- | :--- | :--- |
| **High-Level Compute** | Raspberry Pi 5 (85 × 56 mm) | Layer 2 (Top Deck) | IPM Lane detection, ONNX YOLO/PilotNet, FSM planner |
| **Vision Sensor** | Raspberry Pi Camera Rev 1.3 (OV5647 5MP) | Layer 3 (Elevated Mast) | 12–15 cm elevation, 15°–20° tilt for path & sign perception |
| **Low-Level Controller** | ESP32 DevKit V1 (30-pin) | Layer 1 (on Breadboard) | 50 Hz PWM actuator control, ultrasonic filtering, watchdog |
| **Ground Line Sensor** | SmartElex RLS-06 (6-IR Array) | Layer 0 (Under-Nose) | 5–10 mm ground clearance for millisecond lane recovery |
| **Steering Actuator** | Micro Servo 9g (SG90 / MG90S) | Layer 0 (Front Center) | Front wheel Ackermann steering linkage via 50 Hz PWM |
| **Propulsion & ESC** | RC Brushed/Brushless Motor + ESC | Layer 0 / Layer 1 | 50 Hz ESC throttle control (1000–2000 µs pulse) |
| **Brain Power Supply** | 2500–3000 mAh LiPo Power Bank (5V/3A) | Layer 1 (Mid Deck) | Dedicated isolated power for Raspberry Pi 5 |
| **Motor Power Supply** | 7.4V 2S LiPo / 7.2V NiMH Battery | Layer 0 (Chassis floor)| High-discharge power for ESC, motor, and servo BEC |
| **Proximity Sonar Array**| 3× or 4× HC-SR04 Ultrasonic Modules | Layer 2 Front Bumper | Left (+30°), Center (0°), Right (-30°), Flank (90°) |
| **Wiring & Power Rails** | 400 Tie-Point Solderless Breadboard | Layer 1 (Mid Deck) | ESP32 carrier, voltage dividers, sensor distribution |

> [!NOTE]
> **No ESP32-CAM is needed:** The autonomous vehicle's perception pipeline runs on the **Raspberry Pi 5** using the **Raspberry Pi Camera Rev 1.3**. The ESP32 DevKit V1 communicates with the Pi over a direct USB cable link.

> [!IMPORTANT]
> **Raspberry Pi 5 Camera Cable:** The Pi Camera Rev 1.3 has a 15-pin (1.0 mm pitch) ribbon cable. The Raspberry Pi 5 uses a smaller 22-pin (0.5 mm pitch) CSI connector. You must use a standard **15-pin to 22-pin Raspberry Pi 5 Camera Adapter Ribbon Cable**.

---

## 📐 2. Master CAD Dimensioning & Fastener Specification

Use the exact millimeter dimensions below for 3D modeling in Fusion 360, SolidWorks, Tinkercad, or Onshape. Hole diameters include standard FDM 3D printer shrinkage allowances (+0.2 mm to +0.3 mm):

| Component | Physical Dimensions (L × W × H) | Mounting Hole Pattern | Fastener Size | CAD Modeling Tolerance / Notes |
| :--- | :--- | :--- | :--- | :--- |
| **SmartElex RLS-06 (6-IR Array)** | 135.0 × 20.0 × 12.0 mm | 2 holes: **125.0 mm** apart | M3 screws + nuts | Ground clearance: **5.0 – 10.0 mm** from track surface. |
| **Micro Servo 9g (SG90 / MG90S)**| 23.0 × 12.2 × 29.0 mm (ear span: 32.5 mm) | 2 holes: **28.0 mm** center-to-center | M2 or M2.5 screws | Pocket cutout: **23.5 × 12.5 mm**, depth 18.0 mm. |
| **Raspberry Pi Cam Rev 1.3** | 25.0 × 24.0 × 9.0 mm (lens Ø 8.0 mm) | 4 holes: **21.0 × 12.5 mm** rectangle | M2 nylon screws | Lens hole: Ø 8.5 mm; ribbon slot: 17.0 × 2.0 mm. |
| **400-Point Breadboard** | 82.0 × 55.0 × 9.0 mm | Flat base (adhesive tape back) | Snap-fit border / lip | Recessed deck tray: **83.5 × 56.5 × 3.0 mm**. |
| **ESP32 DevKit V1 (30-pin)** | 52.0 × 28.5 × 13.0 mm | 2.54 mm header pitch (width 25.4 mm)| Plugs into breadboard | Straddles center channel of 400-pt breadboard. |
| **2500–3000 mAh LiPo Power Bank**| ~96.0 × 63.0 × 15.0 mm | Flat enclosure (no screw holes) | 2× 15 mm Velcro straps | Bay: **100.0 × 65.0 mm** with strap slots (18 × 3 mm). |
| **Raspberry Pi 5** | 85.0 × 56.0 × 17.0 mm (24 mm w/ Cooler) | 4 holes: **58.0 × 49.0 mm** rectangle | M2.5 × 10 mm standoffs | Hole diameter: **Ø 2.8 mm**. Leave SD slot accessible. |
| **HC-SR04 Ultrasonic Modules** | 45.0 × 20.0 × 15.0 mm (cylinders: Ø 16.0 mm)| Transducer center spacing: **26.0 mm**| Front friction fit / clip | Cut 2 barrel holes: **Ø 16.4 mm** spaced 26.0 mm apart. |
| **RC ESC** | ~42.0 × 34.0 × 21.0 mm | Flat base with heatsink top | Zip-ties or 3M VHB tape| Cut honeycomb ventilation under heatsink area. |
| **7.4V Motor LiPo Battery** | ~135.0 × 45.0 × 24.0 mm | Battery cradle | 20 mm Velcro cinch strap| Centerline bottom deck tray: **140.0 × 48.0 mm**. |

---

## 🏗️ 3. Multi-Deck Stacking Architecture

A 3-Deck sandwich structure keeps high-current motor power separated from sensitive compute and provides rigid, vibration-isolated sensor placement.

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
  │   (Optional Expansion: Left +30°, Right -30°, Right Flank for Round 2)          │
  │ • Raspberry Pi 5 (M2.5 standoffs, active cooler intake & MicroSD egress)        │
  └────────────────────────────────────────┬────────────────────────────────────────┘
                   ▲                       │ (4x M3 × 35mm Hex Standoffs)
                   │                       ▼
  ┌─────────────────────────────────────────────────────────────────────────────────┐
  │ LAYER 1: POWER & CONTROLLER DECK (Middle Plate)                                 │
  │ • 400-Point Breadboard with ESP32 DevKit V1 seated                              │
  │ • 2500–3000 mAh LiPo Power Bank (dedicated Raspberry Pi 5 power)                │
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

---

## 🔍 4. Layer-by-Layer CAD Modeling Guide

### 🏎️ Layer 0: Base Chassis Deck (Ground & Drive Layer)
1. **Under-Chassis SmartElex RLS-06 Mount:**
   * Design two drop-down lugs projecting downwards beneath the front nose.
   * Hole spacing: **125.0 mm** (M3 hardware).
   * Ensure that when the car wheels rest on the floor, the bottom face of the RLS-06 PCB sits exactly **6 mm to 8 mm above the ground**.
2. **Micro Servo 9g Steering Pocket:**
   * Position on vehicle centerline directly above or behind the front steering tie-rod axis.
   * Pocket dimensions: **23.5 mm length × 12.5 mm width × 18.0 mm depth**.
   * Flange ledge: 2.0 mm wide with two pilot holes of **Ø 2.2 mm** spaced **28.0 mm** apart.
   * Ensure the servo arm/horn moves ±28° with zero mechanical obstruction against chassis walls.
3. **Drive Battery Well:**
   * Centerline tray: **140 mm × 48 mm** with 4 mm raised perimeter lips and twin slots for a 20 mm Velcro strap.
4. **Deck Coupling:**
   * 4× M3 counterbored holes on the outer perimeter to bolt 30 mm standoffs connecting to Layer 1.

---

### ⚡ Layer 1: Power & Controller Deck (Middle Plate)
1. **400-Point Breadboard Tray:**
   * Recessed tray: **83.5 mm × 56.5 mm × 2.5 mm**.
   * Mount the breadboard with its adhesive back into this tray.
   * Seat the **ESP32 DevKit V1** straddling the breadboard's central trough. This leaves 2 terminal tie-points accessible on either side for jumper wires to sensors, servo, and ESC.
2. **Power Bank Tray (Pi 5 Power):**
   * Pocket: **100.0 mm × 65.0 mm × 3.0 mm** with two 18 × 3 mm strap slots.
   * Place toward the rear half of Layer 1 to balance the vehicle's forward weight.
   * Position the USB output port facing forward or sideways for a clean, short cable route to the Pi 5.
3. **ESC Bay:**
   * Raised 42 × 34 mm pad with a honeycomb cutout grid beneath it to let cool air reach the ESC heatsink.
4. **Wiring Feedthroughs:**
   * Four 15 × 8 mm oval slots to route servo, motor, battery, and IR sensor cables between Layer 0 and Layer 1.

---

### 🧠 Layer 2: Compute & Perception Deck (Top Plate)
1. **Raspberry Pi 5 Standoff Posts:**
   * 4× M2.5 holes arranged in a **58.0 mm × 49.0 mm** rectangle.
   * Use 10 mm brass or nylon M2.5 standoffs so the Active Cooler can pull ambient air smoothly.
   * Include a 20 × 10 mm slot directly beneath the MicroSD card slot and CSI camera connector.
2. **Integrated Front Bumper & Ultrasonic Sonar Pod:**
   * Extend the front edge into an impact-resistant curved bumper.
   * **Round 1 Required:** 1 Center HC-SR04 bracket at 0° (pointing straight ahead, GPIO 35).
   * **Optional expansion pods (Round 2 only):** Left (+30°), Right (-30°), and Right Flank (90°).
   * Standard bracket dimensions: Two cylinder holes of **Ø 16.4 mm** with **26.0 mm** center-to-center spacing.
3. **Flank Parking Sonar (Optional for Round 2):**
   * Reserved 1× HC-SR04 bracket facing 90° right to scan parking stalls if needed for advanced tasks.

---

### 📷 Layer 3: Camera Mast (Vision Tower)
1. **Tower Elevation:**
   * Riser height: **120 mm to 140 mm** above ground level.
   * Mounting geometry: An A-frame or twin triangular pylon to prevent camera vibration during driving.
2. **Pi Cam Rev 1.3 Bracket:**
   * Mounting face with 4× M2 holes spaced **21.0 mm × 12.5 mm**.
   * Central aperture: Ø 8.5 mm for the camera lens.
   * Downward pitch angle: Fixed or slotted for **15° to 20° downward tilt**.
   * *Field of View Result:* At 18° tilt from 13 cm height, the camera captures track markings starting 25 cm ahead of the bumper up to 2.0 meters into the distance, perfectly matching the IPM lane tracking parameters in `config/rpi_tuning.py`.

---

## 🔌 5. Electrical Wiring & Breadboard Interconnection Map

```
                     ┌──────────────────────────────────┐
                     │   2500–3000 mAh LiPo Powerbank   │
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
   ├── Pin 18 (PWM 50Hz) ──────► 9g Micro Servo (Signal)
   ├── Pin 19 (PWM 50Hz) ──────► ESC Throttle (Signal)
   ├── Pin 5  (Trigger)  ──────► HC-SR04 Sonar Trig (Shared)
   ├── Pin 34 (Echo Left) ◄───── HC-SR04 Left Echo (via 1k/2k Divider)
   ├── Pin 35 (Echo Center)◄──── HC-SR04 Center Echo (via 1k/2k Divider)
   ├── Pin 32 (Echo Right) ◄──── HC-SR04 Right Echo (via 1k/2k Divider)
   └── Pins 13, 14, 27, └───◄─── SmartElex RLS-06 (Digital Outs 1–6)
       21, 22, 23 (GPIO)
```

> [!TIP]
> **Power Isolation Best Practice:**
> * The **Raspberry Pi 5** is powered exclusively by the **2500–3000 mAh LiPo Power Bank**.
> * The **Drive Motor, ESC, and 9g Micro Servo** are powered by the **7.4V 2S LiPo Battery** (servo power comes from the ESC's 5V/6V BEC).
> * The **ESP32** is powered directly from the Raspberry Pi 5 via the USB data cable.
> * Connect all system grounds (**GND**) together on the 400-point breadboard negative rail.

---

## 🖨️ 6. 3D Print Manufacturing Slicing Profile

| Slicer Parameter | Value | Justification |
| :--- | :--- | :--- |
| **Recommended Filament** | **PETG** (or **PLA+**) | Heat resistance near ESC/motor (>70°C vs PLA's 55°C deformation), impact toughness. |
| **Layer Height** | **0.20 mm** | Accurate screw hole threads and clean fit for sensor pockets. |
| **Perimeter / Walls** | **4 to 5 walls (1.6 – 2.0 mm)** | **Critical:** Screws thread into printed walls. Thin walls will strip under vibration. |
| **Top / Bottom Solid Layers**| **4 Top / 4 Bottom** | Ensures decks remain flat and rigid under battery weight. |
| **Infill Density** | **35% – 45%** | Maximizes torsional stiffness to prevent steering flex. |
| **Infill Pattern** | **Gyroid** or **Cubic** | Uniform 3-axis strength without directional weak spots. |
| **Supports** | Tree / Organic Supports | Enable only for overhang angles > 55° (camera tilt slot & bumper curvature). |
| **Bed Adhesion** | Textured PEI sheet with Brim (5 mm) | Prevents corner warping on long deck plates. |

---

## 🚀 7. Assembly Sequence Checklist

1. **Step 1 — Base Chassis Assembly (Layer 0):**
   * Bolt the SmartElex RLS-06 array under the front nose using M3 screws and spacers (verify 6–8 mm ground clearance).
   * Install the 9g Micro Servo into the 23.5 × 12.5 mm pocket using M2 screws and connect the steering linkage to the front steering knuckles.
   * Secure the 7.4V motor battery in the centerline cradle with a Velcro strap.
   * Screw 4× M3 × 30 mm hex standoffs into the corner mounting points.

2. **Step 2 — Controller & Power Deck (Layer 1):**
   * Mount the Layer 1 plate onto the M3 standoffs.
   * Adhere the 400-point breadboard into its recessed tray and insert the ESP32 DevKit V1 across the central channel.
   * Fasten the ESC in its bay using zip-ties or 3M foam tape.
   * Strap the 2500–3000 mAh LiPo power bank into its bay.
   * Screw 4× M3 × 35 mm hex standoffs into the deck.

3. **Step 3 — Compute & Vision Deck (Layer 2 & 3):**
   * Press-fit the 3× HC-SR04 ultrasonic sensors into the front bumper pods.
   * Bolt the Raspberry Pi 5 onto the 10 mm M2.5 standoffs.
   * Attach the Camera Mast (Layer 3) to the front of Layer 2.
   * Secure the Raspberry Pi Camera Rev 1.3 to the mast using 4× M2 nylon screws at an 18° downward tilt.
   * Connect the 15-to-22 pin adapter ribbon cable between the Pi Cam and Pi 5 CSI port.

4. **Step 4 — Final Interconnect & Verification:**
   * Connect the ESP32 to the Raspberry Pi 5 using the USB cable.
   * Plug in the breadboard jumpers for servo (Pin 18), ESC (Pin 19), and sensors.
   * Power up the Pi 5 from the power bank and execute pre-flight diagnostics:
     ```bash
     python3 scripts/detect_hardware.py
     python3 scripts/verify_system_ready.py
     ```
