# Engineering Calculations & Kinematic Models

This document details the mathematical models, physical dimensions, sensor thresholds, and control parameters governing the **AML-Rover-V1** autonomous vehicle for the Urban Autonomous Mobility Challenge (UAMC).

---

## 1. Vehicle Kinematics & Ackermann Steering Geometry

### A. Bicycle Kinematic Model
For a standard front-wheel steered non-holonomic vehicle at low to moderate speeds ($v \le 1.0\text{ m/s}$), tire slip angles are negligible ($\alpha_{tire} \approx 0$). The motion is modeled using the kinematic bicycle model:

$$\begin{aligned}
\dot{x} &= v \cos(\theta) \\
\dot{y} &= v \sin(\theta) \\
\dot{\theta} &= \frac{v}{L} \tan(\delta)
\end{aligned}$$

Where:
- $(x, y)$ is the Cartesian position of the rear axle midpoint.
- $\theta$ is the vehicle heading orientation in the global frame.
- $v$ is the longitudinal forward velocity.
- $L$ is the vehicle wheelbase: **$L = 260\text{ mm} = 0.260\text{ m}$**.
- $\delta$ is the effective steering angle of the front wheels.

### B. Turning Radius Calculation
The turning radius $R$ measured from the center of curvature to the center of the rear axle is given by:

$$R = \frac{L}{\tan(\delta)}$$

Given our physical steering servo linkage limits:
- Maximum steering angle: $\delta_{max} = 28^\circ \approx 0.4886\text{ rad}$
- Minimum turning radius:
  $$R_{min} = \frac{0.260}{\tan(28^\circ)} = \frac{0.260}{0.5317} = 0.4890\text{ m} \approx 48.9\text{ cm}$$

**Validation with Arena Constraints:**
Standard UAMC arena lanes are $35\text{ cm}$ wide per lane ($70\text{ cm}$ total two-way road), and roundabouts have an inner island radius $R_{island} \ge 40\text{ cm}$ with lane center radius $R_{roundabout} \approx 57.5\text{ cm}$.
Since $R_{min} = 48.9\text{ cm} < R_{roundabout} = 57.5\text{ cm}$, the vehicle can easily negotiate the tightest roundabout curve without departing its designated lane.

---

## 2. Longitudinal Dynamics & Stopping Distance Analysis

### A. Stopping Distance Formulation
Total distance $d_{total}$ required to bring the vehicle to a full stop from forward velocity $v$ upon detecting an obstacle or stop line:

$$d_{total} = d_{reaction} + d_{braking}$$

$$d_{total} = v \cdot t_{reaction} + \frac{v^2}{2 \cdot a_{decel}}$$

Where:
- $v$: Vehicle operating speed ($0.45\text{ m/s}$ standard cruising speed, $0.65\text{ m/s}$ maximum burst speed).
- $t_{reaction}$: Total perception and computation latency:
  $$t_{reaction} = t_{camera\_exposure} + t_{inference} + t_{uart\_transmission} + t_{esc\_response}$$
  - $t_{camera\_exposure} = 16.7\text{ ms}$ (at 60 FPS)
  - $t_{inference} = 25.0\text{ ms}$ (Perception pipeline processing)
  - $t_{uart\_transmission} = 2.0\text{ ms}$ (115200 baud serial packet)
  - $t_{esc\_response} = 15.0\text{ ms}$ (Motor driver inductance & brake response)
  - **$t_{reaction, max} \approx 58.7\text{ ms} \approx 0.06\text{ s}$**.
- $a_{decel}$: Controlled motor deceleration rate (with active regenerative / dynamic braking on ESC):
  $$a_{decel} = 2.2\text{ m/s}^2$$

### B. Numerical Solution:
1. **At Cruising Speed ($v = 0.45\text{ m/s}$)**:
   $$d_{reaction} = 0.45 \times 0.06 = 0.027\text{ m} = 2.7\text{ cm}$$
   $$d_{braking} = \frac{(0.45)^2}{2 \times 2.2} = \frac{0.2025}{4.4} = 0.046\text{ m} = 4.6\text{ cm}$$
   $$d_{total} = 2.7\text{ cm} + 4.6\text{ cm} = \mathbf{7.3\text{ cm}}$$

2. **At Maximum Speed ($v = 0.65\text{ m/s}$)**:
   $$d_{reaction} = 0.65 \times 0.06 = 0.039\text{ m} = 3.9\text{ cm}$$
   $$d_{braking} = \frac{(0.65)^2}{2 \times 2.2} = \frac{0.4225}{4.4} = 0.096\text{ m} = 9.6\text{ cm}$$
   $$d_{total} = 3.9\text{ cm} + 9.6\text{ cm} = \mathbf{13.5\text{ cm}}$$

