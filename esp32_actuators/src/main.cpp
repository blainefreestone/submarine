#include <Arduino.h>
#include "config/device_config.h"
#include "managers/device_manager.h"
#include "communication/command_parser.h"
#include "drivers/hiwonder_servo.h"
#include "drivers/dc_motor.h"

// Global device instances
HiWonderServo servo1(Serial1, SERVO_1_ID);

void setup() {
    // Initialize USB serial for commands and debugging
    Serial.begin(USB_BAUD_RATE);
    delay(1000);  // Wait for serial connection
    
    // Initialize servo serial port
    Serial1.begin(
        SERVO_BAUD_RATE,
        SERIAL_8N1,
        SERVO_RX_PIN,
        SERVO_TX_PIN
    );

    // Configure servo parameters
    servo1.setAngleLimits(SERVO_1_ANGLE_MIN, SERVO_1_ANGLE_MAX);
    servo1.setPositionLimits(SERVO_1_POS_MIN, SERVO_1_POS_MAX);
    servo1.setCenter(SERVO_1_CENTER);

    // Register all devices with the manager
    DeviceManager& mgr = DeviceManager::getInstance();
    
    if (!mgr.registerDevice(&servo1)) {
        Serial.println("ERROR: Failed to register servo1");
    }
    
    // Print initial status
    delay(500);
    mgr.printStatus();
    
    Serial.println("\nReady for commands!");
    Serial.println("Send commands like:");
    Serial.println("  SERVO,1,angle,45,time,500");
    Serial.println("  STATUS");
    Serial.println("  STOP_ALL");
}

void loop() {
    // Process incoming commands from USB serial
    CommandParser::update();
    
    // Update all devices
    DeviceManager::getInstance().update();
    
    // Small delay to prevent watchdog issues
    delay(10);
}
