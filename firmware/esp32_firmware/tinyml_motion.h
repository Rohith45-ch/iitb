/*
  TinyML Motion & Collision Anomaly Classifier for ESP32
  Runs on Core 0 of ESP32 at 100 Hz.
  Classifies 6-DOF IMU accelerations and gyroscope angular rates to detect:
  - NOMINAL: Normal driving conditions
  - COLLISION: Abrupt high-G impact with obstacle or curb
  - ROLLOVER: Excessive vehicle tilt angle exceeding stability threshold
*/

#ifndef TINYML_MOTION_H
#define TINYML_MOTION_H

#include <Arduino.h>

enum VehicleMotionState {
  MOTION_NOMINAL = 0,
  MOTION_BUMP_WARNING = 1,
  MOTION_COLLISION_DETECTED = 2,
  MOTION_ROLLOVER_DETECTED = 3
};

class TinyMLMotionClassifier {
private:
  const float ACCEL_COLLISION_THRESHOLD_G = 2.8f;  // > 2.8G sudden impulse
  const float TILT_ROLLOVER_THRESHOLD_DEG = 35.0f; // > 35 degree roll/pitch

  float filterAx = 0.0f;
  float filterAy = 0.0f;
  float filterAz = 1.0f;

public:
  TinyMLMotionClassifier() {}

  VehicleMotionState classify(float ax, float ay, float az, float pitch_deg, float roll_deg) {
    // Low-pass exponential moving average filter
    filterAx = 0.8f * filterAx + 0.2f * ax;
    filterAy = 0.8f * filterAy + 0.2f * ay;
    filterAz = 0.8f * filterAz + 0.2f * az;

    // High-pass magnitude impulse
    float deltaX = ax - filterAx;
    float deltaY = ay - filterAy;
    float jerkMagnitude = sqrt(deltaX * deltaX + deltaY * deltaY);

    if (abs(roll_deg) > TILT_ROLLOVER_THRESHOLD_DEG || abs(pitch_deg) > TILT_ROLLOVER_THRESHOLD_DEG) {
      return MOTION_ROLLOVER_DETECTED;
    }

    if (jerkMagnitude > ACCEL_COLLISION_THRESHOLD_G) {
      return MOTION_COLLISION_DETECTED;
    }

    if (jerkMagnitude > 1.2f) {
      return MOTION_BUMP_WARNING;
    }

    return MOTION_NOMINAL;
  }
};

#endif // TINYML_MOTION_H
