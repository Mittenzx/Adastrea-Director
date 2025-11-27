"""
Unreal Engine Remote Execution Client.

This module provides a Python implementation for communicating with
Unreal Engine's Python Remote Execution protocol, enabling direct
Python script execution in the Unreal Editor.

Based on the protocol used by runreal/unreal-mcp but implemented
in pure Python for better integration with Adastrea Director.
"""

import socket
import struct
import logging
import time
import threading
from typing import Optional, Dict, Any, Tuple, Callable, List
from dataclasses import dataclass, field
from enum import IntEnum
from datetime import datetime

logger = logging.getLogger(__name__)


class MessageType(IntEnum):
    """Message types for the remote execution protocol."""
    PING = 0
    PONG = 1
    OPEN_CONNECTION = 2
    CLOSE_CONNECTION = 3
    COMMAND = 4
    COMMAND_RESULT = 5


class ExecutionMode(IntEnum):
    """Execution modes for Python commands."""
    EXECUTE_FILE = 0
    EXECUTE_STATEMENT = 1
    EVALUATE_STATEMENT = 2


@dataclass
class RemoteExecutionConfig:
    """Configuration for remote execution connection."""
    multicast_group: str = "239.0.0.1"
    multicast_port: int = 6766
    bind_address: str = "0.0.0.0"
    command_timeout: float = 30.0
    discovery_timeout: float = 5.0
    max_retries: int = 3
    retry_delay: float = 2.0


@dataclass
class CommandResult:
    """Result of a remote execution command."""
    success: bool
    output: str = ""
    error: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class RemoteNode:
    """Information about a discovered remote Unreal Editor node."""
    node_id: str
    project_name: str
    address: Tuple[str, int]
    last_seen: datetime = field(default_factory=datetime.now)