### C. Sensor Trigger Distance Thresholds:
To guarantee safety with a **Safety Margin Factor of 2.0×**:
- **Obstacle Emergency Halt Threshold ($d_{halt}$)**: Set to **$25\text{ cm}$** ($> 13.5\text{ cm}$).
- **Obstacle Slowdown Deceleration Threshold ($d_{slow}$)**: Set to **$45\text{ cm}$**.
- **Stop Line Stop Threshold**: Detection at **$35\text{ cm}$**, initiating smooth linear deceleration targeting $0\text{ km/h}$ exactly $5\text{ cm}$ before the stop line.

---

## 3. Optical Perception & Geometry Calculations

### A. Camera Field of View (FOV) & Road Coverage
Using a wide-angle lens with horizontal FOV $\theta_H = 120^\circ$, mounted at height $h = 140\text{ mm}$ with downward tilt pitch angle $\alpha_{pitch} = 22^\circ$:

1. **Near Ground Visibility Point ($d_{near}$)**:
   $$d_{near} = \frac{h}{\tan(\alpha_{pitch} + \frac{\theta_V}{2})}$$
   With vertical FOV $\theta_V \approx 75^\circ$:
   $$d_{near} = \frac{0.14}{\tan(22^\circ + 37.5^\circ)} = \frac{0.14}{\tan(59.5^\circ)} = \frac{0.14}{1.6977} \approx 0.082\text{ m} = \mathbf{8.2\text{ cm}}$$
   The car sees the road just $8.2\text{ cm}$ ahead of its bumper, leaving virtually no blind zone.

2. **Lookahead Horizon ($d_{look}$)**:
   The lookahead target distance for Pure Pursuit steering is chosen at **$l_d = 28\text{ cm}$**.
   At $28\text{ cm}$, the camera provides a horizontal field width of:
   $$W_{ground} = 2 \cdot d_{look} \cdot \tan\left(\frac{\theta_H}{2}\right) = 2 \times 0.28 \times \tan(60^\circ) = 0.56 \times 1.732 \approx 0.97\text{ m}$$
   Since road width is $0.70\text{ m}$, the camera easily observes both left and right lane boundaries with ample margins.

---

## 4. Lateral Controller Tuning (Pure Pursuit)

The Pure Pursuit algorithm calculates steering angle $\delta$ based on curvature $\gamma$:

$$\gamma = \frac{2 \sin(\alpha)}{l_d}$$

$$\delta = \arctan(\gamma \cdot L) = \arctan\left(\frac{2 L \sin(\alpha)}{l_d}\right)$$

Where:
- $\alpha$: Heading error between vehicle centerline and vector to the lookahead goal point $(x_g, y_g)$.
- $l_d$: Lookahead distance, dynamically scaled with speed:
  $$l_d(v) = k_{look} \cdot v + l_{d,0}$$
  - $l_{d,0} = 0.22\text{ m}$ (base static lookahead)
  - $k_{look} = 0.15\text{ s}$ (speed sensitivity gain)
  - At $v = 0.45\text{ m/s}$: $l_d = 0.15 \times 0.45 + 0.22 = 0.2875\text{ m} \approx 28.7\text{ cm}$.

---

## 5. Summary of Tuned Calibration Constants
| Parameter | Symbol | Design Value | Units |
| :--- | :--- | :--- | :--- |
| Wheelbase | $L$ | 0.260 | m |
| Track Width | $W$ | 0.165 | m |
| Max Steering Angle | $\delta_{max}$ | 28.0 | degrees |
| Cruising Velocity | $v_{cruise}$ | 0.45 | m/s |
| Approach Velocity | $v_{slow}$ | 0.25 | m/s |
| Max Deceleration | $a_{decel}$ | 2.20 | m/s² |
| Emergency Stop Range | $d_{halt}$ | 0.25 | m |
| Warning Slowdown Range | $d_{slow}$ | 0.45 | m |
| Base Lookahead | $l_{d,0}$ | 0.22 | m |
| Lookahead Gain | $k_{look}$ | 0.15 | s |
| Speed PID Proportional | $K_p$ | 1.80 | - |
| Speed PID Integral | $K_i$ | 0.45 | - |
| Speed PID Derivative | $K_d$ | 0.08 | - |
