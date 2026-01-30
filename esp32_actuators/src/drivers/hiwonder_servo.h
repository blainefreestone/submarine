#pragma once

#include <Arduino.h>
#include "../actuators/actuator_base.h"

class HiWonderServo : public Actuator {
public:
    explicit HiWonderServo(HardwareSerial& serial, uint8_t id);

    // Actuator interface implementation
    Type getType() const override;
    uint8_t getId() const override;
    State getState() const override;
    void stop() override;
    bool executeCommand(const char* command) override;
    void update() override;
    const char* getStatus() const override;

    // Raw position control (0–1000)
    void move(uint16_t position, uint16_t time_ms);

    // Angle control (degrees)
    void moveAngle(float angle_deg, uint16_t time_ms);

    // Configuration
    void setAngleLimits(float min_deg, float max_deg);
    void setPositionLimits(uint16_t min_pos, uint16_t max_pos);
    void setCenter(uint16_t center_pos);

    void load();
    void unload();

private:
    HardwareSerial& serial_;
    uint8_t id_;
    State state_ = State::IDLE;
    char status_[64] = {0};

    // Angle mapping parameters
    float min_angle_ = -120.0f;
    float max_angle_ =  120.0f;

    uint16_t min_pos_ = 0;
    uint16_t max_pos_ = 1000;
    uint16_t center_pos_ = 500;

    uint8_t checksum(const uint8_t* buf, uint8_t length);
    void sendFrame(uint8_t id, uint8_t command,
                   const uint8_t* payload, uint8_t payload_len);

    uint16_t angleToPosition(float angle_deg) const;
};
