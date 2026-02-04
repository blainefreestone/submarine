"""Main entry point for the submarine joystick controller."""
import logging
import sys
from pathlib import Path

# Add src directory to path for direct execution
if __name__ == "__main__":
    src_path = Path(__file__).parent.parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

from joystick.controller import JoystickController


def setup_logging(level: int = logging.INFO) -> None:
    """
    Configure logging for the application.
    
    Args:
        level: Logging level (default: INFO)
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main() -> None:
    """Main entry point for the joystick controller application."""
    setup_logging()
    
    logger = logging.getLogger(__name__)
    
    # Look for config file in the project root
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    
    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        logger.error("Please create a config.yaml file in the project root")
        sys.exit(1)
    
    try:
        controller = JoystickController(config_path)
        controller.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

