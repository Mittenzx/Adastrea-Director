"""
Tests for the MCP Server remote execution module.
"""

import struct
from unittest.mock import Mock, patch, MagicMock

from mcp_server.remote_execution import (
    UnrealRemoteExecution,
    RemoteExecutionConfig,
    CommandResult,
    RemoteNode,
    MessageType,
    ExecutionMode,
)


class TestRemoteExecutionConfig:
    """Tests for RemoteExecutionConfig."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = RemoteExecutionConfig()
        
        assert config.multicast_group == "239.0.0.1"
        assert config.multicast_port == 6766
        assert config.bind_address == "0.0.0.0"
        assert config.command_timeout == 30.0
        assert config.discovery_timeout == 5.0
        assert config.max_retries == 3
        assert config.retry_delay == 2.0
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = RemoteExecutionConfig(
            multicast_group="239.0.0.2",
            multicast_port=7000,
            bind_address="127.0.0.1",
            command_timeout=60.0
        )
        
        assert config.multicast_group == "239.0.0.2"
        assert config.multicast_port == 7000
        assert config.bind_address == "127.0.0.1"
        assert config.command_timeout == 60.0


class TestCommandResult:
    """Tests for CommandResult dataclass."""
    
    def test_success_result(self):
        """Test successful command result."""
        result = CommandResult(
            success=True,
            output="Hello, World!",
            error=""
        )
        
        assert result.success is True
        assert result.output == "Hello, World!"
        assert result.error == ""
        assert result.timestamp is not None
    
    def test_error_result(self):
        """Test error command result."""
        result = CommandResult(
            success=False,
            output="",
            error="Command failed"
        )
        
        assert result.success is False
        assert result.output == ""
        assert result.error == "Command failed"


class TestRemoteNode:
    """Tests for RemoteNode dataclass."""
    
    def test_node_creation(self):
        """Test creating a remote node."""
        node = RemoteNode(
            node_id="test-node-123",
            project_name="TestProject",
            address=("127.0.0.1", 6767)
        )
        
        assert node.node_id == "test-node-123"
        assert node.project_name == "TestProject"
        assert node.address == ("127.0.0.1", 6767)
        assert node.last_seen is not None


class TestUnrealRemoteExecution:
    """Tests for UnrealRemoteExecution class."""
    
    def test_initialization(self):
        """Test initialization with default config."""
        remote = UnrealRemoteExecution()
        
        assert remote.config is not None
        assert remote.config.multicast_group == "239.0.0.1"
        assert remote._running is False
        assert remote._connected_node is None
    
    def test_initialization_custom_config(self):
        """Test initialization with custom config."""
        config = RemoteExecutionConfig(
            multicast_port=7000,
            command_timeout=60.0
        )
        remote = UnrealRemoteExecution(config)
        
        assert remote.config.multicast_port == 7000
        assert remote.config.command_timeout == 60.0
    
    def test_is_connected_initially_false(self):
        """Test that is_connected returns False initially."""
        remote = UnrealRemoteExecution()
        
        assert remote.is_connected() is False
    
    def test_get_remote_nodes_empty(self):
        """Test that get_remote_nodes returns empty dict initially."""
        remote = UnrealRemoteExecution()
        
        nodes = remote.get_remote_nodes()
        assert nodes == {}
    
    def test_write_string(self):
        """Test string encoding."""
        remote = UnrealRemoteExecution()
        
        result = remote._write_string("hello")
        
        # Should be 4 bytes length + string
        assert len(result) == 4 + 5
        length = struct.unpack("<I", result[:4])[0]
        assert length == 5
        assert result[4:] == b"hello"
    
    def test_read_string(self):
        """Test string decoding."""
        remote = UnrealRemoteExecution()
        
        # Encode a string
        data = struct.pack("<I", 5) + b"hello" + b"extra"
        
        text, remaining = remote._read_string(data)
        
        assert text == "hello"
        assert remaining == b"extra"
    
    def test_read_string_empty(self):
        """Test reading from insufficient data."""
        remote = UnrealRemoteExecution()
        
        text, remaining = remote._read_string(b"ab")
        
        assert text == ""
        assert remaining == b"ab"
    
    def test_run_command_not_connected(self):
        """Test run_command returns error when not connected."""
        remote = UnrealRemoteExecution()
        
        result = remote.run_command("print('hello')")
        
        assert result.success is False
        assert "Not connected" in result.error
    
    def test_context_manager(self):
        """Test context manager protocol."""
        with patch.object(UnrealRemoteExecution, '_setup_discovery_socket'):
            with patch.object(UnrealRemoteExecution, '_start_discovery_thread'):
                with UnrealRemoteExecution() as remote:
                    assert remote._running is True
                
                assert remote._running is False
    
    def test_add_remove_command_listener(self):
        """Test adding and removing command listeners."""
        remote = UnrealRemoteExecution()
        listener = Mock()
        
        remote.add_command_listener(listener)
        assert listener in remote._command_listeners
        
        remote.remove_command_listener(listener)
        assert listener not in remote._command_listeners
    
    def test_remove_nonexistent_listener(self):
        """Test removing a listener that doesn't exist."""
        remote = UnrealRemoteExecution()
        listener = Mock()
        
        # Should not raise
        remote.remove_command_listener(listener)
    
    @patch('socket.socket')
    def test_start_stop(self, mock_socket_class):
        """Test start and stop lifecycle."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        remote = UnrealRemoteExecution()
        
        remote.start()
        assert remote._running is True
        
        remote.stop()
        assert remote._running is False
        assert remote._discovery_socket is None
        assert remote._command_socket is None
    
    def test_stop_when_not_running(self):
        """Test stopping when not running doesn't raise."""
        remote = UnrealRemoteExecution()
        
        # Should not raise
        remote.stop()
        assert remote._running is False


