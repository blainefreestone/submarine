#pragma once

#include "actuators/actuator_base.h"
#include "config/device_config.h"

/**
 * Central device manager
 * Manages all actuators (servos, motors, pumps)
 * Provides unified interface for controlling devices
 */
class DeviceManager {
public:
    /**
     * Get singleton instance
     */
    static DeviceManager& getInstance() {
        static DeviceManager instance;
        return instance;
    }

    // Prevent copying
    DeviceManager(const DeviceManager&) = delete;
    DeviceManager& operator=(const DeviceManager&) = delete;

    /**
     * Register an actuator with the manager
     */
    bool registerDevice(Actuator* device);

    /**
     * Find device by ID
     */
    Actuator* getDevice(uint8_t id);

    /**
     * Find device by type and index (e.g., first servo)
     */
    Actuator* getDeviceByType(Actuator::Type type, uint8_t index = 0);

    /**
     * Execute command on specific device
     * @param device_id Target device ID
     * @param command Command string
     */
    bool executeDeviceCommand(uint8_t device_id, const char* command);

    /**
     * Update all devices (call regularly from main loop)
     */
    void update();

    /**
     * Stop all devices
     */
    void stopAll();

    /**
     * Get number of registered devices
     */
    uint8_t getDeviceCount() const;

    /**
     * Get device at index
     */
    Actuator* getDeviceAt(uint8_t index);

    /**
     * Print status of all devices
     */
    void printStatus();

private:
    DeviceManager() = default;

    static constexpr size_t MAX_DEVICES = 10;
    Actuator* devices_[MAX_DEVICES] = {nullptr};
    uint8_t device_count_ = 0;
};
