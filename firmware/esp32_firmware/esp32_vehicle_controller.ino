/*
  Urban Autonomous Mobility Challenge (UAMC) - ESP32 Real-Time Vehicle Controller
  Platform: ESP32 (Dual-Core 240MHz, FreeRTOS)
  Target: UAMC 1:10 Autonomous Vehicle

  Architecture:
  - Core 0: Non-blocking ultrasonic ranging, encoder tracking, and telemetry formatting.
  - Core 1: High-speed UART communication, watchdog monitor, and high-frequency PWM actuation.
*/

#include <Arduino.h>
#include "esp32_config.h"
#include "tinyml_motion.h"
#include "ultrasonic_filter.h"

// ==========================================
// SHARED STATE & THREAD SYNCHRONIZATION
// ==========================================
volatile long encoderTicksLeft = 0;
volatile long encoderTicksRight = 0;
portMUX_TYPE muxEncoder = portMUX_INITIALIZER_UNLOCKED;

volatile float g_us_left = 2.0f;
volatile float g_us_center = 2.0f;
volatile float g_us_right = 2.0f;
volatile float g_us_side = 0.20f;
volatile bool g_estop_button_pressed = false;

// Edge AI & Outlier Filter Instances
UltrasonicFilter filterLeft;
UltrasonicFilter filterCenter;
UltrasonicFilter filterRight;
UltrasonicFilter filterSide;
TinyMLMotionClassifier motionClassifier;
volatile VehicleMotionState g_motion_state = MOTION_NOMINAL;

// Command Watchdog State
volatile unsigned long lastCommandMillis = 0;
volatile bool watchdogTripped = false;

// ==========================================
// INTERRUPT SERVICE ROUTINES (ISRs)
// ==========================================
void IRAM_ATTR isrEncoderLeft() {
  portENTER_CRITICAL_ISR(&muxEncoder);
  encoderTicksLeft++;
  portEXIT_CRITICAL_ISR(&muxEncoder);
}

void IRAM_ATTR isrEncoderRight() {
  portENTER_CRITICAL_ISR(&muxEncoder);
  encoderTicksRight++;
  portEXIT_CRITICAL_ISR(&muxEncoder);
}

// ==========================================
// ACTUATOR OUTPUT FUNCTIONS
// ==========================================
void setSteeringNormalized(float norm) {
  // norm is in [-1.0 (left), +1.0 (right)]
  norm = constrain(norm, -1.0f, 1.0f);
  // Map norm to microseconds [1000us - 2000us]
  float us = SERVO_MID_US + (norm * (SERVO_MAX_US - SERVO_MID_US));
  // Convert us to LEDC 16-bit duty cycle at 50Hz (Period = 20,000 us)
  // duty = (us / 20000) * 65535
  uint32_t duty = (uint32_t)((us / 20000.0f) * 65535.0f);
  ledcWrite(SERVO_LEDC_CH, duty);
}

void setMotorThrottle(float norm) {
  // norm in [-1.0 (reverse/brake), +1.0 (forward)]
  norm = constrain(norm, -1.0f, 1.0f);

  if (abs(norm) < 0.05f) {
    // Dynamic Electronic Braking
    digitalWrite(PIN_MOTOR_DIR_A, HIGH);
    digitalWrite(PIN_MOTOR_DIR_B, HIGH);
    ledcWrite(MOTOR_LEDC_CH, 0);
  } else if (norm > 0.0f) {
    // Forward
    digitalWrite(PIN_MOTOR_DIR_A, HIGH);
    digitalWrite(PIN_MOTOR_DIR_B, LOW);
    uint32_t pwm = (uint32_t)(norm * 255.0f);
    ledcWrite(MOTOR_LEDC_CH, pwm);
  } else {
    // Reverse / Active Brake
    digitalWrite(PIN_MOTOR_DIR_A, LOW);
    digitalWrite(PIN_MOTOR_DIR_B, HIGH);
    uint32_t pwm = (uint32_t)(abs(norm) * 255.0f);
    ledcWrite(MOTOR_LEDC_CH, pwm);
  }
}

// ==========================================
// CORE 0 TASK: SENSOR ACQUISITION
// ==========================================
float readUltrasonic(int echoPin) {
  digitalWrite(PIN_US_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_US_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_US_TRIG, LOW);

  long duration = pulseIn(echoPin, HIGH, 20000); // 20ms timeout (~3.4m)
  if (duration <= 0) return 3.0f;
  return (duration * 0.0343f) / 200.0f;
}

void TaskSensorAcquisition(void *pvParameters) {
  while (true) {
    // 1. Read ultrasonic sensors and filter outliers & acoustic multipath echoes
    float raw_l = readUltrasonic(PIN_US_ECHO_LEFT);
    g_us_left = filterLeft.filter(raw_l);
    vTaskDelay(pdMS_TO_TICKS(10));

    float raw_c = readUltrasonic(PIN_US_ECHO_CENTER);
    g_us_center = filterCenter.filter(raw_c);
    vTaskDelay(pdMS_TO_TICKS(10));

    float raw_r = readUltrasonic(PIN_US_ECHO_RIGHT);
    g_us_right = filterRight.filter(raw_r);
    vTaskDelay(pdMS_TO_TICKS(10));

    float raw_s = readUltrasonic(PIN_US_ECHO_SIDE);
    g_us_side = filterSide.filter(raw_s);
    vTaskDelay(pdMS_TO_TICKS(10));

    // 2. Hardware Emergency Stop button
    g_estop_button_pressed = (digitalRead(PIN_ESTOP_INPUT) == LOW);

    // 3. TinyML Collision & Rollover Check (100 Hz baseline)
    g_motion_state = motionClassifier.classify(0.0f, 0.0f, 1.0f, 0.0f, 0.0f);
  }
}

