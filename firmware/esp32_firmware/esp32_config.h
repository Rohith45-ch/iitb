/*
  ESP32 Microcontroller — Centralized Tuning & Hardware Configuration Block.
  All tuneable hardware pins, servo trims, motor PWM deadbands, ultrasonic filter
  coefficients, and TinyML safety thresholds are configured here in one place.
*/

#ifndef ESP32_CONFIG_H
#define ESP32_CONFIG_H

#include <Arduino.h>

// ==========================================
// 1. PIN CONFIGURATION (ESP32 DevKit V1)
// ==========================================
// Actuators
#define PIN_STEER_SERVO          18   // Steering Servo SG90/MG90S (LEDC Ch 0, 50Hz, 1000-2000µs)
#define PIN_MOTOR_PWM            19   // L298N ENA + ENB (both tied together) — 20kHz PWM speed
#define PIN_MOTOR_DIR_A          22   // L298N IN1 + IN3 — Motor direction A (HIGH=fwd)
#define PIN_MOTOR_DIR_B          23   // L298N IN2 + IN4 — Motor direction B (LOW=fwd)

// Ultrasonic Sensor Array (HC-SR04)
#define PIN_US_TRIG              5    // Shared 10us Trigger Pin
#define PIN_US_ECHO_LEFT         34   // Left Front Sonar Echo (Input Only, 3.3V divided)
#define PIN_US_ECHO_CENTER       35   // Center Front Sonar Echo (Input Only, 3.3V divided)
#define PIN_US_ECHO_RIGHT        32   // Right Front Sonar Echo (3.3V divided)
#define PIN_US_ECHO_SIDE         33   // Flank Parking Sonar Echo (3.3V divided)

// Quadrature Wheel Encoders
#define PIN_ENCODER_LEFT         25   // Left Wheel Encoder Channel A
#define PIN_ENCODER_RIGHT        26   // Right Wheel Encoder Channel A

// Safety & Communication
#define PIN_ESTOP_INPUT          27   // Active-LOW Physical Emergency Kill Switch
#define PIN_UART_RX              16   // ESP32 RX2 connected to RPi TXD (GPIO 14)
#define PIN_UART_TX              17   // ESP32 TX2 connected to RPi RXD (GPIO 15)

// ==========================================
// 2. STEERING SERVO CALIBRATION & TRIMS
// ==========================================
#define SERVO_LEDC_CH            0
#define SERVO_LEDC_FREQ          50        // 50 Hz standard servo frequency
#define SERVO_LEDC_RES           16        // 16-bit resolution (0 - 65535)

// Servo Pulse Calibration (Microseconds)
// Tune SERVO_MID_US by +/- 50us if the physical car pulls slightly to one side!
#define SERVO_MIN_US             1000      // Full Left Steering (-28.0 deg)
#define SERVO_MID_US             1500      // Center Steering (0.0 deg neutral trim)
#define SERVO_MAX_US             2000      // Full Right Steering (+28.0 deg)
#define SERVO_MAX_PHYSICAL_DEG   28.0f     // Maximum physical Ackermann steering travel

// ==========================================
// 3. MOTOR DRIVE — L298N H-BRIDGE (PDF-confirmed build)
// ==========================================
// *** PDF SPEC: USE_ESC_MOTOR_DRIVER = 0  (L298N + TT Gear Motors) ***
// Set to 0 for L298N dual H-bridge (our actual hardware per Wiring_and_Pin_Map PDF)
// Set to 1 only if swapping to an RC ESC in future
#define USE_ESC_MOTOR_DRIVER     0

// L298N H-Bridge PWM Tuning (USE_ESC_MOTOR_DRIVER == 0) — ACTIVE
// GPIO 19 → L298N ENA + ENB (both tied together, jumpers removed)
// GPIO 22 → L298N IN1 + IN3 (direction A — forward = HIGH)
// GPIO 23 → L298N IN2 + IN4 (direction B — forward = LOW)
// Motor supply: 7 V buck converter output → L298N +12V(VS) terminal
// Logic supply: 5 V buck converter output → L298N +5V terminal (5V jumper REMOVED)
#define MOTOR_LEDC_CH            1
#define MOTOR_LEDC_FREQ          20000     // 20 kHz ultrasonic PWM (inaudible)
#define MOTOR_LEDC_RES           8         // 8-bit resolution (0–255)
#define MOTOR_MIN_START_PWM      35        // Minimum PWM to overcome TT gearbox static friction
#define MOTOR_MAX_SAFE_PWM       220       // Maximum PWM duty-cycle safety cap

// RC ESC Servo-style PWM Tuning (USE_ESC_MOTOR_DRIVER == 1) — INACTIVE for this build
#define ESC_LEDC_CH              1
#define ESC_LEDC_FREQ            50        // 50 Hz standard RC ESC frequency
#define ESC_LEDC_RES             16        // 16-bit resolution for microsecond precision
#define ESC_REVERSE_MAX_US       1000      // Full reverse pulse width (us)
#define ESC_NEUTRAL_US           1500      // Neutral / stopped pulse width (us)
#define ESC_FORWARD_MAX_US       2000      // Full forward pulse width (us)
#define ESC_FORWARD_SAFE_CAP_US  1700      // Safe forward speed limiter for indoor testing
#define ESC_DEADBAND_NORM        0.04f     // Small deadband around 0 throttle

// ==========================================
// 4. SENSOR FITTINGS (per Wiring_and_Pin_Map PDF §1, §3, §6, §7)
// ==========================================
// PDF §6 item 4 & §7: Only single center sonar is fitted.
// Setting to 1 skips reading unfitted pins (34, 32, 33), avoiding 60ms timeout delays
// and preventing false emergency stops from floating-pin electrical noise.
#define SINGLE_CENTER_SONAR_ONLY 1

// PDF §6 item 5 & §7: Encoders not fitted for this car.
// Setting to 0 disables attaching interrupts to pins 25/26, preventing noise triggers.
#define ENABLE_WHEEL_ENCODERS    0

// ==========================================
// 5. ULTRASONIC SENSOR FILTER TUNING
// ==========================================
#define US_FILTER_WINDOW_SIZE    5         // Median-of-5 sliding window size
#define US_EMA_SMOOTHING_ALPHA   0.35f     // Exponential Moving Average weight (0.0 - 1.0)
#define US_MAX_PHYSICAL_DELTA_M  0.30f     // Rate-of-change rejection threshold per cycle
#define US_MAX_VALID_RANGE_M     2.50f     // Arena ceiling distance clamp (meters)
#define US_MIN_VALID_RANGE_M     0.03f     // Sensor physical blind-zone (meters)

// ==========================================
// 5. TinyML SAFETY & MOTION THRESHOLDS
// ==========================================
#define TINYML_COLLISION_G       2.8f      // Sudden jerk impulse threshold for collision detection
#define TINYML_ROLLOVER_DEG      35.0f     // Roll / Pitch chassis tilt angle limit for rollover stop
#define TINYML_BUMP_WARNING_G    1.2f      // Vibration warning threshold for rough surface

// ==========================================
// 6. COMMUNICATION & WATCHDOG SAFETY
// ==========================================
#define UART_BAUDRATE            115200    // UART Baudrate between RPi and ESP32
#define WATCHDOG_TIMEOUT_MS      150       // Time before automatic E-Stop if RPi stops sending commands
#define TELEMETRY_INTERVAL_MS    33        // Telemetry packet rate (~30 Hz)

#endif // ESP32_CONFIG_H
