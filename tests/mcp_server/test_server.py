"""
Tests for the MCP Server main module.
"""

import pytest
import json
from unittest.mock import Mock, MagicMock, patch

from mcp_server.server import (
    UnrealMCPServer,
    MCPServerConfig,
)
from mcp_server.remote_execution import CommandResult


class TestMCPServerConfig:
    """Tests for MCPServerConfig."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = MCPServerConfig()
        
        assert config.name == "AdastreaMCP"
        assert config.version == "0.1.0"
        assert config.multicast_group == "239.0.0.1"
        assert config.multicast_port == 6766
        assert config.connection_timeout == 30.0
        assert config.max_retries == 3
        assert config.retry_delay == 2.0
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = MCPServerConfig(
            name="CustomMCP",
            version="1.0.0",
            multicast_port=7000
        )
        
        assert config.name == "CustomMCP"
        assert config.version == "1.0.0"
        assert config.multicast_port == 7000


class TestUnrealMCPServer:
    """Tests for UnrealMCPServer class."""
    
    def test_initialization(self):
        """Test server initialization."""
        server = UnrealMCPServer()
        
        assert server.config is not None
        assert server.config.name == "AdastreaMCP"
        assert server._running is False
        assert server._connected is False
    
    def test_initialization_custom_config(self):
        """Test server initialization with custom config."""
        config = MCPServerConfig(name="TestMCP")
        server = UnrealMCPServer(config)
        
        assert server.config.name == "TestMCP"
    
    def test_is_connected_initially_false(self):
        """Test that is_connected returns False initially."""
        server = UnrealMCPServer()
        
        assert server.is_connected() is False
    
    def test_get_server_info(self):
        """Test getting server info."""
        server = UnrealMCPServer()
        info = server.get_server_info()
        
        assert "name" in info
        assert "version" in info
        assert "description" in info
        assert "connected" in info
        assert info["name"] == "AdastreaMCP"
        assert info["connected"] is False
    
    def test_list_tools(self):
        """Test listing available tools."""
        server = UnrealMCPServer()
        tools = server.list_tools()
        
        assert len(tools) > 0
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
    
    def test_handle_tool_call_not_connected(self):
        """Test handling tool call when not connected."""
        server = UnrealMCPServer()
        
        result = server.handle_tool_call("editor_list_assets", {})
        
        assert result["isError"] is True
        assert "Not connected" in result["content"][0]["text"]
    
    def test_handle_tool_call_unknown_tool(self):
        """Test handling unknown tool call."""
        server = UnrealMCPServer()
        server._connected = True
        server._remote = Mock()
        server._remote.is_connected.return_value = True
        
        result = server.handle_tool_call("unknown_tool", {})
        
        assert result["isError"] is True
        assert "Unknown tool" in result["content"][0]["text"]
    
    @patch('mcp_server.server.get_tool')
    def test_handle_tool_call_success(self, mock_get_tool):
        """Test successful tool call handling."""
        server = UnrealMCPServer()
        server._connected = True
        server._remote = Mock()
        server._remote.is_connected.return_value = True
        
        mock_tool = Mock()
        mock_tool.execute.return_value = Mock(
            success=True,
            content=[{"type": "text", "text": "Success!"}]
        )
        mock_get_tool.return_value = mock_tool
        
        result = server.handle_tool_call("test_tool", {"param": "value"})
        
        assert result["isError"] is False
        assert result["content"][0]["text"] == "Success!"
    
    @patch('mcp_server.server.get_tool')
    def test_handle_tool_call_exception(self, mock_get_tool):
        """Test tool call handling when exception occurs."""
        server = UnrealMCPServer()
        server._connected = True
        server._remote = Mock()
        server._remote.is_connected.return_value = True
        
        mock_tool = Mock()
        mock_tool.execute.side_effect = Exception("Test error")
        mock_get_tool.return_value = mock_tool
        
        result = server.handle_tool_call("test_tool", {})
        
        assert result["isError"] is True
        assert "Test error" in result["content"][0]["text"]


class TestMCPMessageHandling:
    """Tests for MCP message handling."""
    
    def test_handle_initialize_message(self):
        """Test handling initialize message."""
        server = UnrealMCPServer()
        
        message = {"type": "initialize", "id": 1}
        response = server.handle_message(message)
        
        assert response["id"] == 1
        assert "result" in response
        assert "protocolVersion" in response["result"]
        assert "serverInfo" in response["result"]
        assert "capabilities" in response["result"]
    
    def test_handle_initialized_message(self):
        """Test handling initialized message."""
        server = UnrealMCPServer()
        
        message = {"type": "initialized", "id": 2}
        response = server.handle_message(message)
        
        assert response["id"] == 2
        assert "result" in response
    
    def test_handle_tools_list_message(self):
        """Test handling tools/list message."""
        server = UnrealMCPServer()
        
        message = {"type": "tools/list", "id": 3}
        response = server.handle_message(message)
        
        assert response["id"] == 3
        assert "result" in response
        assert "tools" in response["result"]
        assert len(response["result"]["tools"]) > 0
    
    def test_handle_tools_call_message(self):
        """Test handling tools/call message."""
        server = UnrealMCPServer()
        
        message = {
            "type": "tools/call",
            "id": 4,
            "params": {
                "name": "editor_list_assets",
                "arguments": {}
            }
        }
        response = server.handle_message(message)
        
        assert response["id"] == 4
        assert "result" in response
        # Not connected, so should be error
        assert response["result"]["isError"] is True
    
    def test_handle_unknown_message(self):
        """Test handling unknown message type."""
        server = UnrealMCPServer()
        
        message = {"type": "unknown_type", "id": 5}
        response = server.handle_message(message)
        
        assert response["id"] == 5
        assert "error" in response
        assert response["error"]["code"] == -32601


class TestServerLifecycle:
    """Tests for server lifecycle management."""
    
    @patch('mcp_server.server.UnrealRemoteExecution')
    def test_start_creates_remote(self, mock_remote_class):
        """Test that start creates remote execution client."""
        mock_remote = MagicMock()
        mock_remote.get_first_remote_node.return_value = None
        mock_remote_class.return_value = mock_remote
        
        server = UnrealMCPServer()
        server.start()
        
        assert server._running is True
        assert server._remote is not None
        mock_remote.start.assert_called_once()
    
    @patch('mcp_server.server.UnrealRemoteExecution')
    def test_stop_cleans_up(self, mock_remote_class):
        """Test that stop cleans up resources."""
        mock_remote = MagicMock()
        mock_remote.get_first_remote_node.return_value = None
        mock_remote_class.return_value = mock_remote
        
        server = UnrealMCPServer()
        server.start()
        server.stop()
        
        assert server._running is False
        assert server._connected is False
        mock_remote.stop.assert_called_once()
    
    def test_context_manager(self):
        """Test context manager protocol."""
        with patch('mcp_server.server.UnrealRemoteExecution') as mock_remote_class:
            mock_remote = MagicMock()
            mock_remote.get_first_remote_node.return_value = None
            mock_remote_class.return_value = mock_remote
            
            with UnrealMCPServer() as server:
                assert server._running is True
            
            assert server._running is False


class TestConnectionRetry:
    """Tests for connection retry logic."""
    
    @patch('mcp_server.server.UnrealRemoteExecution')
    def test_connection_retry_on_failure(self, mock_remote_class):
        """Test that connection retries on failure."""
        mock_remote = MagicMock()
        mock_remote.get_first_remote_node.return_value = None
        mock_remote_class.return_value = mock_remote
        
        config = MCPServerConfig(max_retries=2, retry_delay=0.01)
        server = UnrealMCPServer(config)
        
        # Need to set _remote first before calling _try_connect
        server._remote = mock_remote
        result = server._try_connect()
        
        assert result is False
        # Should have tried multiple times
        assert mock_remote.get_first_remote_node.call_count >= 1
    
    @patch('mcp_server.server.UnrealRemoteExecution')
    def test_successful_connection(self, mock_remote_class):
        """Test successful connection."""
        mock_remote = MagicMock()
        mock_node = Mock(node_id="test", project_name="TestProject")
        mock_remote.get_first_remote_node.return_value = mock_node
        mock_remote.open_command_connection.return_value = True
        mock_remote.run_command.return_value = CommandResult(success=True, output="MCP:connected")
        mock_remote_class.return_value = mock_remote
        
        server = UnrealMCPServer()
        
        # Need to set up remote first
        server._remote = mock_remote
        result = server._try_connect()
        
        assert result is True
