import busio
from board import SCL, SDA
from adafruit_pca9685 import PCA9685

class PWMController:
    def __init__(self, frequency=50, address=0x40):
        self.i2c = busio.I2C(SCL, SDA)
        self.pca = PCA9685(self.i2c, address=address)
        self.pca.frequency = frequency

    def set_pulse_us(self, channel: int, pulse_us: float):
        period_us = 1_000_000 / self.pca.frequency
        duty = int((pulse_us / period_us) * 65535)
        self.pca.channels[channel].duty_cycle = duty
