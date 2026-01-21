from .base import Actuator

class Servo(Actuator):
    def __init__(self, pwm, channel, min_us=1000, max_us=2000):
        self.pwm = pwm
        self.channel = channel
        self.min_us = min_us
        self.max_us = max_us

    def set(self, value: float):
        value = max(-1.0, min(1.0, value))
        pulse = self.min_us + (value + 1) / 2 * (self.max_us - self.min_us)
        self.pwm.set_pulse_us(self.channel, pulse)
