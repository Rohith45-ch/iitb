/*
  Ultrasonic Outlier & Multipath Rejection Filter for ESP32
  Filters raw HC-SR04 pulse durations using:
  1. Median-of-5 Sliding Window (Rejects single-cycle acoustic dropouts and multipath spikes)
  2. Rate-of-Change Limit (Physical maximum velocity clamp: vehicle cannot move > 1.5m in 20ms)
  3. Exponential Moving Average (EMA) smoothing for stable parking bay edge detection.
*/

#ifndef ULTRASONIC_FILTER_H
#define ULTRASONIC_FILTER_H

#include <Arduino.h>

class UltrasonicFilter {
private:
  static const int WINDOW_SIZE = 5;
  float window[WINDOW_SIZE];
  int windowIdx;
  bool isInitialized;
  float lastValidDistance;
  float smoothedDistance;
  const float ALPHA = 0.35f;             // EMA weight for new reading
  const float MAX_PHYSICAL_DELTA = 0.30f; // Max realistic change between 20ms cycles (m)
  const float MAX_VALID_RANGE = 2.50f;    // Max operational range in tabletop smart city (m)
  const float MIN_VALID_RANGE = 0.03f;    // 3cm minimum blind spot (m)

  float computeMedian(float arr[], int n) {
    float temp[WINDOW_SIZE];
    for (int i = 0; i < n; i++) temp[i] = arr[i];
    // Simple insertion sort for 5 elements (microsecond execution on ESP32)
    for (int i = 1; i < n; i++) {
      float key = temp[i];
      int j = i - 1;
      while (j >= 0 && temp[j] > key) {
        temp[j + 1] = temp[j];
        j = j - 1;
      }
      temp[j + 1] = key;
    }
    return temp[n / 2];
  }

public:
  UltrasonicFilter() : windowIdx(0), isInitialized(false), lastValidDistance(1.5f), smoothedDistance(1.5f) {
    for (int i = 0; i < WINDOW_SIZE; i++) window[i] = 1.5f;
  }

  float filter(float rawDistance_m) {
    // 1. Sanity check bounds
    float sanitized = rawDistance_m;
    if (sanitized > MAX_VALID_RANGE) sanitized = MAX_VALID_RANGE;
    if (sanitized < MIN_VALID_RANGE) sanitized = MIN_VALID_RANGE;

    // 2. Reject impossible jump if initialized (rate of change clamp)
    if (isInitialized) {
      if (abs(sanitized - lastValidDistance) > MAX_PHYSICAL_DELTA) {
        // Soft-clamp towards the new measurement to prevent sensor latching
        sanitized = lastValidDistance + (sanitized > lastValidDistance ? MAX_PHYSICAL_DELTA : -MAX_PHYSICAL_DELTA);
      }
    }

    // 3. Insert into circular window
    window[windowIdx] = sanitized;
    windowIdx = (windowIdx + 1) % WINDOW_SIZE;

    // 4. Compute median
    float median = computeMedian(window, WINDOW_SIZE);
    lastValidDistance = median;

    // 5. Apply Exponential Moving Average (EMA)
    if (!isInitialized) {
      smoothedDistance = median;
      isInitialized = true;
    } else {
      smoothedDistance = ALPHA * median + (1.0f - ALPHA) * smoothedDistance;
    }

    return smoothedDistance;
  }

  void reset(float initialDist = 1.5f) {
    for (int i = 0; i < WINDOW_SIZE; i++) window[i] = initialDist;
    lastValidDistance = initialDist;
    smoothedDistance = initialDist;
    windowIdx = 0;
    isInitialized = false;
  }
};

#endif // ULTRASONIC_FILTER_H
