#pragma once

#include "managers/device_manager.h"

/**
 * Serial command parser for USB communication
 * Parses commands and routes them to appropriate devices
 * 
 * Command format:
 * SERVO,<id>,angle,<deg>,time,<ms>     - Move servo to angle
 * MOTOR,<id>,speed,<0-255>,dir,<forward|reverse|brake>  - Control motor
 * PUMP,<id>,power,<0-255>              - Control pump (PWM)
 * SERVO,<id>,load                       - Load servo
 * SERVO,<id>,unload                     - Unload servo
 * STATUS                                - Print status of all devices
 * STOP_ALL                              - Emergency stop all devices
 */
class CommandParser {
public:
    /**
     * Process incoming serial data
     * Call this regularly from main loop
     */
    static void update();

    /**
     * Get parsed command result
     */
    static bool getLastResult();

    /**
     * Get last error message
     */
    static const char* getLastError();

private:
    static constexpr size_t BUFFER_SIZE = 256;
    static char command_buffer_[BUFFER_SIZE];
    static size_t buffer_pos_;
    static bool last_result_;
    static char error_msg_[128];

    /**
     * Parse and execute a complete command
     */
    static bool parseAndExecute(const char* cmd_str);

    /**
     * Helper to trim whitespace
     */
    static char* trimWhitespace(char* str);
};
