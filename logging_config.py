"""
Logging Configuration for Adastrea Director

Provides centralized logging configuration with structured output,
file rotation, and debugging support.

Usage:
    from logging_config import setup_logging, get_logger
    
    # Setup logging once at application start
    setup_logging(debug=False)
    
    # Get logger in any module
    logger = get_logger(__name__)
    logger.info("Application started")
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


# Default log directory
DEFAULT_LOG_DIR = Path(__file__).parent / "logs"

# Log format with timestamp, level, module, and message
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Detailed format for debug mode
DEBUG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"


def setup_logging(
    debug: bool = False,
    log_file: Optional[str] = None,
    console: bool = True,
    log_dir: Optional[Path] = None
) -> None:
    """
    Setup logging configuration for the application.
    
    Args:
        debug: If True, set log level to DEBUG and use detailed format
        log_file: Optional custom log file name (default: adastrea_YYYYMMDD.log)
        console: If True, also log to console
        log_dir: Optional custom log directory (default: ./logs)
    """
    # Determine log directory
    if log_dir is None:
        log_dir = DEFAULT_LOG_DIR
    
    # Create log directory if it doesn't exist
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine log file name
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = f"adastrea_{timestamp}.log"
    
    log_path = log_dir / log_file
    
    # Determine log level and format
    log_level = logging.DEBUG if debug else logging.INFO
    log_format = DEBUG_FORMAT if debug else LOG_FORMAT
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatters
    formatter = logging.Formatter(log_format, datefmt=LOG_DATE_FORMAT)
    
    # File handler with rotation (10MB max, keep 5 backups)
    file_handler = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler if requested
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Log initial message
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized - Level: {logging.getLevelName(log_level)}, File: {log_path}")
    
    # Suppress noisy third-party loggers
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Logger name (typically __name__ from calling module)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_exception(logger: logging.Logger, message: str, exc_info: bool = True) -> None:
    """
    Log an exception with full traceback.
    
    Args:
        logger: Logger instance
        message: Error message
        exc_info: If True, include exception traceback
    """
    logger.error(message, exc_info=exc_info)


def log_debug_info(logger: logging.Logger, context: str, **kwargs) -> None:
    """
    Log debug information with context and key-value pairs.
    
    Args:
        logger: Logger instance
        context: Context description
        **kwargs: Key-value pairs to log
    """
    debug_msg = f"{context}"
    if kwargs:
        debug_details = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        debug_msg += f" - {debug_details}"
    logger.debug(debug_msg)


class LogContext:
    """
    Context manager for logging operation start/end with timing.
    
    Usage:
        with LogContext(logger, "Processing query"):
            # ... do work ...
            pass
    """
    
    def __init__(self, logger: logging.Logger, operation: str, level: int = logging.INFO):
        """
        Initialize log context.
        
        Args:
            logger: Logger instance
            operation: Operation description
            level: Log level (default: INFO)
        """
        self.logger = logger
        self.operation = operation
        self.level = level
        self.start_time = None
    
    def __enter__(self):
        """Start operation logging."""
        self.start_time = datetime.now()
        self.logger.log(self.level, f"Starting: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End operation logging with timing."""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.log(self.level, f"Completed: {self.operation} (took {duration:.2f}s)")
        else:
            self.logger.error(f"Failed: {self.operation} (took {duration:.2f}s)", exc_info=True)
        
        return False  # Don't suppress exceptions


# Note: Automatic initialization removed to avoid issues with multiple imports
# or testing scenarios. Call setup_logging() explicitly in your application's
# entry point (e.g., main(), __init__(), etc.)
