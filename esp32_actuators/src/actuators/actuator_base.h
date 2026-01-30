#pragma once

#include <Arduino.h>

/**
 * Abstract base class for all actuators (servos, motors, pumps)
 * Provides a unified interface for controlling different device types
 */
class Actuator {
public:
    enum class Type {
        SERVO,
        DC_MOTOR,
        PUMP
    };

    enum class State {
        IDLE,
        MOVING,
        ERROR
    };

    virtual ~Actuator() = default;

    /**
     * Get the actuator type
     */
    virtual Type getType() const = 0;

    /**
     * Get the unique device ID
     */
    virtual uint8_t getId() const = 0;

    /**
     * Get current state
     */
    virtual State getState() const = 0;

    /**
     * Stop any active motion/operation
     */
    virtual void stop() = 0;

    /**
     * Generic command handler for device-specific operations
     * Format: "SERVO,1,angle,90,time,500" or "MOTOR,2,speed,100"
     */
    virtual bool executeCommand(const char* command) = 0;

    /**
     * Update internal state (call regularly from main loop)
     */
    virtual void update() = 0;

    /**
     * Get human-readable status
     */
    virtual const char* getStatus() const = 0;
};