class TestUnrealRemoteExecutionConnection:
    """Tests for connection handling."""
    
    @patch('socket.socket')
    def test_open_command_connection_success(self, mock_socket_class):
        """Test successful command connection."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        remote = UnrealRemoteExecution()
        node = RemoteNode(
            node_id="test-node",
            project_name="TestProject",
            address=("127.0.0.1", 6766)
        )
        
        result = remote.open_command_connection(node)
        
        assert result is True
        assert remote._connected_node == node
        mock_socket.connect.assert_called_once()
    
    @patch('socket.socket')
    def test_open_command_connection_failure(self, mock_socket_class):
        """Test failed command connection."""
        mock_socket = MagicMock()
        mock_socket.connect.side_effect = ConnectionRefusedError("Connection refused")
        mock_socket_class.return_value = mock_socket
        
        remote = UnrealRemoteExecution()
        node = RemoteNode(
            node_id="test-node",
            project_name="TestProject",
            address=("127.0.0.1", 6766)
        )
        
        result = remote.open_command_connection(node)
        
        assert result is False
        assert remote._connected_node is None


class TestMessageParsing:
    """Tests for message parsing and handling."""
    
    def test_magic_constant(self):
        """Test magic constant is correct."""
        assert UnrealRemoteExecution.MAGIC == b"CYCB"
    
    def test_protocol_version(self):
        """Test protocol version is correct."""
        assert UnrealRemoteExecution.PROTOCOL_VERSION == 1
    
    def test_message_type_values(self):
        """Test message type enum values."""
        assert MessageType.PING == 0
        assert MessageType.PONG == 1
        assert MessageType.OPEN_CONNECTION == 2
        assert MessageType.CLOSE_CONNECTION == 3
        assert MessageType.COMMAND == 4
        assert MessageType.COMMAND_RESULT == 5
    
    def test_execution_mode_values(self):
        """Test execution mode enum values."""
        assert ExecutionMode.EXECUTE_FILE == 0
        assert ExecutionMode.EXECUTE_STATEMENT == 1
        assert ExecutionMode.EVALUATE_STATEMENT == 2
