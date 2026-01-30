#pragma once

#include <Arduino.h>

/**
 * Device Configuration
 * Define all actuators and their pins here
 */

// Serial communication pins for HiWonder servos
static constexpr uint8_t SERVO_TX_PIN = 17;
static constexpr uint8_t SERVO_RX_PIN = 16;
static constexpr uint32_t SERVO_BAUD_RATE = 115200;

// Servo definitions
static constexpr uint8_t SERVO_1_ID = 1;
static constexpr float SERVO_1_ANGLE_MIN = -120.0f;
static constexpr float SERVO_1_ANGLE_MAX = 120.0f;
static constexpr uint16_t SERVO_1_POS_MIN = 0;
static constexpr uint16_t SERVO_1_POS_MAX = 1000;
static constexpr uint16_t SERVO_1_CENTER = 500;