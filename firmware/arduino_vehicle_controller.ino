/*
  Urban Autonomous Mobility Challenge (UAMC) - Vehicle Controller Firmware
  Platform: Arduino Nano / Uno / Mega / ESP32
  Description: Real-time actuator PWM driver, ultrasonic polling, encoder interrupts,
               and hardware watchdog safety fail-safe.
*/

#include <Servo.h>

// Pin Definitions
#define PIN_SERVO_STEER        9
#define PIN_MOTOR_PWM          5
#define PIN_MOTOR_DIR_A        6
#define PIN_MOTOR_DIR_B        7

#define PIN_US_TRIG            8
#define PIN_US_ECHO_LEFT       10
#define PIN_US_ECHO_CENTER     11
#define PIN_US_ECHO_RIGHT      12
#define PIN_US_ECHO_SIDE       4

#define PIN_ENCODER_LEFT       2   // External Interrupt
#define PIN_ENCODER_RIGHT      3   // External Interrupt
#define PIN_ESTOP_BUTTON       A0  // Hardware kill switch monitor

// Safety Watchdog
const unsigned long WATCHDOG_TIMEOUT_MS = 200;
unsigned long lastCommandTime = 0;
bool watchdogTriggered = false;

// Actuator Objects
Servo steeringServo;
const int SERVO_CENTER_DEG = 90;
const int SERVO_MAX_TRIM_DEG = 28;

// Odometry
volatile long encoderTicksLeft = 0;
volatile long encoderTicksRight = 0;

void isrEncoderLeft() {
  encoderTicksLeft++;
}

void isrEncoderRight() {
  encoderTicksRight++;
}

// Ultrasonic reading helper
float readUltrasonicDistance(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  long duration = pulseIn(echoPin, HIGH, 25000); // 25ms timeout (~4 meters)
  if (duration <= 0) return 3.0; // max range fallback
  float distanceMeters = (duration * 0.0343) / 200.0;
  return distanceMeters;
}

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 2000);

  // Actuator init
  steeringServo.attach(PIN_SERVO_STEER);
  steeringServo.write(SERVO_CENTER_DEG);

  pinMode(PIN_MOTOR_PWM, OUTPUT);
  pinMode(PIN_MOTOR_DIR_A, OUTPUT);
  pinMode(PIN_MOTOR_DIR_B, OUTPUT);
  setMotorThrottle(0.0);

  // Ultrasonic pins
  pinMode(PIN_US_TRIG, OUTPUT);
  pinMode(PIN_US_ECHO_LEFT, INPUT);
  pinMode(PIN_US_ECHO_CENTER, INPUT);
  pinMode(PIN_US_ECHO_RIGHT, INPUT);
  pinMode(PIN_US_ECHO_SIDE, INPUT);

  // Encoders
  pinMode(PIN_ENCODER_LEFT, INPUT_PULLUP);
  pinMode(PIN_ENCODER_RIGHT, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_ENCODER_LEFT), isrEncoderLeft, RISING);
  attachInterrupt(digitalPinToInterrupt(PIN_ENCODER_RIGHT), isrEncoderRight, RISING);

  pinMode(PIN_ESTOP_BUTTON, INPUT_PULLUP);

  lastCommandTime = millis();
}

void setSteeringNormalized(float norm) {
  // norm is in [-1.0, 1.0]
  norm = constrain(norm, -1.0, 1.0);
  int angle = SERVO_CENTER_DEG + (int)(norm * SERVO_MAX_TRIM_DEG);
  steeringServo.write(angle);
}

void setMotorThrottle(float norm) {
  // norm in [-1.0, 1.0]
  norm = constrain(norm, -1.0, 1.0);
  if (abs(norm) < 0.05) {
    // Active electronic brake
    digitalWrite(PIN_MOTOR_DIR_A, HIGH);
    digitalWrite(PIN_MOTOR_DIR_B, HIGH);
    analogWrite(PIN_MOTOR_PWM, 0);
  } else if (norm > 0) {
    // Forward
    digitalWrite(PIN_MOTOR_DIR_A, HIGH);
    digitalWrite(PIN_MOTOR_DIR_B, LOW);
    int pwm = (int)(norm * 255);
    analogWrite(PIN_MOTOR_PWM, pwm);
  } else {
    // Reverse / Dynamic braking
    digitalWrite(PIN_MOTOR_DIR_A, LOW);
    digitalWrite(PIN_MOTOR_DIR_B, HIGH);
    int pwm = (int)(abs(norm) * 255);
    analogWrite(PIN_MOTOR_PWM, pwm);
  }
}

void processIncomingCommand() {
  if (Serial.available() > 0) {
    String line = Serial.readStringUntil('\n');
    line.trim();
    if (line.startsWith("#CMD,") && line.endsWith("*")) {
      String payload = line.substring(5, line.length() - 1);
      int firstComma = payload.indexOf(',');
      int secondComma = payload.indexOf(',', firstComma + 1);

      if (firstComma > 0 && secondComma > 0) {
        float steer = payload.substring(0, firstComma).toFloat();
        float throttle = payload.substring(firstComma + 1, secondComma).toFloat();
        int estop = payload.substring(secondComma + 1).toInt();

        if (estop == 1) {
          setMotorThrottle(0.0);
          setSteeringNormalized(0.0);
        } else {
          setSteeringNormalized(steer);
          setMotorThrottle(throttle);
        }
        lastCommandTime = millis();
        watchdogTriggered = false;
      }
    }
  }
}

unsigned long lastTelemetryTime = 0;

void loop() {
  processIncomingCommand();

  // Watchdog verification: Fail-safe stop if SBC communication drops
  if (millis() - lastCommandTime > WATCHDOG_TIMEOUT_MS) {
    setMotorThrottle(0.0);
    setSteeringNormalized(0.0);
    watchdogTriggered = true;
  }

  // Periodic Telemetry at 20 Hz
  if (millis() - lastTelemetryTime >= 50) {
    lastTelemetryTime = millis();

    float d_left = readUltrasonicDistance(PIN_US_TRIG, PIN_US_ECHO_LEFT);
    float d_center = readUltrasonicDistance(PIN_US_TRIG, PIN_US_ECHO_CENTER);
    float d_right = readUltrasonicDistance(PIN_US_TRIG, PIN_US_ECHO_RIGHT);
    float d_side = readUltrasonicDistance(PIN_US_TRIG, PIN_US_ECHO_SIDE);
    int estop_btn = (digitalRead(PIN_ESTOP_BUTTON) == LOW) ? 1 : 0;

    // Packet: #TEL,<us_l>,<us_c>,<us_r>,<us_s>,<enc_l>,<enc_r>,<yaw>,<estop>*
    Serial.print("#TEL,");
    Serial.print(d_left, 2); Serial.print(",");
    Serial.print(d_center, 2); Serial.print(",");
    Serial.print(d_right, 2); Serial.print(",");
    Serial.print(d_side, 2); Serial.print(",");
    Serial.print(encoderTicksLeft); Serial.print(",");
    Serial.print(encoderTicksRight); Serial.print(",");
    Serial.print("0.0,"); // yaw placeholder
    Serial.print(estop_btn);
    Serial.println("*");
  }
}
