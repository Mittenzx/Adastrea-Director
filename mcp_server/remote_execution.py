"""
Unreal Engine Remote Execution Client.

This module provides a Python implementation for communicating with
Unreal Engine's Python Remote Execution protocol, enabling direct
Python script execution in the Unreal Editor.

Based on the protocol used by runreal/unreal-mcp but implemented
in pure Python for better integration with Adastrea Director.
"""

import json
import socket
import logging
import time
import threading
import uuid
from typing import Optional, Dict, Tuple, Callable, List, Any
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


class MessageType:
    """Message types for the remote execution protocol (JSON-based)."""
    PING = "ping"
    PONG = "pong"
    OPEN_CONNECTION = "open_connection"
    CLOSE_CONNECTION = "close_connection"
    COMMAND = "command"
    COMMAND_RESULT = "command_result"


class ExecutionMode:
    """Execution modes for Python commands."""
    EXECUTE_FILE = "ExecuteFile"
    EXECUTE_STATEMENT = "ExecuteStatement"
    EVALUATE_STATEMENT = "EvaluateStatement"


@dataclass
class RemoteExecutionConfig:
    """Configuration for remote execution connection."""
    multicast_group: str = "239.0.0.1"
    multicast_port: int = 6766
    bind_address: str = "0.0.0.0"
    command_endpoint: Tuple[str, int] = ("127.0.0.1", 6776)
    command_timeout: float = 30.0
    discovery_timeout: float = 5.0
    max_retries: int = 3
    retry_delay: float = 2.0
    multicast_ttl: int = 0  # 0 = local only, 1 = same subnet


@dataclass
class CommandResult:
    """Result of a remote execution command."""
    success: bool
    output: str = ""
    error: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass 
class CommandOutputItem:
    """Individual output item from command execution."""
    type: str  # "Info", "Warning", "Error"
    output: str


@dataclass
class RemoteNodeData:
    """Data about a remote Unreal Editor node."""
    engine_root: str = ""
    engine_version: str = ""
    machine: str = ""
    project_name: str = ""
    project_root: str = ""
    user: str = ""


@dataclass
class RemoteNode:
    """Information about a discovered remote Unreal Editor node."""
    node_id: str
    data: RemoteNodeData
    last_seen: datetime = field(default_factory=datetime.now)
    
    @property
    def project_name(self) -> str:
        """Get project name for backwards compatibility."""
        return self.data.project_name


