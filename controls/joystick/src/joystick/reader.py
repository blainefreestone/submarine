import logging
import pygame
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class JoystickState:
    """Represents the current state of all joystick inputs."""
    axes: list[float]
    buttons: list[int]
    hats: list[tuple[int, int]]


class JoystickReader:
    """Reads input from a connected joystick device."""
    
    def __init__(self, joystick_index: int = 0):
        """
        Initialize the joystick reader.
        
        Args:
            joystick_index: Index of the joystick to use (0 = first joystick)
            
        Raises:
            RuntimeError: If no joystick is detected
        """
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            raise RuntimeError("No joystick detected")

        self.joystick = pygame.joystick.Joystick(joystick_index)
        self.joystick.init()

        self.num_axes = self.joystick.get_numaxes()
        self.num_buttons = self.joystick.get_numbuttons()
        self.num_hats = self.joystick.get_numhats()

        logger.info(f"Joystick connected: {self.joystick.get_name()}")
        logger.info(f"Axes: {self.num_axes}, Buttons: {self.num_buttons}, Hats: {self.num_hats}")

    def read(self) -> JoystickState:
        """
        Poll the joystick and return the current state.
        
        Returns:
            JoystickState containing current axes, buttons, and hats
        """
        pygame.event.pump()  # Required to update joystick state

        axes = [self.joystick.get_axis(i) for i in range(self.num_axes)]
        buttons = [self.joystick.get_button(i) for i in range(self.num_buttons)]
        hats = [self.joystick.get_hat(i) for i in range(self.num_hats)]

        return JoystickState(
            axes=axes,
            buttons=buttons,
            hats=hats,
        )

