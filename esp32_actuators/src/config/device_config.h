#pragma once

#include <Arduino.h>
#include <MS5837.h>

/**
 * Device Configuration
 * Define all actuators and their pins here
 */

// --- L298N BALLAST & SOLENOID PINS ---
// Channel A: Ballast Water Pump
static constexpr uint8_t PUMP_IN1_PIN = 26;
static constexpr uint8_t PUMP_IN2_PIN = 25;

// Channel B: Solenoid Valve Control
static constexpr uint8_t SOL_IN3_PIN = 33;
static constexpr uint8_t SOL_IN4_PIN = 32; // Tied LOW for unidirectional control

// --- GPIO PIN FOR LIGHT CONTROL ---
static constexpr uint8_t LIGHT_GPIO_PIN = 14;

// --- I2C CONFIGURATIONS FOR MS5837 SENSOR ---
static constexpr uint8_t I2C_SDA_PIN = 21;  // Default SDA pin
static constexpr uint8_t I2C_SCL_PIN = 22;  // Default SCL pin

extern MS5837 sensor;