"""
Tests for the MCP Server remote execution module.
"""

import json
import struct
from unittest.mock import Mock, patch, MagicMock

from mcp_server.remote_execution import (
    UnrealRemoteExecution,
    RemoteExecutionConfig,
    CommandResult,
    RemoteNode,
    RemoteNodeData,
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
        assert config.command_endpoint == ("127.0.0.1", 6776)
    
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
        node_data = RemoteNodeData(
            project_name="TestProject",
            engine_version="5.3",
            machine="test-machine"
        )
        node = RemoteNode(
            node_id="test-node-123",
            data=node_data
        )
        
        assert node.node_id == "test-node-123"
        assert node.project_name == "TestProject"
        assert node.data.engine_version == "5.3"
        assert node.last_seen is not None
    
    def test_node_project_name_property(self):
        """Test that project_name property works correctly."""
        node_data = RemoteNodeData(project_name="MyGame")
        node = RemoteNode(node_id="test", data=node_data)
        
        assert node.project_name == "MyGame"


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
        """Test string encoding (legacy method)."""
        remote = UnrealRemoteExecution()
        
        result = remote._write_string("hello")
        
        # Should be 4 bytes length + string
        assert len(result) == 4 + 5
        length = struct.unpack("<I", result[:4])[0]
        assert length == 5
        assert result[4:] == b"hello"
    
    def test_read_string(self):
        """Test string decoding (legacy method)."""
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
    
    def test_create_message(self):
        """Test JSON message creation."""
        remote = UnrealRemoteExecution()
        
        message = remote._create_message(MessageType.PING)
        parsed = json.loads(message)
        
        assert parsed["version"] == 1
        assert parsed["magic"] == "ue_py"
        assert parsed["type"] == "ping"
        assert parsed["source"] == remote._node_id
    
    def test_create_message_with_dest_and_data(self):
        """Test JSON message creation with destination and data."""
        remote = UnrealRemoteExecution()
        
        message = remote._create_message(
            MessageType.COMMAND,
            dest="target-node",
            data={"command": "print('test')"}
        )
        parsed = json.loads(message)
        
        assert parsed["dest"] == "target-node"
        assert parsed["data"]["command"] == "print('test')"
    
    def test_validate_message(self):
        """Test message validation."""
        remote = UnrealRemoteExecution()
        
        valid_message = {
            "version": 1,
            "magic": "ue_py",
            "type": "ping",
            "source": "some-node"
        }
        
        assert remote._validate_message(valid_message) is True
        
        # Invalid version
        invalid_version = {**valid_message, "version": 2}
        assert remote._validate_message(invalid_version) is False
        
        # Invalid magic
        invalid_magic = {**valid_message, "magic": "wrong"}
        assert remote._validate_message(invalid_magic) is False
    
    def test_passes_receive_filter(self):
        """Test receive filter logic."""
        remote = UnrealRemoteExecution()
        
        # Message from another node, no dest (broadcast)
        msg1 = {"source": "other-node"}
        assert remote._passes_receive_filter(msg1) is True
        
        # Message from ourselves
        msg2 = {"source": remote._node_id}
        assert remote._passes_receive_filter(msg2) is False
        
        # Message destined for us
        msg3 = {"source": "other-node", "dest": remote._node_id}
        assert remote._passes_receive_filter(msg3) is True
        
        # Message destined for someone else
        msg4 = {"source": "other-node", "dest": "different-node"}
        assert remote._passes_receive_filter(msg4) is False


class TestUnrealRemoteExecutionConnection:
    """Tests for connection handling."""
    
    @patch('socket.socket')
    def test_open_command_connection_timeout(self, mock_socket_class):
        """Test command connection timeout."""
        import socket as socket_module
        
        mock_server = MagicMock()
        mock_server.accept.side_effect = socket_module.timeout("timeout")
        mock_socket_class.return_value = mock_server
        
        remote = UnrealRemoteExecution()
        remote._discovery_socket = MagicMock()
        
        node_data = RemoteNodeData(project_name="TestProject")
        node = RemoteNode(node_id="test-node", data=node_data)
        
        result = remote.open_command_connection(node, timeout_ms=100)
        
        assert result is False
        assert remote._connected_node is None


class TestMessageParsing:
    """Tests for message parsing and handling."""
    
    def test_magic_constant(self):
        """Test magic constant is correct (JSON protocol uses string)."""
        assert UnrealRemoteExecution.MAGIC == "ue_py"
        assert UnrealRemoteExecution.PROTOCOL_MAGIC == "ue_py"
    
    def test_protocol_version(self):
        """Test protocol version is correct."""
        assert UnrealRemoteExecution.PROTOCOL_VERSION == 1
    
    def test_message_type_values(self):
        """Test message type values (now string-based)."""
        assert MessageType.PING == "ping"
        assert MessageType.PONG == "pong"
        assert MessageType.OPEN_CONNECTION == "open_connection"
        assert MessageType.CLOSE_CONNECTION == "close_connection"
        assert MessageType.COMMAND == "command"
        assert MessageType.COMMAND_RESULT == "command_result"
    
    def test_execution_mode_values(self):
        """Test execution mode values (now string-based)."""
        assert ExecutionMode.EXECUTE_FILE == "ExecuteFile"
        assert ExecutionMode.EXECUTE_STATEMENT == "ExecuteStatement"
        assert ExecutionMode.EVALUATE_STATEMENT == "EvaluateStatement"


class TestDiscoveryHandling:
    """Tests for node discovery message handling."""
    
    def test_handle_pong_creates_node(self):
        """Test that PONG message creates a new node."""
        remote = UnrealRemoteExecution()
        
        pong_message = {
            "version": 1,
            "magic": "ue_py",
            "type": "pong",
            "source": "unreal-node-123",
            "data": {
                "project_name": "TestGame",
                "engine_version": "5.3.0",
                "machine": "test-pc"
            }
        }
        
        remote._handle_pong(pong_message)
        
        nodes = remote.get_remote_nodes()
        assert "unreal-node-123" in nodes
        assert nodes["unreal-node-123"].project_name == "TestGame"
        assert nodes["unreal-node-123"].data.engine_version == "5.3.0"
    
    def test_handle_discovery_message_valid_pong(self):
        """Test handling a valid PONG discovery message."""
        remote = UnrealRemoteExecution()
        
        pong_message = json.dumps({
            "version": 1,
            "magic": "ue_py",
            "type": "pong",
            "source": "test-node",
            "data": {"project_name": "MyProject"}
        })
        
        remote._handle_discovery_message(pong_message.encode("utf-8"), ("127.0.0.1", 6766))
        
        nodes = remote.get_remote_nodes()
        assert "test-node" in nodes
    
    def test_handle_discovery_message_ignores_own_messages(self):
        """Test that we ignore messages from ourselves."""
        remote = UnrealRemoteExecution()
        
        own_message = json.dumps({
            "version": 1,
            "magic": "ue_py",
            "type": "pong",
            "source": remote._node_id,
            "data": {"project_name": "MyProject"}
        })
        
        remote._handle_discovery_message(own_message.encode("utf-8"), ("127.0.0.1", 6766))
        
        nodes = remote.get_remote_nodes()
        assert len(nodes) == 0
    
    def test_handle_discovery_message_invalid_json(self):
        """Test handling invalid JSON gracefully."""
        remote = UnrealRemoteExecution()
        
        # Should not raise exception
        remote._handle_discovery_message(b"not valid json", ("127.0.0.1", 6766))
        
        nodes = remote.get_remote_nodes()
        assert len(nodes) == 0
    
    def test_handle_discovery_message_wrong_magic(self):
        """Test that messages with wrong magic are ignored."""
        remote = UnrealRemoteExecution()
        
        wrong_magic = json.dumps({
            "version": 1,
            "magic": "wrong_magic",
            "type": "pong",
            "source": "test-node",
            "data": {}
        })
        
        remote._handle_discovery_message(wrong_magic.encode("utf-8"), ("127.0.0.1", 6766))
        
        nodes = remote.get_remote_nodes()
        assert len(nodes) == 0
