#include "device_manager.h"

bool DeviceManager::registerDevice(Actuator* device) {
    if (device_count_ >= MAX_DEVICES) {
        return false;
    }
    
    // Check if device ID already exists
    for (uint8_t i = 0; i < device_count_; i++) {
        if (devices_[i]->getId() == device->getId()) {
            return false;  // Duplicate ID
        }
    }
    
    devices_[device_count_++] = device;
    return true;
}

Actuator* DeviceManager::getDevice(uint8_t id) {
    for (uint8_t i = 0; i < device_count_; i++) {
        if (devices_[i]->getId() == id) {
            return devices_[i];
        }
    }
    return nullptr;
}

Actuator* DeviceManager::getDeviceByType(Actuator::Type type, uint8_t index) {
    uint8_t count = 0;
    for (uint8_t i = 0; i < device_count_; i++) {
        if (devices_[i]->getType() == type) {
            if (count == index) {
                return devices_[i];
            }
            count++;
        }
    }
    return nullptr;
}

bool DeviceManager::executeDeviceCommand(uint8_t device_id, const char* command) {
    Actuator* device = getDevice(device_id);
    if (device == nullptr) {
        return false;
    }
    return device->executeCommand(command);
}

void DeviceManager::update() {
    for (uint8_t i = 0; i < device_count_; i++) {
        devices_[i]->update();
    }
}

void DeviceManager::stopAll() {
    for (uint8_t i = 0; i < device_count_; i++) {
        devices_[i]->stop();
    }
}

uint8_t DeviceManager::getDeviceCount() const {
    return device_count_;
}

Actuator* DeviceManager::getDeviceAt(uint8_t index) {
    if (index >= device_count_) {
        return nullptr;
    }
    return devices_[index];
}

void DeviceManager::printStatus() {
    Serial.println("=== Device Status ===");
    for (uint8_t i = 0; i < device_count_; i++) {
        Serial.printf("  %s\n", devices_[i]->getStatus());
    }
    Serial.println("====================");
}
