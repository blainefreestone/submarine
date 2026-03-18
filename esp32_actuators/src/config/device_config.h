#pragma once

#include <Arduino.h>
#include <MS5837.h>

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

// GPIO pin for light control
static constexpr uint8_t LIGHT_GPIO_PIN = 25;

// I2C configurations for MS5837 sensor
static constexpr uint8_t I2C_SDA_PIN = 21;  // Default SDA pin
static constexpr uint8_t I2C_SCL_PIN = 22;  // Default SCL pin

extern MS5837 sensor;