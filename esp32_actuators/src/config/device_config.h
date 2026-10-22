#pragma once

#include <Arduino.h>

// --- SYSTEM & SERIAL CONFIG ---
#define USB_BAUD_RATE 115200

// UART2 (Connected to Raspberry Pi inside the hull)
#define RXD2 16
#define TXD2 17
#define SECONDARY_BAUD_RATE 9600

// --- I2C BUS CONFIG (MS5837 Depth Sensor) ---
#ifndef I2C_SDA_PIN
#define I2C_SDA_PIN 21  // Standard ESP32 SDA default (adjust if using custom pins)
#endif
#ifndef I2C_SCL_PIN
#define I2C_SCL_PIN 22  // Standard ESP32 SCL default (adjust if using custom pins)
#endif

// --- THRUSTER ESC PINS (ZTW Shark G2) ---
#define M1_PIN 4
#define M2_PIN 18
#define M3_PIN 19
#define M4_PIN 23

// --- L298N BALLAST PUMP & SOLENOID PINS ---
#define PUMP_IN1_PIN 26
#define PUMP_IN2_PIN 25
#define SOL_IN3_PIN  33
#define SOL_IN4_PIN  32

// --- UNDERWATER LED LIGHT PIN ---
#ifndef LIGHT_GPIO_PIN
#define LIGHT_GPIO_PIN 27  // Adjust this to match your actual light relay/transistor pin
#endif

// --- COMMAND PARSER CONFIG ---
#define BUFFER_SIZE 256