class UnrealRemoteExecution:
    """
    Client for Unreal Engine's Python Remote Execution protocol.
    
    This allows executing Python code directly in the Unreal Editor,
    enabling AI agents to control and interact with Unreal Engine projects.
    
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
    
    # Protocol constants
    MAGIC = b"CYCB"
    PROTOCOL_VERSION = 1
    
    def __init__(self, config: Optional[RemoteExecutionConfig] = None):
        """
        Initialize the remote execution client.
        
        Args:
            config: Configuration for the remote execution connection.
        """
        self.config = config or RemoteExecutionConfig()
        self._discovery_socket: Optional[socket.socket] = None
        self._command_socket: Optional[socket.socket] = None
        self._running = False
        self._nodes: Dict[str, RemoteNode] = {}
        self._discovery_thread: Optional[threading.Thread] = None
        self._connected_node: Optional[RemoteNode] = None
        self._node_id = f"adastrea-mcp-{int(time.time())}"
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
        
        if self._command_socket:
            try:
                self._send_close_connection()
                self._command_socket.close()
            except Exception as e:
                logger.debug(f"Error closing command socket: {e}")
            self._command_socket = None
        
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
        self._discovery_socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP
        )
        self._discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Try to set SO_REUSEPORT if available (not on all platforms)
        try:
            self._discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except AttributeError:
            pass
        
        self._discovery_socket.bind((self.config.bind_address, self.config.multicast_port))
        
        # Join multicast group
        mreq = struct.pack(
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
                data, addr = self._discovery_socket.recvfrom(4096)
                self._handle_discovery_message(data, addr)
            except socket.timeout:
                continue
            except Exception as e:
                if self._running:
                    logger.debug(f"Discovery loop error: {e}")
    
    def _handle_discovery_message(self, data: bytes, addr: Tuple[str, int]) -> None:
        """Handle an incoming discovery message."""
        try:
            # Parse message header
            if len(data) < 8 or data[:4] != self.MAGIC:
                return
            
            version, msg_type = struct.unpack("<II", data[4:12])
            if version != self.PROTOCOL_VERSION:
                return
            
            if msg_type == MessageType.PONG:
                self._handle_pong(data[12:], addr)
        except Exception as e:
            logger.debug(f"Error handling discovery message: {e}")
    
    def _handle_pong(self, data: bytes, addr: Tuple[str, int]) -> None:
        """Handle a PONG response from a remote node."""
        try:
            # Parse node info from PONG message
            # Format: node_id (string), project_name (string)
            node_id, rest = self._read_string(data)
            project_name, _ = self._read_string(rest)
            
            with self._lock:
                self._nodes[node_id] = RemoteNode(
                    node_id=node_id,
                    project_name=project_name,
                    address=addr,
                    last_seen=datetime.now()
                )
            
            logger.debug(f"Discovered node: {node_id} ({project_name}) at {addr}")
        except Exception as e:
            logger.debug(f"Error handling PONG: {e}")
    
    def _read_string(self, data: bytes) -> Tuple[str, bytes]:
        """Read a length-prefixed UTF-8 string from data."""
        if len(data) < 4:
            return "", data
        
        length = struct.unpack("<I", data[:4])[0]
        if len(data) < 4 + length:
            return "", data
        
        return data[4:4+length].decode("utf-8"), data[4+length:]
    
    def _write_string(self, s: str) -> bytes:
        """Write a length-prefixed UTF-8 string."""
        encoded = s.encode("utf-8")
        return struct.pack("<I", len(encoded)) + encoded
    
    def _send_ping(self) -> None:
        """Send a PING message to discover nodes."""
        if not self._discovery_socket:
            return
        
        message = self.MAGIC + struct.pack("<II", self.PROTOCOL_VERSION, MessageType.PING)
        message += self._write_string(self._node_id)
        
        try:
            self._discovery_socket.sendto(
                message,
                (self.config.multicast_group, self.config.multicast_port)
            )
            logger.debug("Sent PING for node discovery")
        except Exception as e:
            logger.error(f"Error sending PING: {e}")
    
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
    
    def open_command_connection(self, node: RemoteNode) -> bool:
        """
        Open a command connection to a remote node.
        
        Args:
            node: The remote node to connect to.
            
        Returns:
            True if connection was successful.
        """
        try:
            # Create TCP socket for command connection
            self._command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._command_socket.settimeout(self.config.command_timeout)
            
            # Connect to the node's command port (usually multicast_port + 1)
            command_address = (node.address[0], self.config.multicast_port + 1)
            self._command_socket.connect(command_address)
            
            # Send OPEN_CONNECTION message
            message = self.MAGIC + struct.pack("<II", self.PROTOCOL_VERSION, MessageType.OPEN_CONNECTION)
            message += self._write_string(self._node_id)
            self._command_socket.sendall(message)
            
            self._connected_node = node
            
            logger.info(f"Opened command connection to {node.node_id} at {command_address}")
            return True
        except Exception as e:
            logger.error(f"Failed to open command connection: {e}")
            if self._command_socket:
                self._command_socket.close()
                self._command_socket = None
            return False
    
    def _send_close_connection(self) -> None:
        """Send a CLOSE_CONNECTION message."""
        if not self._command_socket:
            return
        
        try:
            message = self.MAGIC + struct.pack("<II", self.PROTOCOL_VERSION, MessageType.CLOSE_CONNECTION)
            self._command_socket.sendall(message)
        except Exception as e:
            logger.debug(f"Error sending close connection: {e}")
    
    def run_command(self, code: str, mode: ExecutionMode = ExecutionMode.EXECUTE_STATEMENT) -> CommandResult:
        """
        Execute Python code in the connected Unreal Editor.
        
        Args:
            code: Python code to execute.
            mode: Execution mode (execute statement, evaluate, or file).
            
        Returns:
            CommandResult with output and any errors.
        """
        if not self._command_socket or not self._connected_node:
            return CommandResult(
                success=False,
                error="Not connected to a remote node"
            )
        
        try:
            # Build command message
            message = self.MAGIC + struct.pack("<II", self.PROTOCOL_VERSION, MessageType.COMMAND)
            message += struct.pack("<I", mode)
            message += self._write_string(code)
            
            self._command_socket.sendall(message)
            
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
        """Receive and parse a command result."""
        if not self._command_socket:
            return CommandResult(success=False, error="No connection")
        
        # Read header
        header = self._recv_exact(12)
        if not header or header[:4] != self.MAGIC:
            return CommandResult(success=False, error="Invalid response header")
        
        version, msg_type = struct.unpack("<II", header[4:12])
        if msg_type != MessageType.COMMAND_RESULT:
            return CommandResult(success=False, error=f"Unexpected message type: {msg_type}")
        
        # Read result data
        success_byte = self._recv_exact(1)
        success = success_byte and success_byte[0] == 1
        
        # Read output string
        output_len_data = self._recv_exact(4)
        if output_len_data:
            output_len = struct.unpack("<I", output_len_data)[0]
            output_data = self._recv_exact(output_len) if output_len > 0 else b""
            output = output_data.decode("utf-8") if output_data else ""
        else:
            output = ""
        
        # Read error string if present
        error_len_data = self._recv_exact(4)
        if error_len_data:
            error_len = struct.unpack("<I", error_len_data)[0]
            error_data = self._recv_exact(error_len) if error_len > 0 else b""
            error = error_data.decode("utf-8") if error_data else ""
        else:
            error = ""
        
        return CommandResult(
            success=success,
            output=output,
            error=error
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
    
    def is_connected(self) -> bool:
        """Check if currently connected to a remote node."""
        return self._connected_node is not None and self._command_socket is not None
    
    def add_command_listener(self, listener: Callable[[CommandResult], None]) -> None:
        """Add a listener for command results."""
        self._command_listeners.append(listener)
    
    def remove_command_listener(self, listener: Callable[[CommandResult], None]) -> None:
        """Remove a command result listener."""
        if listener in self._command_listeners:
            self._command_listeners.remove(listener)
    
    def __enter__(self) -> "UnrealRemoteExecution":
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.stop()
