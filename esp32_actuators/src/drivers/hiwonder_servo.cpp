#include "hiwonder_servo.h"

// ========================
// Protocol constants
// ========================

static constexpr uint8_t FRAME_HEADER = 0x55;

// Lobot / HiWonder command set
static constexpr uint8_t CMD_MOVE_TIME_WRITE      = 0x01;
static constexpr uint8_t CMD_MOVE_STOP            = 0x0C;
static constexpr uint8_t CMD_POS_READ              = 0x1C;
static constexpr uint8_t CMD_VIN_READ              = 0x1B;
static constexpr uint8_t CMD_MOTOR_MODE_WRITE      = 0x1D;
static constexpr uint8_t CMD_LOAD_OR_UNLOAD_WRITE  = 0x1F;

// ========================
// Constructor
// ========================

HiWonderServo::HiWonderServo(HardwareSerial& serial, uint8_t id)
    : serial_(serial), id_(id) {
    snprintf(status_, sizeof(status_), "Servo ID %d: OK", id_);
}

// ========================
// Actuator interface implementation
// ========================

Actuator::Type HiWonderServo::getType() const {
    return Type::SERVO;
}

uint8_t HiWonderServo::getId() const {
    return id_;
}

Actuator::State HiWonderServo::getState() const {
    return state_;
}

void HiWonderServo::stop() {
    sendFrame(id_, CMD_MOVE_STOP, nullptr, 0);
    state_ = State::IDLE;
    snprintf(status_, sizeof(status_), "Servo ID %d: Stopped", id_);
}

bool HiWonderServo::executeCommand(const char* command) {
    // Parse command: "angle,90,time,500"
    float angle = 0.0f;
    uint16_t time_ms = 500;
    
    if (sscanf(command, "angle,%f,time,%hu", &angle, &time_ms) == 2) {
        moveAngle(angle, time_ms);
        state_ = State::MOVING;
        snprintf(status_, sizeof(status_), "Servo ID %d: Moving to %.1f°", id_, angle);
        return true;
    }
    
    if (strcmp(command, "load") == 0) {
        load();
        snprintf(status_, sizeof(status_), "Servo ID %d: Loaded", id_);
        return true;
    }
    
    if (strcmp(command, "unload") == 0) {
        unload();
        snprintf(status_, sizeof(status_), "Servo ID %d: Unloaded", id_);
        return true;
    }
    
    return false;
}

void HiWonderServo::update() {
    // No state tracking needed for servos, they handle timing internally
}

const char* HiWonderServo::getStatus() const {
    return status_;
}

// ========================
// Public API
// ========================

void HiWonderServo::move(uint16_t position,
                          uint16_t time_ms) {
    position = constrain(position, min_pos_, max_pos_);

    uint8_t payload[4] = {
        static_cast<uint8_t>(position & 0xFF),
        static_cast<uint8_t>(position >> 8),
        static_cast<uint8_t>(time_ms & 0xFF),
        static_cast<uint8_t>(time_ms >> 8)
    };

    sendFrame(id_, CMD_MOVE_TIME_WRITE, payload, sizeof(payload));
}

void HiWonderServo::moveAngle(float angle_deg,
                               uint16_t time_ms) {
    uint16_t position = angleToPosition(angle_deg);
    move(position, time_ms);
}

void HiWonderServo::load() {
    uint8_t payload = 1;
    sendFrame(id_, CMD_LOAD_OR_UNLOAD_WRITE, &payload, 1);
}


// In hiwonder_servo.cpp
void HiWonderServo::unload() {
    // 0x14 is the Unload command for HiWonder/Lewansoul servos
    uint8_t packet[] = { 0x55, 0x55, id_, 0x04, 0x14, 0x00 }; 
    // Calculate checksum here if your driver requires it
    serial_.write(packet, sizeof(packet)); // Use serial_ instead of _serial
}

void HiWonderServo::setAngleLimits(float min_angle, float max_angle) {
    min_angle_ = min_angle;
    max_angle_ = max_angle;
}

void HiWonderServo::setPositionLimits(uint16_t min_pos,
                                       uint16_t max_pos) {
    min_pos_ = min_pos;
    max_pos_ = max_pos;
}

void HiWonderServo::setCenter(uint16_t center_pos) {
    center_pos_ = center_pos;
}

// ========================
// Internal helpers
// ========================

uint16_t HiWonderServo::angleToPosition(float angle_deg) const {
    angle_deg = constrain(angle_deg, min_angle_, max_angle_);

    float ratio =
        (angle_deg - min_angle_) /
        (max_angle_ - min_angle_);

    return static_cast<uint16_t>(
        min_pos_ + ratio * (max_pos_ - min_pos_)
    );
}

uint8_t HiWonderServo::checksum(const uint8_t* buf,
                                uint8_t length) {
    uint16_t sum = 0;
    // Match original: buf[3] contains the length field (payload_len + 3)
    // Sum from index 2 to buf[3] + 1 inclusive
    for (uint8_t i = 2; i < buf[3] + 2; i++) {
        sum += buf[i];
    }
    return static_cast<uint8_t>(~sum);
}

void HiWonderServo::sendFrame(uint8_t id,
                               uint8_t command,
                               const uint8_t* payload,
                               uint8_t payload_len) {
    uint8_t buf[16];
    uint8_t len = payload_len + 3;

    buf[0] = FRAME_HEADER;
    buf[1] = FRAME_HEADER;
    buf[2] = id;
    buf[3] = len;
    buf[4] = command;

    for (uint8_t i = 0; i < payload_len; i++) {
        buf[5 + i] = payload[i];
    }

    buf[5 + payload_len] = checksum(buf, 0);  // length param unused, buf[3] is used
    serial_.write(buf, 6 + payload_len);
}
