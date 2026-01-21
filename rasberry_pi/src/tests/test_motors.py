import time
import yaml

from src.drivers.pwm_controller import PWMController
from src.actuators.servo import Servo
from src.actuators.esc_motor import ESCMotor

CONFIG = "src/config/actuators.yaml"

def main():
    with open(CONFIG) as f:
        cfg = yaml.safe_load(f)

    pwm_cfg = cfg["pwm_controller"]
    pwm = PWMController(
        frequency=pwm_cfg["frequency"],
        address=pwm_cfg["address"]
    )

    servos = []
    motors = []

    for s in cfg["servos"]:
        servos.append(Servo(pwm, s["channel"]))

    for m in cfg["motors"]:
        motors.append(ESCMotor(pwm, m["channel"]))

    print("Centering servos, neutral motors...")
    for s in servos:
        s.set(0.0)
    for m in motors:
        m.set(0.0)

    time.sleep(3)

    print("Slow forward...")
    for m in motors:
        m.set(0.3)

    time.sleep(3)

    print("Stopping motors...")
    for m in motors:
        m.set(0.0)

if __name__ == "__main__":
    main()
