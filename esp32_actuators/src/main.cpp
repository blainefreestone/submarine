#include <Arduino.h>
#include <Servo.h>
#include <Wire.h>
#include <MS5837.h>
#include "config/device_config.h"
#include "managers/device_manager.h"
#include "communication/command_parser.h"

#define USB_BAUD_RATE 115200

// --- SECONDARY HARDWARE SERIAL (UART2) PINS ---
// Dedicated for communication with the Raspberry Pi (Pins 16 & 17)
#define RXD2 16
#define TXD2 17
#define SECONDARY_BAUD_RATE 9600

// --- THRUSTER PIN DEFINITIONS (ZTW Shark G2 ESCs) ---
#define M1_PIN 4
#define M2_PIN 18
#define M3_PIN 19
#define M4_PIN 23

// Create Servo objects for the 4 thrusters
Servo thrusterM1;
Servo thrusterM2;
Servo thrusterM3;
Servo thrusterM4;

// Define the MS5837 sensor instance
MS5837 sensor;

// --- L298N MOTOR DRIVER PIN DEFINITIONS FOR BALLAST & SOLENOID ---
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
    // Initialize USB serial for workbench debugging (Uses USB TX=1, RX=3)
    Serial.begin(USB_BAUD_RATE);
    delay(1000);  // Wait for serial connection

    // Initialize Secondary Hardware Serial (UART2) on pins 16 & 17 for the Raspberry Pi
    Serial2.begin(SECONDARY_BAUD_RATE, SERIAL_8N1, RXD2, TXD2);
    Serial.println("UART2 initialized on pins 16 (RX2) and 17 (TX2) for Raspberry Pi link.");

    // --- THRUSTER ESC INITIALIZATION & ARMING ---
    thrusterM1.attach(M1_PIN, 1000, 2000);
    thrusterM2.attach(M2_PIN, 1000, 2000);
    thrusterM3.attach(M3_PIN, 1000, 2000);
    thrusterM4.attach(M4_PIN, 1000, 2000);

    // Send neutral (1500µs) stop signal to arm the ZTW Shark G2 ESCs
    Serial.println("Arming ESCs (sending neutral pulse)...");
    thrusterM1.writeMicroseconds(1500);
    thrusterM2.writeMicroseconds(1500);
    thrusterM3.writeMicroseconds(1500);
    thrusterM4.writeMicroseconds(1500);
    delay(2000); // Give ESCs time to initialize and emit arming confirmation beeps
    Serial.println("ESCs armed successfully!");

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
    
    Serial.println("\nReady for operation!");
}

void loop() {
    // Process incoming command packets from the Raspberry Pi over UART2
    CommandParser::update();
    
    // Update all devices managed by the DeviceManager
    DeviceManager::getInstance().update();
    
    // Small delay to prevent watchdog issues
    delay(10);
}