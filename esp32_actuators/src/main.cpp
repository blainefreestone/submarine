#include <Arduino.h>
#include "config/device_config.h"
#include "managers/device_manager.h"
#include "communication/command_parser.h"
#include <MS5837.h>
#include <Wire.h>

#define USB_BAUD_RATE 115200

// Define the MS5837 sensor instance
MS5837 sensor;

// --- L298N MOTOR DRIVER PIN DEFINITIONS FOR BALLAST & SOLENOID ---
// (Ensure these pin constants are also defined in your device_config.h, 
// or update them here to match your physical ESP32 wiring)
#ifndef PUMP_IN1_PIN
#define PUMP_IN1_PIN 26
#endif
#ifndef PUMP_IN2_PIN
#define PUMP_IN2_PIN 25
#endif
#ifndef SOL_IN3_PIN
#define SOL_IN3_PIN 33
#endif
#ifndef SOL_IN4_PIN
#define SOL_IN4_PIN 32
#endif

void setup() {
    // Initialize USB serial for commands and debugging
    Serial.begin(USB_BAUD_RATE);
    delay(1000);  // Wait for serial connection
    
    // Initialize light GPIO pin
    pinMode(LIGHT_GPIO_PIN, OUTPUT);
    digitalWrite(LIGHT_GPIO_PIN, LOW);  // Ensure light is off at startup

    // Initialize L298N Pump Pins (Channel A) & Solenoid Pins (Channel B)
    pinMode(PUMP_IN1_PIN, OUTPUT);
    pinMode(PUMP_IN2_PIN, OUTPUT);
    pinMode(SOL_IN3_PIN, OUTPUT);
    pinMode(SOL_IN4_PIN, OUTPUT);
    digitalWrite(SOL_IN4_PIN, LOW); // Unidirectional ground reference for Channel B

    // Ensure pump and solenoid start OFF/closed safely
    digitalWrite(PUMP_IN1_PIN, LOW);
    digitalWrite(PUMP_IN2_PIN, LOW);
    digitalWrite(SOL_IN3_PIN, LOW);

    // Initialize I2C bus
    Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);

    // Initialize the MS5837 sensor
    if (!sensor.init()) {
        Serial.println("ERROR: Unable to initialize MS5837 sensor");
    } else {
        Serial.println("MS5837 sensor initialized successfully");
    }
    sensor.setFluidDensity(997);

    // Register all devices with the manager
    DeviceManager& mgr = DeviceManager::getInstance();
    
    // Print initial status
    delay(500);
    mgr.printStatus();
    
    Serial.println("\nReady for commands!");
    Serial.println("Send commands like:");
    Serial.println("  PUMP,FILL (or EMPTY / STOP)");
    Serial.println("  SOL,1 (Manual override open) or SOL,0 (Closed)");
    Serial.println("  LIGHTS,1 or LIGHTS,0");
    Serial.println("  STATUS");
    Serial.println("  STOP_ALL");
}

void loop() {
    // Process incoming commands from USB serial
    CommandParser::update();
    
    // Update all devices managed by the DeviceManager
    DeviceManager::getInstance().update();
    
    // Small delay to prevent watchdog issues
    delay(10);
}