#include "command_parser.h"
#include "config/device_config.h"
#include <Arduino.h>
#include <Servo.h>
#include <MS5837.h>

// Bring in the MS5837 sensor instance from main.cpp
extern MS5837 sensor;

// Bring in the external Servo objects defined in main.cpp so the parser can control them
extern Servo thrusterM1;
extern Servo thrusterM2;
extern Servo thrusterM3;
extern Servo thrusterM4;

char CommandParser::command_buffer_[BUFFER_SIZE];
size_t CommandParser::buffer_pos_ = 0;
bool CommandParser::last_result_ = false;
char CommandParser::error_msg_[128] = "";

void CommandParser::update() {
    // Listen to Serial2 (pins 16/17) for incoming commands from the Raspberry Pi
    while (Serial2.available() > 0) {
        char c = Serial2.read();
        if (c == '\n' || c == '\r') {
            if (buffer_pos_ > 0) {
                command_buffer_[buffer_pos_] = '\0';
                last_result_ = parseAndExecute(command_buffer_);
                buffer_pos_ = 0;
            }
        } else if (buffer_pos_ < BUFFER_SIZE - 1) {
            command_buffer_[buffer_pos_++] = c;
        }
    }
}

bool CommandParser::parseAndExecute(const char* cmd_str) {
    char work_buf[BUFFER_SIZE];
    strncpy(work_buf, cmd_str, BUFFER_SIZE);
    
    // Simple command: STATUS
    if (strcmp(work_buf, "STATUS") == 0) {
        DeviceManager::getInstance().printStatus();
        return true;
    }

    // Simple command: STOP_ALL
    if (strcmp(work_buf, "STOP_ALL") == 0) {
        DeviceManager::getInstance().stopAll();
        
        // Neutralize all 4 thrusters (1500µs stop signal)
        thrusterM1.writeMicroseconds(1500);
        thrusterM2.writeMicroseconds(1500);
        thrusterM3.writeMicroseconds(1500);
        thrusterM4.writeMicroseconds(1500);

        // Safe-stop pump and solenoid
        digitalWrite(PUMP_IN1_PIN, LOW);
        digitalWrite(PUMP_IN2_PIN, LOW);
        digitalWrite(SOL_IN3_PIN, LOW);
        return true;
    }

    // Simple command: PRESSURE
    if (strcmp(work_buf, "PRESSURE") == 0) {
        sensor.read();
        float pressure = sensor.pressure();
        float temperature = sensor.temperature();
        float altitude = sensor.altitude();
        float depth = sensor.depth();
        // Send telemetry data back to the Raspberry Pi over Serial2
        Serial2.printf("Pressure: %.2f mbar, Temperature: %.2f C, Altitude: %.2f m, Depth: %.2f m\n", pressure, temperature, altitude, depth);
        return true;
    }

    // Parametric command: LIGHT,<state> (or LIGHTS,<state>)
    if (strncmp(work_buf, "LIGHT", 5) == 0) {
        char* state_str = strchr(work_buf, ',');
        if (state_str) {
            int state = atoi(state_str + 1);
            digitalWrite(LIGHT_GPIO_PIN, state ? HIGH : LOW);
            return true;
        }
    }

    // --- 4-THRUSTER, PUMP, & SOLENOID PACKET PARSING ---
    // Handles incoming string format like: M1:0.50,M2:-0.50,M3:0.00,M4:0.00,PUMP:1,SOL:0
    if (strstr(work_buf, "M1:") != nullptr || strstr(work_buf, "PUMP:") != nullptr) {
        
        // 1. Parse Thruster Values (M1 to M4) - Expected range: -1.0 to 1.0
        // Maps -1.0 -> 1000µs (Full Reverse), 0.0 -> 1500µs (Stop), 1.0 -> 2000µs (Full Forward)
        char* m1Ptr = strstr(work_buf, "M1:");
        if (m1Ptr) {
            float val = atof(m1Ptr + 3);
            int us = 1500 + (int)(val * 500);
            thrusterM1.writeMicroseconds(constrain(us, 1000, 2000));
        }

        char* m2Ptr = strstr(work_buf, "M2:");
        if (m2Ptr) {
            float val = atof(m2Ptr + 3);
            int us = 1500 + (int)(val * 500);
            thrusterM2.writeMicroseconds(constrain(us, 1000, 2000));
        }

        char* m3Ptr = strstr(work_buf, "M3:");
        if (m3Ptr) {
            float val = atof(m3Ptr + 3);
            int us = 1500 + (int)(val * 500);
            thrusterM3.writeMicroseconds(constrain(us, 1000, 2000));
        }

        char* m4Ptr = strstr(work_buf, "M4:");
        if (m4Ptr) {
            float val = atof(m4Ptr + 3);
            int us = 1500 + (int)(val * 500);
            thrusterM4.writeMicroseconds(constrain(us, 1000, 2000));
        }

        // 2. Parse Pump Direction (PUMP:1 = Fill, PUMP:-1 = Empty, PUMP:0 = Stop)
        int pumpDir = 0;
        char* pumpPtr = strstr(work_buf, "PUMP:");
        if (pumpPtr) {
            pumpDir = atoi(pumpPtr + 5);
        }

        // Apply Pump Action (L298N Channel A)
        if (pumpDir == 1) {
            digitalWrite(PUMP_IN1_PIN, HIGH);
            digitalWrite(PUMP_IN2_PIN, LOW);
        } else if (pumpDir == -1) {
            digitalWrite(PUMP_IN1_PIN, LOW);
            digitalWrite(PUMP_IN2_PIN, HIGH);
        } else {
            digitalWrite(PUMP_IN1_PIN, LOW);
            digitalWrite(PUMP_IN2_PIN, LOW);
        }

        // 3. Parse Solenoid Override / State (SOL:1 = Open, SOL:0 = Closed)
        bool solOverride = false;
        char* solPtr = strstr(work_buf, "SOL:");
        if (solPtr) {
            solOverride = (atoi(solPtr + 4) == 1);
        }

        // Automate Solenoid Safety Logic (Open if pump is active OR manual override is pressed)
        bool isPumpActive = (pumpDir != 0);
        if (isPumpActive || solOverride) {
            digitalWrite(SOL_IN3_PIN, HIGH); // Open valve (Channel B)
        } else {
            digitalWrite(SOL_IN3_PIN, LOW);  // Close valve
        }

        return true;
    }

    return false;
}