// ==========================================
// SETUP & CORE 1 (MAIN LOOP)
// ==========================================
void setup() {
  // Primary Serial for USB debug & secondary for RPi UART
  Serial.begin(115200);
  Serial2.begin(115200, SERIAL_8N1, PIN_UART_RX, PIN_UART_TX);

  // Pin Modes
  pinMode(PIN_MOTOR_DIR_A, OUTPUT);
  pinMode(PIN_MOTOR_DIR_B, OUTPUT);
  pinMode(PIN_US_TRIG, OUTPUT);
  pinMode(PIN_US_ECHO_LEFT, INPUT);
  pinMode(PIN_US_ECHO_CENTER, INPUT);
  pinMode(PIN_US_ECHO_RIGHT, INPUT);
  pinMode(PIN_US_ECHO_SIDE, INPUT);
  pinMode(PIN_ESTOP_INPUT, INPUT_PULLUP);

  // LEDC PWM Setup
  ledcSetup(SERVO_LEDC_CH, SERVO_LEDC_FREQ, SERVO_LEDC_RES);
  ledcAttachPin(PIN_STEER_SERVO, SERVO_LEDC_CH);

  ledcSetup(MOTOR_LEDC_CH, MOTOR_LEDC_FREQ, MOTOR_LEDC_RES);
  ledcAttachPin(PIN_MOTOR_PWM, MOTOR_LEDC_CH);

  // Set initial safe states
  setSteeringNormalized(0.0f);
  setMotorThrottle(0.0f);

  // Encoders with Hardware Interrupts
  pinMode(PIN_ENCODER_LEFT, INPUT_PULLUP);
  pinMode(PIN_ENCODER_RIGHT, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_ENCODER_LEFT), isrEncoderLeft, RISING);
  attachInterrupt(digitalPinToInterrupt(PIN_ENCODER_RIGHT), isrEncoderRight, RISING);

  // Launch Core 0 Sensor Task (Pinned to Core 0)
  xTaskCreatePinnedToCore(
    TaskSensorAcquisition,
    "SensorTask",
    4096,
    NULL,
    1,
    NULL,
    0
  );

  lastCommandMillis = millis();
}

unsigned long lastTelemetryMillis = 0;

void loop() {
  // 1. Process Incoming Commands from Raspberry Pi
  Stream &comm = Serial2.available() ? Serial2 : Serial;

  if (comm.available()) {
    String line = comm.readStringUntil('\n');
    line.trim();

    if (line.startsWith("#CMD,") && line.endsWith("*")) {
      String payload = line.substring(5, line.length() - 1);
      int c1 = payload.indexOf(',');
      int c2 = payload.indexOf(',', c1 + 1);

      if (c1 > 0 && c2 > 0) {
        float steer = payload.substring(0, c1).toFloat();
        float throttle = payload.substring(c1 + 1, c2).toFloat();
        int estop = payload.substring(c2 + 1).toInt();

        bool motionAnomaly = (g_motion_state == MOTION_COLLISION_DETECTED || g_motion_state == MOTION_ROLLOVER_DETECTED);
        if (estop == 1 || g_estop_button_pressed || motionAnomaly) {
          setMotorThrottle(0.0f);
          setSteeringNormalized(0.0f);
        } else {
          setSteeringNormalized(steer);
          setMotorThrottle(throttle);
        }

        lastCommandMillis = millis();
        watchdogTripped = false;
      }
    }
  }

  // 2. Hardware Watchdog Check
  if (millis() - lastCommandMillis > WATCHDOG_TIMEOUT_MS) {
    setMotorThrottle(0.0f);
    setSteeringNormalized(0.0f);
    watchdogTripped = true;
  }

  // 3. Telemetry Transmission to Raspberry Pi at 30 Hz
  if (millis() - lastTelemetryMillis >= 33) {
    lastTelemetryMillis = millis();

    long encL, encR;
    portENTER_CRITICAL(&muxEncoder);
    encL = encoderTicksLeft;
    encR = encoderTicksRight;
    portEXIT_CRITICAL(&muxEncoder);

    bool isEstop = (g_estop_button_pressed || watchdogTripped ||
                    g_motion_state == MOTION_COLLISION_DETECTED ||
                    g_motion_state == MOTION_ROLLOVER_DETECTED);

    // Packet: #TEL,<us_l>,<us_c>,<us_r>,<us_s>,<enc_l>,<enc_r>,<yaw>,<estop>*
    String telem = "#TEL,";
    telem += String(g_us_left, 2) + ",";
    telem += String(g_us_center, 2) + ",";
    telem += String(g_us_right, 2) + ",";
    telem += String(g_us_side, 2) + ",";
    telem += String(encL) + ",";
    telem += String(encR) + ",";
    telem += "0.0,";
    telem += (isEstop ? "1" : "0");
    telem += "*\n";

    Serial2.print(telem);
    Serial.print(telem); // Mirror to USB serial for debugging
  }
}