class UnrealRemoteExecution:
    """
    Client for Unreal Engine's Python Remote Execution protocol.
    
    This allows executing Python code directly in the Unreal Editor,
    enabling AI agents to control and interact with Unreal Engine projects.
    
    Uses JSON-based messaging protocol compatible with Unreal Engine 4.x and 5.x.
    
    Example:
        ```python
        remote = UnrealRemoteExecution()
        remote.start()
        
        # Wait for connection
        node = remote.get_first_remote_node()
        if node:
            remote.open_command_connection(node)
            result = remote.run_command('print("Hello from MCP!")')
            print(result.output)
        
        remote.stop()
        ```
    """
    
    # Protocol constants - JSON-based protocol
    PROTOCOL_MAGIC = "ue_py"
    PROTOCOL_VERSION = 1
    
    # Legacy constants for backwards compatibility with tests
    MAGIC = PROTOCOL_MAGIC
    
    # Node timeout in milliseconds
    NODE_TIMEOUT_MS = 5000
    
    def __init__(self, config: Optional[RemoteExecutionConfig] = None):
        """
        Initialize the remote execution client.
        
        Args:
            config: Configuration for the remote execution connection.
        """
        self.config = config or RemoteExecutionConfig()
        self._discovery_socket: Optional[socket.socket] = None
        self._command_socket: Optional[socket.socket] = None
        self._command_server: Optional[socket.socket] = None
        self._running = False
        self._nodes: Dict[str, RemoteNode] = {}
        self._discovery_thread: Optional[threading.Thread] = None
        self._connected_node: Optional[RemoteNode] = None
        self._node_id = str(uuid.uuid4())
        self._lock = threading.Lock()
        self._command_listeners: List[Callable[[CommandResult], None]] = []
        
        logger.info(f"Initialized UnrealRemoteExecution with node_id: {self._node_id}")
    
    def start(self) -> None:
        """Start the remote execution client and begin node discovery."""
        if self._running:
            logger.warning("Remote execution client is already running")
            return
        
        self._running = True
        self._setup_discovery_socket()
        self._start_discovery_thread()
        
        logger.info("Remote execution client started")
    
    def stop(self) -> None:
        """Stop the remote execution client and close all connections."""
        self._running = False
        
        if self._connected_node:
            try:
                self._broadcast_close_connection()
            except Exception as e:
                logger.debug(f"Error sending close connection: {e}")
        
        if self._command_socket:
            try:
                self._command_socket.close()
            except Exception as e:
                logger.debug(f"Error closing command socket: {e}")
            self._command_socket = None
        
        if self._command_server:
            try:
                self._command_server.close()
            except Exception as e:
                logger.debug(f"Error closing command server: {e}")
            self._command_server = None
        
        if self._discovery_socket:
            try:
                self._discovery_socket.close()
            except Exception as e:
                logger.debug(f"Error closing discovery socket: {e}")
            self._discovery_socket = None
        
        if self._discovery_thread and self._discovery_thread.is_alive():
            self._discovery_thread.join(timeout=2.0)
        
        self._connected_node = None
        self._nodes.clear()
        
        logger.info("Remote execution client stopped")
    
    def _setup_discovery_socket(self) -> None:
        """Set up the multicast socket for node discovery."""
        import struct as struct_module
        
        self._discovery_socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP
        )
        self._discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Try to set SO_REUSEPORT if available (not on all platforms)
        try:
            self._discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except (AttributeError, OSError):
            pass
        
        # Bind to the multicast port
        self._discovery_socket.bind((self.config.bind_address, self.config.multicast_port))
        
        # Set multicast options
        self._discovery_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
        self._discovery_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.config.multicast_ttl)
        
        # Set multicast interface
        self._discovery_socket.setsockopt(
            socket.IPPROTO_IP, socket.IP_MULTICAST_IF,
            socket.inet_aton(self.config.bind_address)
        )
        
        # Join multicast group
        mreq = struct_module.pack(
            "4s4s",
            socket.inet_aton(self.config.multicast_group),
            socket.inet_aton(self.config.bind_address)
        )
        self._discovery_socket.setsockopt(
            socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq
        )
        
        self._discovery_socket.settimeout(1.0)
        
        logger.debug(
            f"Discovery socket bound to {self.config.bind_address}:{self.config.multicast_port}"
        )
    
    def _start_discovery_thread(self) -> None:
        """Start the background thread for node discovery."""
        self._discovery_thread = threading.Thread(
            target=self._discovery_loop,
            daemon=True,
            name="UnrealRemoteExecution-Discovery"
        )
        self._discovery_thread.start()
    
    def _discovery_loop(self) -> None:
        """Background loop for receiving node announcements."""
        while self._running and self._discovery_socket:
            try:
                data, addr = self._discovery_socket.recvfrom(65535)
                self._handle_discovery_message(data, addr)
            except socket.timeout:
                continue
            except Exception as e:
                if self._running:
                    logger.debug(f"Discovery loop error: {e}")
    
    def _handle_discovery_message(self, data: bytes, addr: Tuple[str, int]) -> None:
        """Handle an incoming discovery message (JSON format)."""
        try:
            # Parse JSON message
            json_str = data.decode("utf-8")
            message = json.loads(json_str)
            
            # Validate message format
            if not self._validate_message(message):
                return
            
            # Check if this message passes our receive filter
            if not self._passes_receive_filter(message):
                return
            
            msg_type = message.get("type", "")
            if msg_type == MessageType.PONG:
                self._handle_pong(message)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.debug(f"Error decoding discovery message: {e}")
        except Exception as e:
            logger.debug(f"Error handling discovery message: {e}")
    
    def _validate_message(self, message: Dict[str, Any]) -> bool:
        """Validate that a message has required fields and correct values."""
        if message.get("version") != self.PROTOCOL_VERSION:
            return False
        if message.get("magic") != self.PROTOCOL_MAGIC:
            return False
        return True
    
    def _passes_receive_filter(self, message: Dict[str, Any]) -> bool:
        """Check if a message passes our receive filter."""
        source = message.get("source", "")
        dest = message.get("dest")
        
        # Ignore messages from ourselves
        if source == self._node_id:
            return False
        
        # Accept if no destination (broadcast) or if destined for us
        if dest is None or dest == self._node_id:
            return True
        
        return False
    
    def _handle_pong(self, message: Dict[str, Any]) -> None:
        """Handle a PONG response from a remote node."""
        try:
            source_id = message.get("source", "")
            data_dict = message.get("data", {})
            
            # Build RemoteNodeData from message data
            node_data = RemoteNodeData(
                engine_root=data_dict.get("engine_root", ""),
                engine_version=data_dict.get("engine_version", ""),
                machine=data_dict.get("machine", ""),
                project_name=data_dict.get("project_name", ""),
                project_root=data_dict.get("project_root", ""),
                user=data_dict.get("user", "")
            )
            
            with self._lock:
                if source_id in self._nodes:
                    # Update existing node
                    self._nodes[source_id].data = node_data
                    self._nodes[source_id].last_seen = datetime.now()
                else:
                    # Add new node
                    self._nodes[source_id] = RemoteNode(
                        node_id=source_id,
                        data=node_data,
                        last_seen=datetime.now()
                    )
            
            logger.debug(f"Discovered node: {source_id} ({node_data.project_name})")
        except Exception as e:
            logger.debug(f"Error handling PONG: {e}")
    
    def _create_message(self, msg_type: str, dest: Optional[str] = None, 
                        data: Optional[Dict[str, Any]] = None) -> str:
        """Create a JSON message string."""
        message: Dict[str, Any] = {
            "version": self.PROTOCOL_VERSION,
            "magic": self.PROTOCOL_MAGIC,
            "source": self._node_id,
            "type": msg_type
        }
        
        if dest:
            message["dest"] = dest
        if data:
            message["data"] = data
        
        return json.dumps(message)
    
    def _send_ping(self) -> None:
        """Send a PING message to discover nodes."""
        if not self._discovery_socket:
            return
        
        message = self._create_message(MessageType.PING)
        
        try:
            self._discovery_socket.sendto(
                message.encode("utf-8"),
                (self.config.multicast_group, self.config.multicast_port)
            )
            logger.debug("Sent PING for node discovery")
        except Exception as e:
            logger.error(f"Error sending PING: {e}")
    
    def _broadcast_open_connection(self, node: RemoteNode) -> None:
        """Broadcast an OPEN_CONNECTION message to initiate command channel."""
        if not self._discovery_socket:
            return
        
        data = {
            "command_ip": self.config.command_endpoint[0],
            "command_port": self.config.command_endpoint[1]
        }
        
        message = self._create_message(MessageType.OPEN_CONNECTION, dest=node.node_id, data=data)
        
        try:
            self._discovery_socket.sendto(
                message.encode("utf-8"),
                (self.config.multicast_group, self.config.multicast_port)
            )
            logger.debug(f"Sent OPEN_CONNECTION to {node.node_id}")
        except Exception as e:
            logger.error(f"Error sending OPEN_CONNECTION: {e}")
    
    def _broadcast_close_connection(self) -> None:
        """Broadcast a CLOSE_CONNECTION message."""
        if not self._discovery_socket or not self._connected_node:
            return
        
        message = self._create_message(MessageType.CLOSE_CONNECTION, dest=self._connected_node.node_id)
        
        try:
            self._discovery_socket.sendto(
                message.encode("utf-8"),
                (self.config.multicast_group, self.config.multicast_port)
            )
            logger.debug(f"Sent CLOSE_CONNECTION to {self._connected_node.node_id}")
        except Exception as e:
            logger.debug(f"Error sending CLOSE_CONNECTION: {e}")
    
    def get_remote_nodes(self) -> Dict[str, RemoteNode]:
        """Get all discovered remote nodes."""
        with self._lock:
            return dict(self._nodes)
    
    def get_first_remote_node(
        self,
        poll_interval: float = 0.5,
        timeout: Optional[float] = None
    ) -> Optional[RemoteNode]:
        """
        Wait for and return the first discovered remote node.
        
        Args:
            poll_interval: How often to check for nodes and send pings.
            timeout: Maximum time to wait. Uses config.discovery_timeout if None.
            
        Returns:
            The first discovered RemoteNode, or None if timeout.
        """
        timeout = timeout or self.config.discovery_timeout
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            self._send_ping()
            time.sleep(poll_interval)
            
            nodes = self.get_remote_nodes()
            if nodes:
                return next(iter(nodes.values()))
        
        logger.warning(f"No remote nodes discovered within {timeout}s timeout")
        return None
    
    def open_command_connection(self, node: RemoteNode, timeout_ms: int = 10000) -> bool:
        """
        Open a command connection to a remote node.
        
        The protocol works by:
        1. We start a TCP server on our command endpoint
        2. We broadcast an OPEN_CONNECTION message via UDP multicast
        3. Unreal receives the message and connects to our TCP server
        
        Args:
            node: The remote node to connect to.
            timeout_ms: Timeout in milliseconds for connection.
            
        Returns:
            True if connection was successful.
        """
        try:
            # Create TCP server to accept connection from Unreal
            self._command_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._command_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._command_server.settimeout(timeout_ms / 1000.0)
            self._command_server.bind(self.config.command_endpoint)
            self._command_server.listen(1)
            
            logger.debug(f"Command server listening on {self.config.command_endpoint}")
            
            # Broadcast the open connection request
            self._broadcast_open_connection(node)
            
            # Wait for Unreal to connect
            try:
                self._command_socket, client_addr = self._command_server.accept()
                self._command_socket.settimeout(self.config.command_timeout)
                logger.debug(f"Accepted connection from {client_addr}")
            except socket.timeout:
                logger.error(f"Timeout waiting for Unreal to connect")
                self._command_server.close()
                self._command_server = None
                return False
            
            self._connected_node = node
            
            logger.info(f"Opened command connection to {node.node_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to open command connection: {e}")
            if self._command_server:
                self._command_server.close()
                self._command_server = None
            if self._command_socket:
                self._command_socket.close()
                self._command_socket = None
            return False
    
    def _send_close_connection(self) -> None:
        """Send a CLOSE_CONNECTION message (broadcast-based)."""
        self._broadcast_close_connection()
    
    def run_command(self, code: str, mode: str = ExecutionMode.EXECUTE_FILE, 
                    unattended: bool = True) -> CommandResult:
        """
        Execute Python code in the connected Unreal Editor.
        
        Args:
            code: Python code to execute.
            mode: Execution mode (ExecuteFile, ExecuteStatement, or EvaluateStatement).
            unattended: If True, suppress UI interactions.
            
        Returns:
            CommandResult with output and any errors.
        """
        if not self._command_socket or not self._connected_node:
            return CommandResult(
                success=False,
                error="Not connected to Unreal Engine. Use open_command_connection() to establish a connection first."
            )
        
        try:
            # Build command message (JSON format)
            command_data = {
                "command": code,
                "unattended": unattended,
                "exec_mode": mode
            }
            
            message = self._create_message(
                MessageType.COMMAND, 
                dest=self._connected_node.node_id,
                data=command_data
            )
            
            # Send message
            self._command_socket.sendall(message.encode("utf-8"))
            
            # Wait for response
            response = self._receive_command_result()
            return response
        except socket.timeout:
            return CommandResult(
                success=False,
                error=f"Command timed out after {self.config.command_timeout}s"
            )
        except Exception as e:
            logger.error(f"Error running command: {e}")
            return CommandResult(
                success=False,
                error=str(e)
            )
    
    def _receive_command_result(self) -> CommandResult:
        """Receive and parse a command result (JSON format)."""
        if not self._command_socket:
            return CommandResult(success=False, error="No connection")
        
        # Read data from socket - may come in chunks for large responses
        data_received = b""
        
        while True:
            try:
                chunk = self._command_socket.recv(65535)
                if not chunk:
                    break
                data_received += chunk
                
                # Try to parse as JSON
                try:
                    json_str = data_received.decode("utf-8")
                    message = json.loads(json_str)
                    break
                except json.JSONDecodeError:
                    # Not complete yet, continue reading
                    continue
            except socket.timeout:
                break
        
        if not data_received:
            return CommandResult(success=False, error="No response received")
        
        try:
            json_str = data_received.decode("utf-8")
            message = json.loads(json_str)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            return CommandResult(success=False, error=f"Failed to parse response: {e}")
        
        # Validate message
        if not self._validate_message(message):
            return CommandResult(success=False, error="Invalid response message format")
        
        if message.get("type") != MessageType.COMMAND_RESULT:
            return CommandResult(success=False, error=f"Unexpected message type: {message.get('type')}")
        
        # Extract result data
        data = message.get("data", {})
        success = data.get("success", False)
        result_text = data.get("result", "")
        
        # Collect output from output array
        output_items = data.get("output", [])
        output_lines = []
        error_lines = []
        
        for item in output_items:
            item_type = item.get("type", "Info")
            item_output = item.get("output", "")
            
            if item_type == "Error":
                error_lines.append(item_output)
            else:
                output_lines.append(item_output)
        
        # Add result to error if command failed
        if not success and result_text:
            error_lines.append(result_text)
        
        return CommandResult(
            success=success,
            output="\n".join(output_lines),
            error="\n".join(error_lines)
        )
    
    def _recv_exact(self, num_bytes: int) -> Optional[bytes]:
        """Receive exactly num_bytes from the socket."""
        if not self._command_socket:
            return None
        
        data = b""
        while len(data) < num_bytes:
            try:
                chunk = self._command_socket.recv(num_bytes - len(data))
                if not chunk:
                    return None
                data += chunk
            except socket.timeout:
                return None
        
        return data
    
    # Legacy methods for backwards compatibility with tests
    def _write_string(self, s: str) -> bytes:
        """Write a length-prefixed UTF-8 string (legacy method for tests)."""
        import struct as struct_module
        encoded = s.encode("utf-8")
        return struct_module.pack("<I", len(encoded)) + encoded
    
    def _read_string(self, data: bytes) -> Tuple[str, bytes]:
        """Read a length-prefixed UTF-8 string from data (legacy method for tests)."""
        import struct as struct_module
        if len(data) < 4:
            return "", data
        
        length = struct_module.unpack("<I", data[:4])[0]
        if len(data) < 4 + length:
            return "", data
        
        return data[4:4+length].decode("utf-8"), data[4+length:]
    
    def is_connected(self) -> bool:
        """Check if currently connected to a remote node."""
        return self._connected_node is not None and self._command_socket is not None
    
    def add_command_listener(self, listener: Callable[[CommandResult], None]) -> None:
        """Add a listener for command results."""
        with self._lock:
            self._command_listeners.append(listener)
    
    def remove_command_listener(self, listener: Callable[[CommandResult], None]) -> None:
        """Remove a command result listener."""
        with self._lock:
            if listener in self._command_listeners:
                self._command_listeners.remove(listener)
    
    def __enter__(self) -> "UnrealRemoteExecution":
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.stop()
