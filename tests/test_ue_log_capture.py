#!/usr/bin/env python3
"""
Tests for UE Log Capture Module

Tests the functionality of the ue_log_capture module to ensure
logs are properly captured, formatted, and saved.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from ue_log_capture import UELogCapture, get_global_capture


@pytest.fixture
def temp_log_dir():
    """Create a temporary directory for log files."""
    temp_dir = tempfile.mkdtemp(prefix="ue_logs_test_")
    yield temp_dir
    # Cleanup after test
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def log_capture(temp_log_dir):
    """Create a UELogCapture instance with a temporary directory."""
    return UELogCapture(log_dir=temp_log_dir)


class TestUELogCapture:
    """Test suite for UELogCapture class."""
    
    def test_initialization(self, temp_log_dir):
        """Test that UELogCapture initializes correctly."""
        capture = UELogCapture(log_dir=temp_log_dir)
        assert capture.log_dir == Path(temp_log_dir)
        assert capture.log_dir.exists()
        assert capture._current_log_file is None
        assert capture._current_log_path is None
    
    def test_start_session_creates_log_file(self, log_capture, temp_log_dir):
        """Test that starting a session creates a log file."""
        log_path = log_capture.start_session()
        
        assert log_path is not None
        assert log_path.exists()
        assert log_path.parent == Path(temp_log_dir)
        assert log_path.name.startswith("ue_output_")
        assert log_path.name.endswith(".log")
        
        log_capture.end_session()
    
    def test_start_session_with_custom_name(self, log_capture, temp_log_dir):
        """Test starting a session with a custom name."""
        custom_name = "test_session"
        log_path = log_capture.start_session(session_name=custom_name)
        
        assert custom_name in log_path.name
        assert log_path.name.startswith("ue_test_session_")
        
        log_capture.end_session()
    
    def test_log_writes_content(self, log_capture):
        """Test that log() writes content to the file."""
        log_path = log_capture.start_session()
        
        test_content = "Test log message"
        log_capture.log(test_content, source="Test", level="INFO")
        
        log_capture.end_session()
        
        # Read and verify
        with open(log_path, 'r') as f:
            content = f.read()
            assert test_content in content
            assert "[INFO]" in content
            assert "[Test]" in content
    
    def test_log_python_execution(self, log_capture):
        """Test logging Python code execution."""
        log_path = log_capture.start_session()
        
        code = "import unreal\nprint('test')"
        output = "test output"
        error = ""
        
        log_capture.log_python_execution(code, output, error)
        log_capture.end_session()
        
        # Verify content
        with open(log_path, 'r') as f:
            content = f.read()
            assert "Python Code Executed:" in content
            assert code in content
            assert output in content
            assert "```python" in content
    
    def test_log_console_command(self, log_capture):
        """Test logging console commands."""
        log_path = log_capture.start_session()
        
        command = "stat fps"
        output = "FPS: 60.00"
        
        log_capture.log_console_command(command, output)
        log_capture.end_session()
        
        # Verify content
        with open(log_path, 'r') as f:
            content = f.read()
            assert "Console Command:" in content
            assert command in content
            assert output in content
    
    def test_log_tool_execution(self, log_capture):
        """Test logging MCP tool execution."""
        log_path = log_capture.start_session()
        
        tool_name = "editor_list_assets"
        parameters = {"filter": "Blueprints"}
        result = "Found 42 assets"
        
        log_capture.log_tool_execution(tool_name, parameters, result)
        log_capture.end_session()
        
        # Verify content
        with open(log_path, 'r') as f:
            content = f.read()
            assert tool_name in content
            assert "Parameters:" in content
            assert "filter" in content
            assert result in content
    
    def test_end_session_closes_file(self, log_capture):
        """Test that ending a session properly closes the file."""
        log_path = log_capture.start_session()
        log_capture.log("Test message", source="Test")
        
        log_capture.end_session()
        
        # Verify file is closed
        assert log_capture._current_log_file is None
        assert log_capture._current_log_path is None
        
        # File should be readable (not locked)
        with open(log_path, 'r') as f:
            content = f.read()
            assert "Session Ended:" in content
            assert "Duration:" in content
    
    def test_context_manager(self, temp_log_dir):
        """Test using UELogCapture as a context manager."""
        capture = UELogCapture(log_dir=temp_log_dir)
        
        with capture:
            log_path = capture.get_current_log_path()
            assert log_path is not None
            capture.log("Context manager test", source="Test")
        
        # Session should be ended after context
        assert capture._current_log_file is None
        
        # Log file should exist and contain content
        assert log_path.exists()
        with open(log_path, 'r') as f:
            content = f.read()
            assert "Context manager test" in content
    
    def test_multiple_sessions(self, log_capture):
        """Test creating multiple sessions."""
        # First session
        log_path1 = log_capture.start_session("session1")
        log_capture.log("First session", source="Test")
        log_capture.end_session()
        
        # Second session
        log_path2 = log_capture.start_session("session2")
        log_capture.log("Second session", source="Test")
        log_capture.end_session()
        
        assert log_path1 != log_path2
        assert log_path1.exists()
        assert log_path2.exists()
        
        # Verify content
        with open(log_path1, 'r') as f:
            assert "First session" in f.read()
        with open(log_path2, 'r') as f:
            assert "Second session" in f.read()
    
    def test_list_log_files(self, log_capture):
        """Test listing log files."""
        # Create multiple log files
        for i in range(5):
            log_capture.start_session(f"test_{i}")
            log_capture.log(f"Log entry {i}", source="Test")
            log_capture.end_session()
        
        # List files
        log_files = log_capture.list_log_files(limit=3)
        
        assert len(log_files) == 3
        assert all(isinstance(f, Path) for f in log_files)
        assert all(f.name.startswith("ue_") for f in log_files)
    
    def test_log_without_session(self, log_capture, caplog):
        """Test that logging without a session logs a warning."""
        # Try to log without starting a session
        log_capture.log("Test message", source="Test")
        
        # Should not raise an error, but should log a warning
        assert "No active log session" in caplog.text
    
    def test_header_format(self, log_capture):
        """Test that the log header is properly formatted."""
        log_path = log_capture.start_session()
        log_capture.end_session()
        
        with open(log_path, 'r') as f:
            content = f.read()
            assert "Unreal Engine Output Log" in content
            assert "Session Started:" in content
            assert "Captured by: Adastrea Director" in content
            assert "=" * 80 in content
    
    def test_file_creation_error_handling(self, temp_log_dir):
        """Test error handling when file creation fails."""
        import os
        
        # Create a read-only directory
        readonly_dir = os.path.join(temp_log_dir, "readonly")
        os.makedirs(readonly_dir, mode=0o444)
        
        capture = UELogCapture(log_dir=readonly_dir)
        
        # Should raise RuntimeError when trying to create file
        with pytest.raises(RuntimeError):
            capture.start_session()
        
        # Cleanup
        os.chmod(readonly_dir, 0o755)
    
    def test_list_log_files_with_deleted_files(self, log_capture):
        """Test that list_log_files handles deleted files gracefully."""
        # Create some log files
        log_paths = []
        for i in range(3):
            log_path = log_capture.start_session(f"test_{i}")
            log_paths.append(log_path)
            log_capture.end_session()
        
        # Delete one of the files
        if log_paths:
            log_paths[1].unlink()
        
        # Should still return remaining files without error
        log_files = log_capture.list_log_files()
        assert len(log_files) >= 2  # At least 2 files should remain


class TestGlobalCapture:
    """Test suite for global capture functions."""
    
    def test_get_global_capture(self):
        """Test getting the global capture instance."""
        capture1 = get_global_capture()
        capture2 = get_global_capture()
        
        # Should return the same instance
        assert capture1 is capture2
    
    def test_global_capture_functions(self, temp_log_dir):
        """Test global capture helper functions."""
        from ue_log_capture import start_capture, log_output, end_capture
        
        # Get global instance and set log dir
        capture = get_global_capture()
        capture.log_dir = Path(temp_log_dir)
        capture.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Use global functions
        log_path = start_capture("global_test")
        log_output("Global test message", source="Test", level="INFO")
        end_capture()
        
        # Verify
        assert log_path.exists()
        with open(log_path, 'r') as f:
            content = f.read()
            assert "Global test message" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
