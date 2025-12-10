#!/usr/bin/env python3
"""
Tests for IPC Server MCP Integration

Tests the new MCP and log access handlers added to the IPC server
to enable VS Code Copilot integration.
"""

import pytest
import json
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Plugins/AdastreaDirector/Python')))


@pytest.fixture
def ipc_server():
    """Create an IPC server instance for testing."""
    from ipc_server import IPCServer
    server = IPCServer(enable_metrics=False)
    return server


@pytest.fixture
def mock_mcp_server():
    """Create a mock MCP server."""
    mock = MagicMock()
    mock.start.return_value = True
    mock.is_connected.return_value = True
    mock.get_server_info.return_value = {
        'name': 'TestMCP',
        'version': '1.0.0',
        'connected': True
    }
    mock.list_tools.return_value = [
        {'name': 'test_tool', 'description': 'Test tool'}
    ]
    mock.handle_tool_call.return_value = {
        'isError': False,
        'content': [{'type': 'text', 'text': 'Success'}]
    }
    return mock


class TestMCPHandlers:
    """Test suite for MCP integration handlers."""
    
    def test_mcp_connect_success(self, ipc_server, mock_mcp_server):
        """Test successful MCP connection."""
        with patch.object(ipc_server, '_get_mcp_server', return_value=mock_mcp_server):
            response = ipc_server._handle_mcp_connect("")
            
            assert response['status'] == 'success'
            assert response['connected'] is True
            assert 'project_info' in response
    
    def test_mcp_connect_failure(self, ipc_server):
        """Test MCP connection failure when server not available."""
        with patch.object(ipc_server, '_get_mcp_server', return_value=None):
            response = ipc_server._handle_mcp_connect("")
            
            assert response['status'] == 'error'
            assert 'MCP server not available' in response['error']
    
    def test_mcp_disconnect(self, ipc_server, mock_mcp_server):
        """Test MCP disconnection."""
        ipc_server._mcp_server = mock_mcp_server
        
        response = ipc_server._handle_mcp_disconnect("")
        
        assert response['status'] == 'success'
        assert ipc_server._mcp_server is None
    
    def test_mcp_status_connected(self, ipc_server, mock_mcp_server):
        """Test MCP status when connected."""
        ipc_server._mcp_server = mock_mcp_server
        
        response = ipc_server._handle_mcp_status("")
        
        assert response['status'] == 'success'
        assert response['connected'] is True
        assert 'server_info' in response
    
    def test_mcp_status_not_connected(self, ipc_server):
        """Test MCP status when not connected."""
        response = ipc_server._handle_mcp_status("")
        
        assert response['status'] == 'success'
        assert response['connected'] is False
    
    def test_mcp_execute_python_success(self, ipc_server, mock_mcp_server):
        """Test Python execution via MCP."""
        ipc_server._mcp_server = mock_mcp_server
        
        with patch.object(ipc_server, '_get_mcp_server', return_value=mock_mcp_server):
            request_data = json.dumps({'code': 'print("test")'})
            response = ipc_server._handle_mcp_execute_python(request_data)
            
            assert response['status'] == 'success'
            assert 'result' in response
    
    def test_mcp_execute_python_no_code(self, ipc_server, mock_mcp_server):
        """Test Python execution with no code."""
        with patch.object(ipc_server, '_get_mcp_server', return_value=mock_mcp_server):
            request_data = json.dumps({'code': ''})
            response = ipc_server._handle_mcp_execute_python(request_data)
            
            assert response['status'] == 'error'
            assert 'No code provided' in response['error']
    
    def test_mcp_execute_python_not_connected(self, ipc_server):
        """Test Python execution when not connected."""
        mock = MagicMock()
        mock.is_connected.return_value = False
        
        with patch.object(ipc_server, '_get_mcp_server', return_value=mock):
            request_data = json.dumps({'code': 'print("test")'})
            response = ipc_server._handle_mcp_execute_python(request_data)
            
            assert response['status'] == 'error'
            assert 'Not connected' in response['error']
    
    def test_mcp_console_command_success(self, ipc_server, mock_mcp_server):
        """Test console command execution via MCP."""
        ipc_server._mcp_server = mock_mcp_server
        
        with patch.object(ipc_server, '_get_mcp_server', return_value=mock_mcp_server):
            request_data = json.dumps({'command': 'stat fps'})
            response = ipc_server._handle_mcp_console_command(request_data)
            
            assert response['status'] == 'success'
            assert 'result' in response
    
    def test_mcp_list_tools(self, ipc_server, mock_mcp_server):
        """Test listing MCP tools."""
        with patch.object(ipc_server, '_get_mcp_server', return_value=mock_mcp_server):
            response = ipc_server._handle_mcp_list_tools("")
            
            assert response['status'] == 'success'
            assert 'tools' in response
            assert len(response['tools']) > 0
    
    def test_mcp_call_tool_success(self, ipc_server, mock_mcp_server):
        """Test generic tool call via MCP."""
        ipc_server._mcp_server = mock_mcp_server
        
        with patch.object(ipc_server, '_get_mcp_server', return_value=mock_mcp_server):
            request_data = json.dumps({
                'tool': 'editor_list_assets',
                'arguments': {}
            })
            response = ipc_server._handle_mcp_call_tool(request_data)
            
            assert response['status'] == 'success'
            assert 'result' in response
    
    def test_mcp_call_tool_no_tool_name(self, ipc_server, mock_mcp_server):
        """Test tool call with no tool name."""
        with patch.object(ipc_server, '_get_mcp_server', return_value=mock_mcp_server):
            request_data = json.dumps({'tool': '', 'arguments': {}})
            response = ipc_server._handle_mcp_call_tool(request_data)
            
            assert response['status'] == 'error'
            assert 'No tool name provided' in response['error']


