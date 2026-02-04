"""Controller module for managing joystick input and serial output."""
import logging
import time
from pathlib import Path
from typing import Any

import yaml

from joystick.reader import JoystickReader
from joystick.mapping import AxisConfig, AxisMapper
from joystick.comms.serial_link import SerialLink, ServoCommand


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
        
        # Control loop settings
        self.send_rate_hz = serial_config.get("send_rate_hz", 30)
        self.period = 1.0 / self.send_rate_hz
        
        logger.info(f"Controller initialized with {len(axis_configs)} axes")
        logger.info(f"Update rate: {self.send_rate_hz} Hz")
    
    def _load_config(self, config_path: str | Path) -> dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to the YAML configuration file
            
        Returns:
            Configuration dictionary
        """
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        logger.info(f"Loaded configuration from {config_path}")
        return config
    
    def run(self) -> None:
        """
        Run the main control loop.
        
        Continuously reads joystick state, maps axes, and sends commands
        to the serial device. Runs until interrupted with Ctrl+C.
        """
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
                
                time.sleep(self.period)
                
        except KeyboardInterrupt:
            logger.info("Control loop interrupted")
        finally:
            self.cleanup()
    
    def _send_axis_command(self, axis_name: str, value: float) -> None:
        """
        Send a command for a specific axis.
        
        Args:
            axis_name: Name of the axis
            value: Mapped value to send
        """
        config = self.axis_mapper.get_config(axis_name)
        if config is None:
            logger.warning(f"No configuration found for axis: {axis_name}")
            return
        
        value_int = int(round(value))
        
        command = ServoCommand(
            servo_id=config.target_servo_id,
            angle=value_int,
            move_time_ms=config.move_time_ms,
        )
        
        self.serial_link.send_command(command)
        logger.debug(f"{axis_name}: {value_int}")
    
    def cleanup(self) -> None:
        """Clean up resources when shutting down."""
        logger.info("Cleaning up...")
        self.serial_link.close()
        logger.info("Shutdown complete")
