from .base import Actuator

class ESCMotor(Actuator):
    def __init__(self, pwm, channel,
                 min_us=1100, neutral_us=1500, max_us=1900):
        self.pwm = pwm
        self.channel = channel
        self.min_us = min_us
        self.neutral_us = neutral_us
        self.max_us = max_us

    def set(self, value: float):
        value = max(-1.0, min(1.0, value))
        if value >= 0:
            pulse = self.neutral_us + value * (self.max_us - self.neutral_us)
        else:
            pulse = self.neutral_us + value * (self.neutral_us - self.min_us)
        self.pwm.set_pulse_us(self.channel, pulse)
