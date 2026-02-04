#include "command_parser.h"
#include <Arduino.h>

char CommandParser::command_buffer_[BUFFER_SIZE];
size_t CommandParser::buffer_pos_ = 0;
bool CommandParser::last_result_ = false;
char CommandParser::error_msg_[128] = "";

void CommandParser::update() {
    while (Serial.available() > 0) {
        char c = Serial.read();
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
        return true;
    }

    // Parametric commands: SERVO,1,angle,90...
    char* type = strtok(work_buf, ",");
    char* id_str = strtok(NULL, ",");
    
    if (type && id_str) {
        uint8_t id = atoi(id_str);
        // Find the rest of the command string after the ID
        // This passes "angle,90,time,500" to the specific device
        const char* remaining = cmd_str + (id_str - work_buf) + strlen(id_str) + 1;
        return DeviceManager::getInstance().executeDeviceCommand(id, remaining);
    }

    return false;
}