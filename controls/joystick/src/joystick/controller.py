"""Controller module for managing joystick input and serial output."""
import logging
import time
from pathlib import Path
from typing import Any

import yaml

from joystick.reader import JoystickReader
from joystick.mapping import AxisConfig, AxisMapper
from joystick.comms.serial_link import (
    SerialLink, 
    MotorCommand, 
    LightCommand, 
    PressureCommand, 
    PumpCommand, 
    SolenoidOverrideCommand
)


logger = logging.getLogger(__name__)


class JoystickController:
    """Main controller that coordinates joystick reading and serial communication."""
    
    def __init__(self, config_path: str | Path):
        """
        Initialize the controller with a configuration file.
        
        Args:
            config_path: Path to the YAML configuration file
        """
        self.config = self._load_config(config_path)
        
        # Initialize joystick reader
        joystick_index = self.config["joystick"]["device_index"]
        self.reader = JoystickReader(joystick_index)
        
        # Initialize serial communication
        serial_config = self.config["serial"]
        self.serial_link = SerialLink(
            port=serial_config["port"],
            baudrate=serial_config["baudrate"],
            timeout=serial_config.get("timeout", 0.1),
        )
        
        # Initialize axis mapper
        axis_configs = [
            AxisConfig.from_dict(axis_data)
            for axis_data in self.config.get("axes", [])
        ]
        self.axis_mapper = AxisMapper(axis_configs)
        
        # Initialize button states and auxiliary states
        self.button_states = {button['name']: False for button in self.config.get('buttons', [])}
        self.light_state = False  # Track light state
        self.solenoid_override_state = False  # Track manual solenoid override state
        self.pump_states: dict[str, str] = {}
        
        # Control loop settings
        self.send_rate_hz = serial_config.get("send_rate_hz", 30)
        self.period = 1.0 / self.send_rate_hz
        
        logger.info(f"Controller initialized with {len(axis_configs)} axes")
        logger.info(f"Update rate: {self.send_rate_hz} Hz")
    
    def _load_config(self, config_path: str | Path) -> dict[str, Any]:
        """Load configuration from YAML file."""
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        logger.info(f"Loaded configuration from {config_path}")
        return config
    
    def run(self) -> None:
        """Run the main control loop."""
        logger.info("Starting control loop. Press Ctrl+C to exit.")
        
        try:
            while True:
                # Read joystick state
                state = self.reader.read()
                
                # Process all configured axes
                mapped_values = self.axis_mapper.process_axes(state.axes)
                
                # Send updates for axes that have changed enough
                for axis_name, value in mapped_values.items():
                    if self.axis_mapper.should_send(axis_name, value):
                        self._send_axis_command(axis_name, value)
                
                # Process button presses
                self._process_buttons(state.buttons)
                
                time.sleep(self.period)
                
        except KeyboardInterrupt:
            logger.info("Control loop interrupted")
        finally:
            self.cleanup()
    
    def _send_axis_command(self, axis_name: str, value: float) -> None:
        """Send a command for a specific axis."""
        config = self.axis_mapper.get_config(axis_name)
        if config is None:
            logger.warning(f"No configuration found for axis: {axis_name}")
            return
        
        value_int = int(round(value))
        
        # Send appropriate command based on device/axis type (Servos removed)
        if config.device_type == "motor" or config.device_type == "motor_group":
            command = MotorCommand(
                motor_id=config.target_motor_id if hasattr(config, 'target_motor_id') else axis_name,
                speed=value_int,
            )
            logger.info(f"[{axis_name}] MOTOR_GROUP/ESC,speed,{value_int}")
        elif config.device_type == "pump":
            direction = "FILL" if value_int > 0 else "EMPTY" if value_int < 0 else "STOP"

            last_direction = self.pump_states.get(axis_name, "STOP")
            if direction in {"FILL", "EMPTY"}:
                if last_direction != "STOP":
                    return
            elif direction == "STOP":
                if last_direction == "STOP":
                    return

            command = PumpCommand(direction)
            self.pump_states[axis_name] = direction
        
        self.serial_link.send_command(command)
    
    def _process_buttons(self, buttons: list[int]) -> None:
        """Process button presses and execute associated commands."""
        for button_config in self.config.get("buttons", []):
            name = button_config["name"]
            index = button_config["button_index"]
            command = button_config["command"]

            if buttons[index] and not self.button_states[name]:
                if command == "TOGGLE_LIGHT":
                    self.light_state = not self.light_state
                    light_command = LightCommand(self.light_state)
                    self.serial_link.send_command(light_command)
                    logger.info(f"[Button: {name}] Light toggled to {'ON' if self.light_state else 'OFF'}")

                elif command == "PRESSURE":
                    pressure_command = PressureCommand()
                    self.serial_link.send_command(pressure_command)
                    logger.info(f"[Button: {name}] Pressure read command sent")

                elif command == "SOLENOID_OVERRIDE":
                    self.solenoid_override_state = not self.solenoid_override_state
                    solenoid_command = SolenoidOverrideCommand(self.solenoid_override_state)
                    self.serial_link.send_command(solenoid_command)
                    logger.info(f"[Button: {name}] Manual Solenoid Override toggled to {'OPEN' if self.solenoid_override_state else 'CLOSED'}")

            self.button_states[name] = buttons[index]

    def cleanup(self) -> None:
        """Clean up resources when shutting down."""
        logger.info("Cleaning up...")
        self.serial_link.close()
        logger.info("Shutdown complete")