#!/usr/bin/env python3
"""
Unreal Engine Log Capture Module

This module provides functionality to capture, save, and manage logs from
Unreal Engine operations. Logs are saved to dated files for agent processing
and historical analysis.

Features:
- Automatic log file creation with timestamps
- Thread-safe log writing
- Log rotation support
- Formatted output with timestamps
- Integration with GUI and MCP systems
"""

import os
import threading
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, TextIO, List
import logging

logger = logging.getLogger(__name__)


class UELogCapture:
    """
    Captures and saves Unreal Engine output logs to dated files.
    
    This class provides thread-safe logging of UE output from various sources
    (MCP, remote control, plugin IPC) to timestamped log files. The logs can
    be processed by AI agents for problem detection and improvement suggestions.
    
    Example:
        ```python
        capture = UELogCapture()
        capture.start_session()
        capture.log("Python execution output", source="MCP")
        capture.log("Console command result", source="Console")
        capture.end_session()
        ```
    """
    
    def __init__(self, log_dir: Optional[str] = None):
        """
        Initialize the UE log capture system.
        
        Args:
            log_dir: Directory to store log files. Defaults to './logs'
        """
        # Determine log directory
        if log_dir is None:
            script_dir = Path(__file__).parent
            log_dir = script_dir / "logs"
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Current session state
        self._current_log_file: Optional[TextIO] = None
        self._current_log_path: Optional[Path] = None
        self._session_start_time: Optional[datetime] = None
        self._lock = threading.Lock()
        
        logger.info(f"UELogCapture initialized with log_dir: {self.log_dir}")
    
    def start_session(self, session_name: Optional[str] = None) -> Path:
        """
        Start a new logging session.
        
        Creates a new log file with a timestamp. If a session is already
        active, it will be ended first.
        
        Args:
            session_name: Optional custom name for the session.
                         If None, uses default format: ue_output_YYYY-MM-DD_HH-MM-SS.log
        
        Returns:
            Path to the created log file.
        """
        with self._lock:
            # End any existing session
            if self._current_log_file is not None:
                self.end_session()
            
            # Generate log file name
            self._session_start_time = datetime.now()
            timestamp = self._session_start_time.strftime("%Y-%m-%d_%H-%M-%S")
            
            if session_name:
                filename = f"ue_{session_name}_{timestamp}.log"
            else:
                filename = f"ue_output_{timestamp}.log"
            
            self._current_log_path = self.log_dir / filename
            
            # Open log file with error handling
            try:
                self._current_log_file = open(self._current_log_path, 'w', encoding='utf-8')
            except (OSError, IOError) as e:
                logger.error(f"Failed to create log file {self._current_log_path}: {e}")
                self._current_log_path = None
                self._current_log_file = None
                self._session_start_time = None
                raise RuntimeError(f"Could not create log file: {e}") from e
            
            # Write header
            self._write_header()
            
            logger.info(f"Started UE log capture session: {self._current_log_path}")
            return self._current_log_path
    
    def _write_header(self):
        """Write session header to the log file."""
        if self._current_log_file and self._session_start_time:
            header = [
                "=" * 80,
                "Unreal Engine Output Log",
                f"Session Started: {self._session_start_time.strftime('%Y-%m-%d %H:%M:%S')}",
                "Captured by: Adastrea Director",
                "=" * 80,
                ""
            ]
            self._current_log_file.write("\n".join(header) + "\n")
            self._current_log_file.flush()
    
    def log(self, content: str, source: str = "Unknown", level: str = "INFO"):
        """
        Log content to the current session file.
        
        Args:
            content: The content to log (e.g., UE output, command result)
            source: Source of the log (e.g., "MCP", "Console", "Plugin")
            level: Log level (e.g., "INFO", "WARNING", "ERROR")
        """
        with self._lock:
            if self._current_log_file is None:
                logger.warning("No active log session. Call start_session() first.")
                return
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            
            # Format log entry
            log_entry = [
                f"[{timestamp}] [{level}] [{source}]",
                content,
                "-" * 80,
                ""
            ]
            
            self._current_log_file.write("\n".join(log_entry) + "\n")
            self._current_log_file.flush()
    
    def log_python_execution(self, code: str, output: str, error: str = ""):
        """
        Log Python code execution in UE.
        
        Args:
            code: The Python code that was executed
            output: Standard output from the execution
            error: Error output if any
        """
        content_parts = [
            "Python Code Executed:",
            "```python",
            code,
            "```",
            ""
        ]
        
        if output:
            content_parts.extend([
                "Output:",
                output,
                ""
            ])
        
        if error:
            content_parts.extend([
                "Errors:",
                error,
                ""
            ])
        
        level = "ERROR" if error else "INFO"
        self.log("\n".join(content_parts), source="MCP-Python", level=level)
    
    def log_console_command(self, command: str, output: str):
        """
        Log console command execution in UE.
        
        Args:
            command: The console command that was executed
            output: Output from the command
        """
        content = [
            f"Console Command: {command}",
            "",
            "Output:",
            output
        ]
        
        self.log("\n".join(content), source="Console", level="INFO")
    
    def log_tool_execution(self, tool_name: str, parameters: dict, result: str):
        """
        Log MCP tool execution.
        
        Args:
            tool_name: Name of the MCP tool
            parameters: Parameters passed to the tool
            result: Result from the tool execution
        """
        content = [
            f"Tool: {tool_name}",
            "",
            "Parameters:",
            json.dumps(parameters, indent=2),
            "",
            "Result:",
            result
        ]
        
        self.log("\n".join(content), source="MCP-Tool", level="INFO")
    
    def end_session(self):
        """
        End the current logging session.
        
        Writes a footer and closes the log file.
        """
        with self._lock:
            if self._current_log_file is None:
                return
            
            # Write footer
            end_time = datetime.now()
            duration = end_time - self._session_start_time if self._session_start_time else None
            
            footer = [
                "",
                "=" * 80,
                f"Session Ended: {end_time.strftime('%Y-%m-%d %H:%M:%S')}",
            ]
            
            if duration:
                footer.append(f"Duration: {duration}")
            
            footer.extend([
                "=" * 80,
                ""
            ])
            
            # Write footer and close file with error handling
            try:
                self._current_log_file.write("\n".join(footer) + "\n")
                self._current_log_file.flush()
            except (OSError, IOError) as e:
                logger.error(f"Failed to write footer to log file: {e}")
            finally:
                # Always try to close the file, even if writing failed
                try:
                    self._current_log_file.close()
                except Exception as e:
                    logger.error(f"Failed to close log file: {e}")
            
            logger.info(f"Ended UE log capture session: {self._current_log_path}")
            
            self._current_log_file = None
            self._current_log_path = None
            self._session_start_time = None
    
    def get_current_log_path(self) -> Optional[Path]:
        """
        Get the path to the current log file.
        
        Returns:
            Path to current log file, or None if no session is active.
        """
        with self._lock:
            return self._current_log_path
    
    def list_log_files(self, limit: int = 10) -> List[Path]:
        """
        List recent log files.
        
        Args:
            limit: Maximum number of log files to return
        
        Returns:
            List of Path objects for log files, sorted by modification time (newest first)
        """
        log_files = list(self.log_dir.glob("ue_*.log"))
        
        # Sort by modification time with error handling
        def safe_mtime(p: Path) -> float:
            try:
                return p.stat().st_mtime
            except (OSError, IOError) as e:
                logger.warning(f"Could not stat log file {p}: {e}")
                return 0.0
        
        log_files.sort(key=safe_mtime, reverse=True)
        return log_files[:limit]
    
    def __enter__(self):
        """Context manager entry - starts a session."""
        self.start_session()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ends the session."""
        self.end_session()
        return False


# Global instance for easy access across the application
# Note: This singleton pattern is intentional for this use case as we typically
# want a single log capture instance shared across all UE operations in the GUI.
# For testing or advanced use cases, create separate UELogCapture instances directly.
_global_capture: Optional[UELogCapture] = None


def get_global_capture() -> UELogCapture:
    """
    Get or create the global UELogCapture instance.
    
    This provides a convenient singleton for simple use cases where you want
    all UE operations to log to the same capture instance. For more control
    or testing scenarios, create UELogCapture instances directly.
    
    Returns:
        Global UELogCapture instance.
    """
    global _global_capture
    if _global_capture is None:
        _global_capture = UELogCapture()
    return _global_capture


def start_capture(session_name: Optional[str] = None) -> Path:
    """
    Start capturing UE logs using the global instance.
    
    Args:
        session_name: Optional custom session name
    
    Returns:
        Path to the log file
    """
    capture = get_global_capture()
    return capture.start_session(session_name)


def log_output(content: str, source: str = "Unknown", level: str = "INFO"):
    """
    Log content using the global capture instance.
    
    Args:
        content: Content to log
        source: Source of the log
        level: Log level
    """
    capture = get_global_capture()
    capture.log(content, source, level)


def end_capture():
    """End the current capture session using the global instance."""
    capture = get_global_capture()
    capture.end_session()


if __name__ == "__main__":
    # Demo usage
    print("UE Log Capture Demo")
    print("-" * 80)
    
    capture = UELogCapture()
    log_path = capture.start_session("demo")
    print(f"Started log session: {log_path}")
    
    # Simulate some UE operations
    capture.log_python_execution(
        code="import unreal\nprint(unreal.SystemLibrary.get_engine_version())",
        output="5.3.0-12345678",
        error=""
    )
    
    capture.log_console_command(
        command="stat fps",
        output="FPS: 60.00"
    )
    
    capture.log_tool_execution(
        tool_name="editor_list_assets",
        parameters={},
        result="Found 150 assets"
    )
    
    capture.end_session()
    print(f"Session ended. Log saved to: {log_path}")
    
    # List recent logs
    print("\nRecent log files:")
    for log_file in capture.list_log_files(5):
        print(f"  - {log_file.name}")
