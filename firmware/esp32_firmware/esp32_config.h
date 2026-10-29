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
#define PIN_STEER_SERVO          18   // Steering Servo (LEDC Channel 0, 50Hz)
#define PIN_MOTOR_PWM            19   // Motor Speed PWM (LEDC Channel 1, 20kHz)
#define PIN_MOTOR_DIR_A          22   // Motor Driver H-Bridge IN1
#define PIN_MOTOR_DIR_B          23   // Motor Driver H-Bridge IN2

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
// 3. MOTOR DRIVE & PWM TUNING
// ==========================================
#define MOTOR_LEDC_CH            1
#define MOTOR_LEDC_FREQ          20000     // 20 kHz ultrasonic PWM (silent, no motor whining)
#define MOTOR_LEDC_RES           8         // 8-bit resolution (0 - 255)

// Motor Deadband & Power Limits
#define MOTOR_MIN_START_PWM      35        // Minimum PWM duty to overcome gearbox static friction
#define MOTOR_MAX_SAFE_PWM       220       // Maximum duty cycle cap (prevents motor overheating)

// ==========================================
// 4. ULTRASONIC SENSOR FILTER TUNING
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
