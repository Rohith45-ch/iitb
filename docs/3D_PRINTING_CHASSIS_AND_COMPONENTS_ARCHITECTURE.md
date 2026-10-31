# 🖨️ 3D-Printed Multi-Deck Chassis & Component Architecture Blueprint
### Urban Autonomous Mobility Challenge (UAMC) — Techfest, IIT Bombay
**Repository:** [Rohith45-ch/iitb](https://github.com/Rohith45-ch/iitb)  
**Document File Path:** [`docs/3D_PRINTING_CHASSIS_AND_COMPONENTS_ARCHITECTURE.md`](file:///home/rohith/iitb/docs/3D_PRINTING_CHASSIS_AND_COMPONENTS_ARCHITECTURE.md)  
**Hardware Authority:** `Wiring_and_Pin_Map.pdf` (Repo: `Rohith45-ch/iitb`)  
**Revision:** 2.0 (Upgraded 170 mm Wheelbase · L298N + TT Motors · Dual Buck Converters · Micro Servo 9g · Single Center Sonar)  
**Date:** October 31, 2026  

---

> [!IMPORTANT]
> This blueprint contains the **complete mechanical engineering specifications**, exact millimeter CAD tolerances, fastener schedules, and layered architecture required to 3D print and assemble the vehicle chassis.
> All specs conform directly to the electrical and component reality defined in **`Wiring_and_Pin_Map.pdf`**.

---

## 📌 1. Executive Hardware Specification

### 📋 Reconciled Component Inventory & Placement

| Component | Physical Model / Specification | Deck Location | Role in Autonomous System |
| :--- | :--- | :--- | :--- |
| **High-Level SBC** | **Raspberry Pi 5 (8GB)** (85 × 56 mm) | **Layer 2** (Top Deck) | IPM Lane Tracking, YOLOv8/PilotNet AI, Behavior FSM Planner |
| **Vision Camera** | **Raspberry Pi Camera Rev 1.3** (OV5647 5MP) | **Layer 3** (Elevated Mast) | 120–150 mm elevation, 18° downward tilt, 15-to-22 pin CSI ribbon |
| **Low-Level MCU** | **ESP32 DevKit V1 (30-pin)** | **Layer 1** (Mid Deck) | 20 kHz motor PWM, 50 Hz servo PWM, sonar timing, 150ms watchdog |
| **Steering Actuator** | **Micro Servo 9g (SG90 / MG90S)** | **Layer 0** (Front Center) | Front Ackermann steering angle ($\pm 28^\circ$) via GPIO 18 |
| **Motor Driver** | **L298N Dual H-Bridge Module** | **Layer 1** (Mid Deck) | Drives both TT motors; PWM via GPIO 19, DIR via GPIO 22/23 |
| **Drive Motors** | **2× TT Gear Motors (3–9V rated)** | **Layer 0** (Rear Axle) | Direct rear wheel propulsion |
| **Drive Battery** | **3S LiPo 2200 mAh (11.1V / 12.6V)** | **Layer 0** (Center Floor) | High-current main power source (lowest center of gravity) |
| **Motor Regulator** | **7V Buck Converter (3A+)** | **Layer 1** (Mid Deck) | Drops 3S pack to 7V for L298N motor supply (`+12V VS`) |
| **Logic Regulator** | **5V Buck Converter (3A+)** | **Layer 1** (Mid Deck) | Powers Servo (+), HC-SR04 VCC, and L298N 5V logic |
| **Pi Power Bank** | **2500–3500 mAh LiPo Bank (5V/3A)** | **Layer 1** (Mid Deck Rear) | Dedicated isolated power via Pi 5 USB-C |
| **Obstacle Sonar** | **1× HC-SR04 Ultrasonic Sensor** | **Layer 2** (Front Bumper) | Front-center emergency braking pod (Trig: GPIO 5, Echo: GPIO 35) |
| **E-Stop Switch** | **22 mm Latching E-Stop (2 Contacts)** | **Layer 1/2** (Top Flange) | NC contact in battery line; NO contact to ESP32 GPIO 27 |
| **Inline Fuse** | **10A Inline Fuse + Holder** | **Layer 0/1** (Power Bay) | Battery positive lead short-circuit protection |
| **Prototyping Deck** | **400-Point Solderless Breadboard** | **Layer 1** (Mid Deck) | ESP32 carrier, common GND rail, 1k/2k echo divider, servo cap |
| **Ground Line Sensor**| **SmartElex RLS-06 (6-IR Array)** | **Layer 0** (Under-Nose) | Optional ground recovery sensor (camera handles main lane tracking) |

---

## 📐 2. Master CAD Dimensioning & Fastener Schedule

Every dimension includes standard FDM 3D printing tolerances (+0.2 mm to +0.3 mm on inner diameters to ensure effortless fastener clearance and drop-in fit):

| Component | Physical Dimensions (L × W × H) | Mounting Pattern / Center-to-Center | Fastener Hardware | CAD Modeling Feature / Pocket Tolerances |
| :--- | :--- | :--- | :--- | :--- |
| **Chassis Wheelbase ($L$)** | **170.0 mm** (Axle to Axle) | Front axle $y = 0$, Rear axle $y = 170.0\text{ mm}$ | M3 / M4 axles | Rigid perimeter rails; Ackermann geometry centered. |
| **Chassis Track Width ($W$)** | **135.0 – 145.0 mm** | Wheel hex-to-hex spacing | M4 locknuts | Allows full $\pm 28^\circ$ steering sweep without tire rub. |
| **Micro Servo 9g (SG90/MG90S)**| 23.0 × 12.2 × 29.0 mm (ear span: 32.5 mm) | 2 holes: **28.0 mm** center-to-center | 2× M2 or M2.5 screws | Pocket cutout: **23.5 × 12.5 mm**, depth **18.0 mm**. |
| **2× TT Gear Motors** | 70.0 × 22.0 × 19.0 mm each | 2 transverse bolt holes: **Ø 3.2 mm** | 2× M3 × 30 mm cross-bolts | Dual clamp saddle: **22.5 × 19.5 mm** pocket per motor. |
| **3S LiPo 2200 mAh Battery** | ~107.0 × 35.0 × 25.0 mm | Flat base, centerline floor cradle | 20 mm Velcro cinch strap | Tray: **112.0 × 38.0 × 12.0 mm** with dual strap slots (22 × 3 mm). |
| **L298N Motor Driver** | 43.5 × 43.5 × 26.0 mm (with heatsink) | 4 holes: **37.5 × 37.5 mm** square pattern | 4× M3 × 8 mm standoffs | Clearance under board for solder tails; heatsink airflow slot. |
| **7V Buck Converter (Motor)** | ~65.0 × 36.0 × 15.0 mm (XL4015/LM2596) | 2 or 4 diagonal holes: **Ø 3.2 mm** | M3 screws or zip-ties | Tray: **68.0 × 38.0 mm**; potentiometer screw accessible. |
| **5V Buck Converter (Logic)** | ~65.0 × 36.0 × 15.0 mm (XL4015/LM2596) | 2 or 4 diagonal holes: **Ø 3.2 mm** | M3 screws or zip-ties | Tray: **68.0 × 38.0 mm**; potentiometer screw accessible. |
| **400-Point Breadboard** | 82.0 × 55.0 × 9.0 mm | Adhesive back foam pad | Recessed snap-lip | Tray: **83.5 × 56.5 × 3.0 mm** recessed well. |
| **ESP32 DevKit V1 (30-pin)** | 52.0 × 28.5 × 13.0 mm | 2.54 mm pitch (25.4 mm pin row span)| Press-fit into breadboard | Straddles center divider of breadboard; leave 2 rows free each side. |
| **Raspberry Pi 5 (8GB)** | 85.0 × 56.0 × 17.0 mm (24 mm w/ cooler) | 4 holes: **58.0 × 49.0 mm** rectangle | 4× M2.5 × 10 mm standoffs | Hole diameter: **Ø 2.8 mm**; bottom cutaway for MicroSD access. |
| **Raspberry Pi Camera Rev 1.3** | 25.0 × 24.0 × 9.0 mm (lens Ø 8.0 mm) | 4 holes: **21.0 × 12.5 mm** rectangle | 4× M2 nylon screws | Lens aperture: **Ø 9.0 mm**; bottom ribbon slot: **17.0 × 2.5 mm**. |
| **HC-SR04 Ultrasonic Module** | 45.0 × 20.0 × 15.0 mm (cylinders: Ø 16.0 mm)| Dual cylinder center spacing: **26.0 mm**| Front friction snap-fit | 2 barrel holes: **Ø 16.4 mm** spaced 26.0 mm on center. |
| **22 mm Latching E-Stop Switch**| Ø 22.0 mm threaded body, Ø 30 mm bezel | Single panel hole | Threaded locking ring | Flange hole: **Ø 22.5 mm**; prominent top-deck position. |
| **2500–3500 mAh LiPo Power Bank**| ~96.0 × 65.0 × 16.0 mm | Flat rectangular pack | 2× 15 mm Velcro cinch straps| Bay: **100.0 × 68.0 × 10.0 mm** with side strap slots (18 × 3 mm). |
| **SmartElex RLS-06 (Optional)** | 135.0 × 20.0 × 12.0 mm | 2 mounting holes: **125.0 mm** apart | 2× M3 screws + spacers | Under-nose bracket: **6.0 – 8.0 mm** track clearance. |

---

## 🏗️ 3. Multi-Deck Sandwich Architecture

The vehicle is partitioned into **4 vertical structural tiers** connected by M3 hexagonal standoffs. This mechanical separation eliminates electromagnetic interference (EMI) from the motors and keeps the center of gravity as low as possible:

```
===================================================================================
                       LAYER 3: VISION MAST (Height: 120–150 mm)
  [ Pi Camera Rev 1.3 ] (18° downward tilt, forward line of sight)
         │ 15-to-22 pin CSI ribbon cable
===================================================================================
                       LAYER 2: COMPUTE & SENSOR DECK (Top Plate)
  • Front Bumper: 1× HC-SR04 Ultrasonic Sonar Pod (Center 0°, GPIO 35 via divider)
  • Center Bay:   Raspberry Pi 5 (8GB) with Active Cooler (M2.5 standoffs)
  • Top Flange:   22 mm Latching E-Stop Kill Switch Button (High-visibility)
===================================================================================
                       LAYER 1: CONTROLLER & POWER REGULATION DECK
  • 400-Point Breadboard (Carries ESP32 DevKit V1 + Voltage Divider + 1000µF Cap)
  • L298N Dual H-Bridge Motor Driver Module (M3 standoffs, heatsink exposed)
  • 7V Buck Converter (Motor Rail) & 5V Buck Converter (Logic & Servo Rail)
  • 2500–3500 mAh LiPo Power Bank Cradle (Pi 5 Dedicated Power)
===================================================================================
                       LAYER 0: STRUCTURAL BASE CHASSIS (Bottom Floor)
  • Wheelbase: Exactly 170.0 mm (Axle to Axle)
  • Front Axle: Ackermann Steering Knuckles + Micro Servo 9g Pocket (23.5 × 12.5 mm)
  • Center Bay: 3S LiPo 2200 mAh Battery Cradle (Lowest vehicle center of gravity)
  • Rear Axle:  Dual TT Gear Motors (3–9V) clamped in transverse saddles
  • Under-Nose: SmartElex RLS-06 6-IR Ground Line Array (Optional add-on)
===================================================================================
```

---

## 🔍 4. Detailed Layer-by-Layer CAD Modeling Guide

### 🚗 Layer 0: Structural Base Chassis
1. **Perimeter Dimensions:**
   - Length: **240.0 mm**, Width: **110.0 mm**, Floor Plate Thickness: **3.5 mm**.
   - Front and rear axle center-to-center distance: **170.0 mm $\pm 0.5\text{ mm}$**.
2. **Micro Servo 9g Steering Pocket:**
   - Position: Centerline at $y = 15.0\text{ mm}$ (directly between front wheels).
   - Recess dimensions: **23.5 mm (W) × 12.5 mm (L) × 18.0 mm (D)**.
   - Flange ears: 2× Ø 2.2 mm pilot holes spaced **28.0 mm** apart for M2 mounting screws.
   - Servo horn must rotate freely $\pm 28^\circ$ without binding against side bulkheads.
3. **TT Gear Motor Clamps:**
   - Position: Rear axle line at $y = 185.0\text{ mm}$.
   - Dual mirror-symmetric saddles holding the 22.0 × 19.0 mm motor bodies.
   - Dual M3 through-bolt channels (spacing **30.0 mm**) to clamp each motor firmly against torque reaction.
4. **3S LiPo Battery Tray:**
   - Position: Centerline at $y = 70.0\text{ mm}$ to $y = 150.0\text{ mm}$.
   - Internal well dimensions: **112.0 mm × 38.0 mm × 10.0 mm wall height**.
   - Include 4 slots (**22.0 × 3.0 mm**) for standard 20 mm Velcro cinch straps.
5. **Deck Standoff Bosses:**
   - 6× M3 mounting bosses (Ø 7.0 mm outer, Ø 3.2 mm inner hole) located along perimeter rails to support Layer 1.

---

### ⚡ Layer 1: Controller & Power Deck (Mid Plate)
1. **Breadboard Well:**
   - Recessed tray: **83.5 mm × 56.5 mm × 2.5 mm depth**.
   - Mount 400-point breadboard using its adhesive backing.
   - ESP32 DevKit V1 plugs into breadboard straddling the center divider groove.
2. **L298N Motor Driver Mounting:**
   - Footprint: **44.0 × 44.0 mm** area.
   - 4× M3 standoff holes on a **37.5 × 37.5 mm** square grid.
   - Provide a **20 × 20 mm central cutout** beneath the board for terminal soldering pin relief and convection cooling.
3. **Dual Buck Converter Trays (7V and 5V):**
   - Side-by-side cradles: each **68.0 × 38.0 mm**.
   - M3 mounting holes or cable-tie anchor channels.
   - Leave clearance around multiturn trim pots so output voltages can be adjusted with a screwdriver while mounted.
4. **Power Bank Tray:**
   - Flat cradle: **100.0 × 68.0 mm** with raised 3.0 mm lips and 2× strap slots for the Pi 5 power bank.
5. **E-Stop Panel Flange:**
   - Raised rear/side boss with a **Ø 22.5 mm** clearance hole for the 22 mm latching emergency kill button.

---

### 🧠 Layer 2: Compute & Sensor Deck (Top Plate)
1. **Raspberry Pi 5 Standoff Posts:**
   - 4× raised cylindrical posts (height 6.0 mm, outer Ø 6.0 mm).
   - Hole pattern: **58.0 mm × 49.0 mm** rectangle with **Ø 2.8 mm** holes for M2.5 brass standoffs.
   - Provide a **30.0 × 15.0 mm rectangular cutaway** underneath the MicroSD card slot for easy card insertion/removal without removing the board.
2. **Front Bumper & Ultrasonic Pod:**
   - Integrated forward curved bumper extending 25 mm ahead of front wheels.
   - Two cylindrical bores: **Ø 16.4 mm**, center-to-center distance **26.0 mm**, wall thickness 2.0 mm.
   - Rear access pocket allowing the 4-pin right-angle header of the HC-SR04 to plug in cleanly.

---

### 📷 Layer 3: Vision Mast & Camera Bracket
1. **Mast Structure:**
   - Rigid A-frame or hollow rectangular tower (height **130.0 mm**, base width **45.0 mm**).
   - Central internal channel (**20.0 × 4.0 mm**) to route the delicate CSI ribbon cable safely away from tire spray.
2. **Pi Camera Rev 1.3 Faceplate:**
   - Dimensions: **30.0 × 30.0 mm** angled faceplate with fixed **18.0° downward tilt**.
   - 4× M2 screw holes on a **21.0 × 12.5 mm** grid.
   - Center lens aperture: **Ø 9.0 mm**.
   - Bottom slot (**18.0 × 2.5 mm**) for 15-pin ribbon exit.

---

## 🔌 5. Master Wiring & Electrical Interconnect Schematic

```
                         ┌────────────────────────────────────────┐
                         │   2500–3500 mAh LiPo Power Bank        │
                         └───────────────────┬────────────────────┘
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
          ├── GPIO 18 (PWM 50Hz) ──────► Micro Servo 9g (Signal)
          ├── GPIO 19 (PWM 20kHz) ─────► L298N ENA + ENB (Speed)
          ├── GPIO 22 (Digital Out) ───► L298N IN1 + IN3 (Dir A)
          ├── GPIO 23 (Digital Out) ───► L298N IN2 + IN4 (Dir B)
          ├── GPIO 5  (Trigger)  ──────► HC-SR04 Center Sonar Trig
          ├── GPIO 35 (Echo Center)◄─── HC-SR04 Center Sonar Echo (via 1k/2k Divider)
          └── GPIO 27 (Input Pullup)◄── Hardware E-Stop Switch (Active-LOW)

┌────────────────────────────────────────────────────────────────────────┐
│                      3S LiPo 2200 mAh (11.1V / 12.6V)                  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (+) Positive Wire
                                    ▼
                      [ E-Stop Switch NC Contact ]
                                    │
                                    ▼
                         [ 10A Inline Fuse ]
                                    │
               ┌────────────────────┴────────────────────┐
               │                                         │
               ▼                                         ▼
       [ 7V Buck Converter ]                     [ 5V Buck Converter ]
       (Adjusted to 7.00V)                       (Adjusted to 5.00V)
               │                                         │
               ▼                                         ├──► Micro Servo 9g (+) [+ 1000µF Cap]
       L298N +12V (VS) Terminal                          ├──► HC-SR04 VCC (5V)
               │                                         └──► L298N +5V Logic [Jumper Removed]
               ▼
     [ Left & Right TT Motors ]

ALL GROUNDS (ESP32 GND, L298N GND, Buck GNDs, Servo GND, Sonar GND) ──► Common Ground Rail
```

---

## 🖨️ 6. 3D Print Manufacturing Slicing Profile

| Slicer Parameter | Recommended Value | Engineering Justification |
| :--- | :--- | :--- |
| **Material / Filament** | **PETG** (or **PLA+**) | Heat resistance near motors (>75°C vs PLA's 55°C deformation) and high layer impact toughness. |
| **Layer Height** | **0.20 mm** (0.28 mm for draft) | Smooth surface finish for screw threads and tight tolerance on sensor pockets. |
| **Perimeter Walls** | **4 to 5 walls (1.6 – 2.0 mm)** | **Critical:** Screws thread directly into 3D-printed plastic walls; 2 walls will strip immediately. |
| **Top & Bottom Layers** | **4 Top / 4 Bottom** | Prevents deck flexing under battery and motor clamping loads. |
| **Infill Density** | **35% – 45%** | Maximizes torsional stiffness to ensure accurate steering geometry. |
| **Infill Pattern** | **Gyroid** or **Cubic** | Uniform 3-dimensional stress resistance without directional failure planes. |
| **Supports** | Tree / Organic Supports | Enable only for overhang angles > 55° (camera tilt bracket and bumper curvature). |
| **Print Bed Adhesion** | Textured PEI sheet with 5 mm Brim | Prevents corner lifting / warping on the long 240 mm chassis baseplate. |

---

## 🚀 7. Step-by-Step Mechanical Assembly Sequence

### Phase 1: Base Chassis Build (Layer 0)
1. **Fit Steering Servo:** Press the Micro Servo 9g into the 23.5 × 12.5 mm pocket. Secure with 2× M2 screws. Attach the servo horn at 90° (neutral trim). Connect steering tie-rods to front knuckles.
2. **Mount TT Motors:** Insert the two TT gear motors into the rear axle saddles. Insert 2× M3 × 30 mm cross-bolts per motor and tighten nylon locknuts. Press rear drive wheels onto motor double-flat axles.
3. **Install Drive Battery:** Place the 3S LiPo 2200 mAh into the central cradle. Cinch securely with a 20 mm Velcro strap.
4. **Install Standoffs:** Thread 6× M3 × 30 mm female-female hex standoffs into the perimeter bosses.

### Phase 2: Power & Controller Deck Assembly (Layer 1)
1. **Install Mid Plate:** Place the Layer 1 plate over the standoffs and secure with M3 countersunk screws.
2. **Mount Breadboard & ESP32:** Peel the adhesive backing off the 400-point breadboard and press it into the recessed tray. Seat the ESP32 DevKit V1 straddling the center channel.
3. **Mount L298N & Bucks:** Fasten the L298N module using 4× M3 × 8 mm standoffs. Fasten both buck converters into their trays using zip-ties or M3 screws.
4. **Wire Power & E-Stop:** Install the 22 mm E-Stop button in the flange hole. Wire the NC contact in series with the battery (+) line and 10A fuse; wire the NO contact to ESP32 GPIO 27.
5. **Adjust Buck Voltages:** Connect battery and use a multimeter to adjust the 7V buck to **7.00V** and the 5V buck to **5.00V** before making connections to components.
6. **Install Upper Standoffs:** Thread 4× M3 × 35 mm hex standoffs into the Layer 1 top bosses.

### Phase 3: Compute & Vision Deck Assembly (Layer 2 & 3)
1. **Mount Ultrasonic Sensor:** Push the HC-SR04 barrels into the front bumper holes until seated flush. Wire TRIG to ESP32 GPIO 5 and ECHO through the 1kΩ/2kΩ divider to GPIO 35.
2. **Mount Raspberry Pi 5:** Bolt the Pi 5 to the 4× M2.5 standoffs. Ensure the Active Cooler is mounted and the MicroSD card is accessible.
3. **Assemble Camera Mast:** Bolt the Layer 3 camera mast to the front of Layer 2. Fasten the Pi Camera Rev 1.3 to the 18° tilted faceplate using 4× M2 nylon screws.
4. **Route Camera Ribbon:** Route the 15-to-22 pin CSI adapter cable down through the mast channel and connect it to Pi 5 port `CAM1`.

### Phase 4: Final Interconnect & Verification
1. **Connect Data Link:** Plug a short USB-A to Micro-USB cable between a Pi 5 USB-A port and the ESP32 Micro-USB port.
2. **Connect Actuator Jumpers:** Wire GPIO 18 to Servo Signal; GPIO 19 to L298N ENA+ENB; GPIO 22 to IN1+IN3; GPIO 23 to IN2+IN4.
3. **Common Ground Verification:** Confirm with a continuity meter that ESP32 GND, L298N GND, battery (−), and buck GNDs are all connected.
4. **Execute Pre-Flight Diagnostic:**
   ```bash
   ssh rohith@10.94.129.58
   cd ~/iitb && git pull origin main
   python3 scripts/detect_hardware.py
   python3 scripts/verify_system_ready.py
   ```
