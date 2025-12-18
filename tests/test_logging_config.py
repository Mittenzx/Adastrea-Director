"""
Tests for logging_config module.

These tests verify that the logging infrastructure works correctly,
including log file creation, formatting, rotation, and context management.
"""

import pytest
import logging
import tempfile
import time
from pathlib import Path
from logging_config import (
    setup_logging,
    get_logger,
    log_exception,
    log_debug_info,
    LogContext,
)


@pytest.fixture
def temp_log_dir(tmp_path):
    """Create a temporary directory for log files."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return log_dir


@pytest.fixture
def clean_logging():
    """Clean up logging handlers after each test."""
    yield
    # Remove all handlers from root logger
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)


def test_setup_logging_creates_log_file(temp_log_dir, clean_logging):
    """Test that setup_logging creates a log file."""
    setup_logging(debug=False, log_dir=temp_log_dir, console=False)
    
    # Check that log file was created
    log_files = list(temp_log_dir.glob("adastrea_*.log"))
    assert len(log_files) == 1, "Expected one log file to be created"
    
    # Verify file is not empty
    logger = get_logger("test")
    logger.info("Test message")
    
    log_file = log_files[0]
    assert log_file.stat().st_size > 0, "Log file should not be empty"


def test_setup_logging_debug_mode(temp_log_dir, clean_logging):
    """Test that debug mode sets DEBUG level."""
    setup_logging(debug=True, log_dir=temp_log_dir, console=False)
    
    root_logger = logging.getLogger()
    assert root_logger.level == logging.DEBUG, "Debug mode should set DEBUG level"


def test_setup_logging_normal_mode(temp_log_dir, clean_logging):
    """Test that normal mode sets INFO level."""
    setup_logging(debug=False, log_dir=temp_log_dir, console=False)
    
    root_logger = logging.getLogger()
    assert root_logger.level == logging.INFO, "Normal mode should set INFO level"


def test_get_logger_returns_logger(clean_logging):
    """Test that get_logger returns a valid logger."""
    logger = get_logger("test_module")
    assert isinstance(logger, logging.Logger), "Should return a Logger instance"
    assert logger.name == "test_module", "Logger should have correct name"


def test_logging_writes_to_file(temp_log_dir, clean_logging):
    """Test that log messages are written to file."""
    setup_logging(debug=True, log_dir=temp_log_dir, console=False)
    logger = get_logger("test")
    
    test_message = "Test log message with unique content"
    logger.info(test_message)
    
    # Force flush by getting the handler
    for handler in logging.getLogger().handlers:
        handler.flush()
    
    log_files = list(temp_log_dir.glob("adastrea_*.log"))
    assert len(log_files) == 1
    
    log_content = log_files[0].read_text()
    assert test_message in log_content, "Log message should be in file"


def test_log_levels(temp_log_dir, clean_logging):
    """Test that different log levels work correctly."""
    setup_logging(debug=True, log_dir=temp_log_dir, console=False)
    logger = get_logger("test")
    
    # Log messages at different levels
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    # Force flush
    for handler in logging.getLogger().handlers:
        handler.flush()
    
    log_files = list(temp_log_dir.glob("adastrea_*.log"))
    log_content = log_files[0].read_text()
    
    assert "DEBUG" in log_content
    assert "INFO" in log_content
    assert "WARNING" in log_content
    assert "ERROR" in log_content


def test_log_exception(temp_log_dir, clean_logging):
    """Test exception logging with traceback."""
    setup_logging(debug=True, log_dir=temp_log_dir, console=False)
    logger = get_logger("test")
    
    try:
        raise ValueError("Test exception")
    except Exception:
        log_exception(logger, "Caught test exception")
    
    # Force flush
    for handler in logging.getLogger().handlers:
        handler.flush()
    
    log_files = list(temp_log_dir.glob("adastrea_*.log"))
    log_content = log_files[0].read_text()
    
    assert "Caught test exception" in log_content
    assert "ValueError: Test exception" in log_content
    assert "Traceback" in log_content


def test_log_debug_info(temp_log_dir, clean_logging):
    """Test debug info logging with key-value pairs."""
    setup_logging(debug=True, log_dir=temp_log_dir, console=False)
    logger = get_logger("test")
    
    log_debug_info(logger, "Test context", key1="value1", key2="value2")
    
    # Force flush
    for handler in logging.getLogger().handlers:
        handler.flush()
    
    log_files = list(temp_log_dir.glob("adastrea_*.log"))
    log_content = log_files[0].read_text()
    
    assert "Test context" in log_content
    assert "key1=value1" in log_content
    assert "key2=value2" in log_content


def test_log_context_success(temp_log_dir, clean_logging):
    """Test LogContext for successful operations."""
    setup_logging(debug=True, log_dir=temp_log_dir, console=False)
    logger = get_logger("test")
    
    with LogContext(logger, "Test operation"):
        time.sleep(0.01)  # Small delay to measure timing
    
    # Force flush
    for handler in logging.getLogger().handlers:
        handler.flush()
    
    log_files = list(temp_log_dir.glob("adastrea_*.log"))
    log_content = log_files[0].read_text()
    
    assert "Starting: Test operation" in log_content
    assert "Completed: Test operation" in log_content
    assert "took" in log_content.lower()


def test_log_context_with_exception(temp_log_dir, clean_logging):
    """Test LogContext when an exception occurs."""
    setup_logging(debug=True, log_dir=temp_log_dir, console=False)
    logger = get_logger("test")
    
    with pytest.raises(ValueError):
        with LogContext(logger, "Failing operation"):
            raise ValueError("Test error")
    
    # Force flush
    for handler in logging.getLogger().handlers:
        handler.flush()
    
    log_files = list(temp_log_dir.glob("adastrea_*.log"))
    log_content = log_files[0].read_text()
    
    assert "Starting: Failing operation" in log_content
    assert "Failed: Failing operation" in log_content


def test_log_format_includes_timestamp(temp_log_dir, clean_logging):
    """Test that log format includes timestamp."""
    setup_logging(debug=False, log_dir=temp_log_dir, console=False)
    logger = get_logger("test")
    
    logger.info("Test message")
    
    # Force flush
    for handler in logging.getLogger().handlers:
        handler.flush()
    
    log_files = list(temp_log_dir.glob("adastrea_*.log"))
    log_content = log_files[0].read_text()
    
    # Check for timestamp format YYYY-MM-DD HH:MM:SS
    import re
    timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
    assert re.search(timestamp_pattern, log_content), "Log should include timestamp"


def test_log_format_includes_module_name(temp_log_dir, clean_logging):
    """Test that log format includes module name."""
    setup_logging(debug=False, log_dir=temp_log_dir, console=False)
    logger = get_logger("test.module")
    
    logger.info("Test message")
    
    # Force flush
    for handler in logging.getLogger().handlers:
        handler.flush()
    
    log_files = list(temp_log_dir.glob("adastrea_*.log"))
    log_content = log_files[0].read_text()
    
    assert "test.module" in log_content, "Log should include module name"


def test_multiple_loggers_same_file(temp_log_dir, clean_logging):
    """Test that multiple loggers write to the same file."""
    setup_logging(debug=True, log_dir=temp_log_dir, console=False)
    
    logger1 = get_logger("module1")
    logger2 = get_logger("module2")
    
    logger1.info("Message from module1")
    logger2.info("Message from module2")
    
    # Force flush
    for handler in logging.getLogger().handlers:
        handler.flush()
    
    log_files = list(temp_log_dir.glob("adastrea_*.log"))
    assert len(log_files) == 1, "All loggers should write to same file"
    
    log_content = log_files[0].read_text()
    assert "module1" in log_content
    assert "module2" in log_content


def test_console_logging_disabled(temp_log_dir, clean_logging, capsys):
    """Test that console logging can be disabled."""
    setup_logging(debug=False, log_dir=temp_log_dir, console=False)
    logger = get_logger("test")
    
    logger.info("Test message")
    
    captured = capsys.readouterr()
    assert "Test message" not in captured.out, "Message should not appear in console"


def test_third_party_loggers_suppressed(temp_log_dir, clean_logging):
    """Test that noisy third-party loggers are suppressed."""
    setup_logging(debug=True, log_dir=temp_log_dir, console=False)
    
    # Check that third-party loggers have higher log level
    chromadb_logger = logging.getLogger("chromadb")
    assert chromadb_logger.level >= logging.WARNING, "chromadb logger should be suppressed"
    
    urllib3_logger = logging.getLogger("urllib3")
    assert urllib3_logger.level >= logging.WARNING, "urllib3 logger should be suppressed"


def test_custom_log_file_name(temp_log_dir, clean_logging):
    """Test that custom log file name works."""
    custom_name = "custom_test.log"
    setup_logging(debug=False, log_file=custom_name, log_dir=temp_log_dir, console=False)
    
    logger = get_logger("test")
    logger.info("Test message")
    
    # Force flush
    for handler in logging.getLogger().handlers:
        handler.flush()
    
    log_file = temp_log_dir / custom_name
    assert log_file.exists(), "Custom log file should be created"
    assert log_file.stat().st_size > 0, "Custom log file should have content"
