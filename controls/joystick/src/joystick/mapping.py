from dataclasses import dataclass
from typing import Any


@dataclass
class AxisConfig:
    """Configuration for a single joystick axis mapping."""
    name: str
    axis_index: int
    target_servo_id: int
    deadzone: float = 0.05
    invert: bool = False
    output_min: float = 0.0
    output_max: float = 180.0
    epsilon: float = 1.0
    move_time_ms: int = 50
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AxisConfig":
        """Create an AxisConfig from a dictionary (e.g., from YAML)."""
        return cls(
            name=data["name"],
            axis_index=data["axis_index"],
            target_servo_id=data["target_servo_id"],
            deadzone=data.get("deadzone", 0.05),
            invert=data.get("invert", False),
            output_min=data.get("output_min", 0.0),
            output_max=data.get("output_max", 180.0),
            epsilon=data.get("epsilon", 1.0),
            move_time_ms=data.get("move_time_ms", 50),
        )


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))


def apply_deadzone(value: float, deadzone: float) -> float:
    """
    Applies a symmetric deadzone around zero.
    Returns 0.0 if inside the deadzone.
    
    Args:
        value: The input value to apply deadzone to
        deadzone: The deadzone threshold
        
    Returns:
        0.0 if |value| < deadzone, otherwise the original value
    """
    if abs(value) < deadzone:
        return 0.0
    return value


def normalize_axis(
    value: float,
    *,
    deadzone: float = 0.05,
    invert: bool = False,
) -> float:
    """
    Takes a raw joystick axis in [-1.0, +1.0] and returns
    a cleaned value in the same range.
    
    Args:
        value: Raw axis value from joystick
        deadzone: Deadzone threshold
        invert: Whether to invert the axis direction
        
    Returns:
        Normalized axis value in [-1.0, +1.0]
    """
    value = clamp(value, -1.0, 1.0)

    if invert:
        value = -value

    value = apply_deadzone(value, deadzone)

    return value


def axis_to_range(
    value: float,
    out_min: float,
    out_max: float,
) -> float:
    """
    Maps [-1.0, +1.0] → [out_min, out_max]
    
    Args:
        value: Normalized axis value in [-1.0, +1.0]
        out_min: Minimum output value
        out_max: Maximum output value
        
    Returns:
        Mapped value in [out_min, out_max]
    """
    # Normalize to [0, 1]
    normalized = (value + 1.0) / 2.0
    return out_min + normalized * (out_max - out_min)

def map_axis(raw_axes: list[float], config: AxisConfig) -> float:
    """
    Map a raw joystick axis to an output range using the provided configuration.
    
    Args:
        raw_axes: List of raw axis values from the joystick
        config: Axis configuration specifying mapping parameters
        
    Returns:
        Mapped axis value in the configured output range
    """
    raw_value = raw_axes[config.axis_index]

    cleaned = normalize_axis(
        raw_value,
        deadzone=config.deadzone,
        invert=config.invert,
    )

    return axis_to_range(
        cleaned,
        config.output_min,
        config.output_max,
    )


class AxisMapper:
    """Manages mapping multiple joystick axes to output values."""
    
    def __init__(self, configs: list[AxisConfig]):
        """
        Initialize the axis mapper with a list of axis configurations.
        
        Args:
            configs: List of AxisConfig objects defining axis mappings
        """
        self.configs = configs
        self.last_values: dict[str, float] = {}
        
    def process_axes(self, raw_axes: list[float]) -> dict[str, float]:
        """
        Process all configured axes and return mapped values.
        
        Args:
            raw_axes: List of raw axis values from the joystick
            
        Returns:
            Dictionary mapping axis names to their mapped values
        """
        results = {}
        for config in self.configs:
            value = map_axis(raw_axes, config)
            results[config.name] = value
        return results
    
    def should_send(self, name: str, value: float) -> bool:
        """
        Check if a value has changed enough to warrant sending an update.
        
        Args:
            name: Name of the axis to check
            value: Current value of the axis
            
        Returns:
            True if the value should be sent, False otherwise
        """
        config = next((c for c in self.configs if c.name == name), None)
        if config is None:
            return False
            
        last = self.last_values.get(name)
        if last is None or abs(value - last) >= config.epsilon:
            self.last_values[name] = value
            return True
        return False
    
    def get_config(self, name: str) -> AxisConfig | None:
        """
        Get the configuration for a specific axis by name.
        
        Args:
            name: Name of the axis
            
        Returns:
            AxisConfig if found, None otherwise
        """
        return next((c for c in self.configs if c.name == name), None)

