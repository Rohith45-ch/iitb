# Round 1 Qualification Action Plan & Video Guide

## Objective
To successfully qualify in the **Top 25 Teams** invited to IIT Bombay for the On-Site rounds of the Urban Autonomous Mobility Challenge (UAMC).

- **Submission Deadline**: November 10th
- **Core Deliverables**:
  1. **Video Demonstration (3–5 minutes)** showing autonomous lane-following and controlled obstacle stopping on a self-built practice track with zero visible remote control.
  2. **Technical Design Document (TDD)**: Completed and provided in `docs/TECHNICAL_DESIGN_DOCUMENT.md`.

---

## 1. Practice Track Construction Guide (Low-Cost)

The competition requires demonstrating basic autonomous capability on a home or lab-built practice track. You can construct a compliant test track in under 2 hours:

### Materials Needed:
1. **White Tape / Masking Tape (2-inch width)**: For road boundary lines.
2. **Yellow Tape (1-inch or 2-inch width)**: For the center dotted or solid dividing line.
3. **Black Floor / Cardboard / Matting (or regular flat floor)**: Good contrast against white/yellow tape.
4. **Cardboard Box / Traffic Cone**: For the static obstacle.
5. **Red Octagonal Cutout**: For the Stop sign.

### Track Dimensions & Layout:
- **Track Length**: At least 3–5 meters long.
- **Lane Width**: $35\text{ cm}$ (or $30\text{--}40\text{ cm}$ standard).
- **Curvature**: Include at least one straight segment ($2\text{ m}$) transitioning into a 90° curve ($R \approx 50\text{--}60\text{ cm}$) to prove turning capability.
- **Obstacle Placement**: Place a static box ($15\text{ cm} \times 15\text{ cm}$) in the car's lane near the end of a straight segment.

```
       | <--- 35 cm ---> | <--- 35 cm ---> |
       |                 |                 |
(White |   Vehicle Lane  |  Opposite Lane  | (White
 Line) |                 : (Yellow Line)   |  Line)
       |                 |                 |
       |       [CAR]     |                 |
       |         |       :                 |
       |         v       |                 |
       |     [OBSTACLE]  |                 |
```

---

## 2. 3–5 Minute Video Script & Storyboard

The video must prove that the vehicle is operating autonomously and reliably. Use the following structured script:

### Segment 1: Vehicle & Architecture Introduction (0:00 – 1:00)
- Close-up shots of the vehicle chassis, compute board (Raspberry Pi / Jetson), microcontroller, camera, and ultrasonic sensors.
- Highlight the **Emergency Stop (E-Stop)** button: show how pressing it instantly cuts motor power.
- Brief voiceover/subtitles: *"AML-Rover-V1, featuring modular perception, Pure Pursuit steering control, and hardware-isolated safety watchdog."*

### Segment 2: Practice Track Autonomous Run (1:00 – 2:30)
- **Wide Angle Static Camera Shot**: Place a tripod capturing the entire track and the team standing with hands visibly empty or raised (proving zero remote control / teleoperation).
- **Run 1: Autonomous Lane Following**:
  - Vehicle starts autonomously, follows the lane centerline smoothly without touching boundary lines, navigates the curve, and stops at the finish.
- **Picture-in-Picture (PiP)**: In the corner of the video, overlay the real-time camera view showing the detected lane polynomials and steering vector! (Our software stack generates this video overlay automatically).

### Segment 3: Obstacle Detection & Controlled Stop (2:30 – 3:30)
- **Run 2: Controlled Obstacle Halt**:
  - Vehicle drives down the lane at cruising speed ($0.45\text{ m/s}$).
  - An obstacle is placed in the lane ahead.
  - Show the vehicle smoothly decelerating and halting stably $15\text{--}25\text{ cm}$ before the obstacle without collision.
  - PiP shows the ultrasonic/vision sensor trigger activating the brake state.

### Segment 4: Engineering Rigor & Code Walkthrough (3:30 – 4:30)
- Screen recording of the terminal running `python3 scripts/run_autonomous.py`.
- Quick display of the behavior state machine transitions (`LANE_FOLLOWING -> OBSTACLE_DETECTED -> CONTROLLED_STOP`).
- Show the safety watchdog test: disconnecting communication brings the vehicle to an instant halt.

### Segment 5: Outro & Team Details (4:30 – 5:00)
- Team Name, Member Names, Institute Name, and Team ID.
- Closing statement: *"Ready for the Techfest on-site arena at IIT Bombay."*

---

## 3. Checklist for Nov 10th Submission
- [ ] Practice track built with white and yellow tape.
- [ ] Camera calibrated using `scripts/calibrate_camera.py`.
- [ ] Lane following tested and stable for 5 consecutive runs.
- [ ] Obstacle stop distance verified ($> 15\text{ cm}$ clearance).
- [ ] 3–5 minute video edited in 1080p and uploaded as unlisted on YouTube.
- [ ] `docs/TECHNICAL_DESIGN_DOCUMENT.md` exported or submitted as 1–2 page PDF.
- [ ] Submission uploaded through the official Techfest portal by the Team Leader.
