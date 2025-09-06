"""Centralized logging configuration for WuWa MCP Server."""

import logging
import logging.handlers
import sys

from .config import LogSettings


class ColoredFormatter(logging.Formatter):
    """Colored console formatter for better readability."""

    # Color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors if supported."""
        # Add color to levelname
        if hasattr(sys.stderr, "isatty") and sys.stderr.isatty():
            color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
            record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"

        return super().format(record)


def setup_logging(
    settings: LogSettings | None = None,
    logger_name: str = "wuwa_mcp",
) -> logging.Logger:
    """Setup centralized logging configuration.

    Args:
        settings: Logging settings. If None, defaults will be used.
        logger_name: Name of the root logger.

    Returns:
        Configured logger instance.
    """
    if settings is None:
        settings = LogSettings()

    # Get or create logger
    logger = logging.getLogger(logger_name)

    # Avoid duplicate handlers if already configured
    if logger.handlers:
        return logger

    # Set level
    numeric_level = getattr(logging, settings.level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)

    # Create formatter
    formatter = ColoredFormatter(fmt=settings.format, datefmt="%Y-%m-%d %H:%M:%S")
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    # Disable uvicorn access logs if requested
    if settings.disable_uvicorn_logs:
        logging.getLogger("uvicorn.access").disabled = True
        logging.getLogger("uvicorn.access").propagate = False

    # Set other library log levels to WARNING to reduce noise
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    logger.info(f"Logging configured with level: {settings.level}")
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module.

    Args:
        name: Name of the module/component.

    Returns:
        Logger instance.
    """
    return logging.getLogger(f"wuwa_mcp.{name}")


class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""

    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        if not hasattr(self, "_logger"):
            class_name = self.__class__.__name__.lower()
            self._logger = get_logger(class_name)
        return self._logger