class TestLogAccessHandlers:
    """Test suite for UE log access handlers."""
    
    @patch('ue_log_capture.UELogCapture')
    def test_get_ue_logs_success(self, mock_capture_class, ipc_server):
        """Test getting UE log list."""
        # Mock log capture
        mock_capture = Mock()
        mock_log = Mock()
        mock_log.name = 'test.log'
        mock_log.stat.return_value.st_size = 1024
        mock_log.stat.return_value.st_mtime = 1234567890
        mock_log.__str__ = lambda self: '/path/to/test.log'
        
        mock_capture.list_log_files.return_value = [mock_log]
        mock_capture_class.return_value = mock_capture
        
        response = ipc_server._handle_get_ue_logs("")
        
        assert response['status'] == 'success'
        assert 'logs' in response
        assert response['count'] == 1
    
    @patch('ue_log_capture.UELogCapture')
    def test_list_ue_logs(self, mock_capture_class, ipc_server):
        """Test listing UE logs (alias for get_ue_logs)."""
        mock_capture = Mock()
        mock_capture.list_log_files.return_value = []
        mock_capture_class.return_value = mock_capture
        
        response = ipc_server._handle_list_ue_logs("")
        
        assert response['status'] == 'success'
        assert 'logs' in response
    
    @patch('ue_log_capture.UELogCapture')
    def test_read_ue_log_success(self, mock_capture_class, ipc_server, tmp_path):
        """Test reading a specific UE log file."""
        # Create a test log file
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        log_file = log_dir / "test.log"
        log_file.write_text("Test log content\n")
        
        # Mock log capture
        mock_capture = Mock()
        mock_capture.log_dir = log_dir
        mock_capture_class.return_value = mock_capture
        
        request_data = json.dumps({'filename': 'test.log'})
        response = ipc_server._handle_read_ue_log(request_data)
        
        assert response['status'] == 'success'
        assert 'content' in response
        assert 'Test log content' in response['content']
    
    @patch('ue_log_capture.UELogCapture')
    def test_read_ue_log_not_found(self, mock_capture_class, ipc_server, tmp_path):
        """Test reading non-existent log file."""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        
        mock_capture = Mock()
        mock_capture.log_dir = log_dir
        mock_capture_class.return_value = mock_capture
        
        request_data = json.dumps({'filename': 'nonexistent.log'})
        response = ipc_server._handle_read_ue_log(request_data)
        
        assert response['status'] == 'error'
        assert 'not found' in response['error']
    
    @patch('ue_log_capture.UELogCapture')
    def test_read_ue_log_no_filename(self, mock_capture_class, ipc_server):
        """Test reading log with no filename provided."""
        request_data = json.dumps({})
        response = ipc_server._handle_read_ue_log(request_data)
        
        assert response['status'] == 'error'
        assert 'No filename or path provided' in response['error']
    
    @patch('ue_log_capture.UELogCapture')
    def test_read_ue_log_security_check(self, mock_capture_class, ipc_server, tmp_path):
        """Test that reading logs outside the logs directory is blocked."""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        
        # Try to access a file outside logs directory
        outside_file = tmp_path / "outside.log"
        outside_file.write_text("Secret content")
        
        mock_capture = Mock()
        mock_capture.log_dir = log_dir
        mock_capture_class.return_value = mock_capture
        
        request_data = json.dumps({'path': str(outside_file)})
        response = ipc_server._handle_read_ue_log(request_data)
        
        assert response['status'] == 'error'
        assert 'Access denied' in response['error']


class TestHandlerRegistration:
    """Test that all new handlers are properly registered."""
    
    def test_mcp_handlers_registered(self, ipc_server):
        """Test that all MCP handlers are registered."""
        assert 'mcp_connect' in ipc_server.handlers
        assert 'mcp_disconnect' in ipc_server.handlers
        assert 'mcp_status' in ipc_server.handlers
        assert 'mcp_execute_python' in ipc_server.handlers
        assert 'mcp_console_command' in ipc_server.handlers
        assert 'mcp_list_tools' in ipc_server.handlers
        assert 'mcp_call_tool' in ipc_server.handlers
    
    def test_log_handlers_registered(self, ipc_server):
        """Test that all log handlers are registered."""
        assert 'get_ue_logs' in ipc_server.handlers
        assert 'list_ue_logs' in ipc_server.handlers
        assert 'read_ue_log' in ipc_server.handlers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
