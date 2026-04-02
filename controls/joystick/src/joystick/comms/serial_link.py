import logging
import serial
import threading
import time
from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)


class Command(ABC):
    """Abstract base class for serial commands."""
    
    @abstractmethod
    def to_message(self) -> str:
        """Convert the command to a message string to send over serial."""
        pass


class ServoCommand(Command):
    """Command to control a servo's angle."""
    
    def __init__(self, servo_id: int, angle: int, move_time_ms: int = 50):
        """
        Create a servo command.
        
        Args:
            servo_id: ID of the servo to control
            angle: Target angle (will be clamped to [-100, 100])
            move_time_ms: Time in milliseconds for the servo to reach target
        """
        self.servo_id = servo_id
        self.angle = max(-100, min(100, angle))
        self.move_time_ms = move_time_ms
    
    def to_message(self) -> str:
        return f"SERVO,{self.servo_id},angle,{self.angle},time,{self.move_time_ms}\n"


class MotorCommand(Command):
    """Command to control a motor's speed."""
    
    def __init__(self, motor_id: int, speed: int):
        """
        Create a motor command.
        
        Args:
            motor_id: ID of the motor to control
            speed: Motor speed (will be clamped to [-100, 100])
        """
        self.motor_id = motor_id
        self.speed = max(-100, min(100, speed))
    
    def to_message(self) -> str:
        return f"MOTOR,{self.motor_id},speed,{self.speed}\n"


class LightCommand:
    """Command to toggle the light on or off."""

    def __init__(self, state: bool):
        """
        Args:
            state: True to turn the light on, False to turn it off.
        """
        self.state = state

    def to_message(self) -> str:
        return f"LIGHT,{int(self.state)}\n"

class PressureCommand(Command):
    """Command to request a pressure reading."""

    def to_message(self) -> str:
        return "PRESSURE\n"

class PumpCommand(Command):
    """Command to control a pump's direction."""
    
    def __init__(self, direction: str):
        """
        Args:
            direction: "FILL", "EMPTY", or "STOP"
        """
        self.direction = direction

    def to_message(self) -> str:
        return f"PUMP,{self.direction}\n"


class SerialLink:
    """Manages serial communication with the ESP32."""
    
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 0.1):
        """
        Initialize serial connection to ESP32.
        
        Args:
            port: Serial port path (e.g., "/dev/ttyUSB0")
            baudrate: Communication baud rate port
            timeout: Read timeout in seconds
        """
        #commented out because we are using serial insted of socket for controles
        # self.ser = serial.Serial(
        #     port=port,
        #     baudrate=baudrate,
        #     timeout=timeout,
        # )

        self.ser = serial.serial_for_url("socket://192.168.1.1:3001", timeout=1)

        self._running = True
        self._rx_thread = threading.Thread(
            target=self._read_loop,
            daemon=True,
        )
        self._rx_thread.start()

        time.sleep(2)
        logger.info(f"Connected to ESP32 on {port}")

    def _read_loop(self) -> None:
        """
        Continuously read lines from ESP32 and log them.
        Runs in a separate thread.
        """
        while self._running:
            try:
                line = self.ser.readline().decode("ascii", errors="ignore").strip()
                if line:
                    logger.info(f"[ESP32] {line}")
            except Exception as e:
                logger.error(f"Serial read error: {e}")
                break
    
    def send_command(self, command: Command) -> None:
        """
        Send a command over serial.
        
        Args:
            command: Command object to send
        """
        message = command.to_message()
        self.ser.write(message.encode("ascii"))
        logger.debug(f"Sent: {message.strip()}")

    def send_servo_angle(self, servo_id: int, angle: int, move_time_ms: int = 50) -> None:
        """
        Send a servo angle command (convenience method).
        
        Args:
            servo_id: ID of the servo to control
            angle: Target angle
            move_time_ms: Time in milliseconds for the servo to reach target
        """
        command = ServoCommand(servo_id, angle, move_time_ms)
        self.send_command(command)
    
    def send_motor_speed(self, motor_id: int, speed: int) -> None:
        """
        Send a motor speed command (convenience method).
        
        Args:
            motor_id: ID of the motor to control
            speed: Motor speed
        """
        command = MotorCommand(motor_id, speed)
        self.send_command(command)

    def send_light(self, state: bool) -> None:
        """
        Send a light toggle command (convenience method).
        
        Args:
            state: True to turn the light on, False to turn it off.
        """
        command = LightCommand(state)
        self.send_command(command)

    def send_pressure_request(self) -> None:
        """
        Send a pressure request command (convenience method).
        """
        command = PressureCommand()
        self.send_command(command)

    def send_pump(self, direction: str) -> None:
        """Convenience method to send pump commands."""
        self.send_command(PumpCommand(direction))

    def close(self) -> None:
        """Close the serial connection and stop the read thread."""
        self._running = False
        if self.ser.is_open:
            self.ser.close()
        logger.info("Serial connection closed")

