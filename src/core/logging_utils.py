"""
Shared logging utilities for M365 Security Toolkit.

Provides consistent logging configuration across all MCP servers and scripts.
"""

import logging
from pathlib import Path


def setup_logging(
    logger_name: str = __name__,
    log_filename: str = "m365_toolkit.log",
    log_level: int = logging.INFO,
) -> logging.Logger:
    """
    Configure logging with consistent format and handlers.

    Creates log directory at ~/.aitk/logs/ if it doesn't exist.

    Args:
        logger_name: Name for the logger (default: __name__)
        log_filename: Name of log file in ~/.aitk/logs/
        log_level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    log_dir = Path.home() / ".aitk" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / log_filename),
            logging.StreamHandler(),
        ],
    )

    return logging.getLogger(logger_name)
