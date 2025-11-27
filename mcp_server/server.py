"""
Adastrea Director MCP Server.

This module implements the Model Context Protocol (MCP) server that enables
AI agents to interact with Unreal Engine through Adastrea Director.
"""

import json
import logging
import sys
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from .remote_execution import UnrealRemoteExecution, RemoteExecutionConfig
from .tools import get_tool, get_all_tools

logger = logging.getLogger(__name__)


@dataclass
class MCPServerConfig:
    """Configuration for the MCP server."""
    name: str = "AdastreaMCP"
    version: str = "0.1.0"
    description: str = "MCP server for Unreal Engine integration via Adastrea Director"
    multicast_group: str = "239.0.0.1"
    multicast_port: int = 6766
    connection_timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 2.0


class UnrealMCPServer:
    """
    MCP Server for Unreal Engine integration.
    
    This server implements the Model Context Protocol to allow AI agents
    to control Unreal Engine through the Python Remote Execution protocol.
    
    Example:
        ```python
        server = UnrealMCPServer()
        server.start()
        
        # Handle incoming MCP requests
        response = server.handle_tool_call("editor_list_assets", {})
        print(response)
        
        server.stop()
        ```
    """
    
    def __init__(self, config: Optional[MCPServerConfig] = None):
        """
        Initialize the MCP server.
        
        Args:
            config: Server configuration.
        """
        self.config = config or MCPServerConfig()
        self._remote: Optional[UnrealRemoteExecution] = None
        self._running = False
        self._connected = False
        
        logger.info(f"Initialized MCP Server: {self.config.name} v{self.config.version}")
    
    def start(self) -> bool:
        """
        Start the MCP server and connect to Unreal Engine.
        
        Returns:
            True if successfully started and connected.
        """
        if self._running:
            logger.warning("MCP server is already running")
            return self._connected
        
        self._running = True
        
        # Initialize remote execution
        remote_config = RemoteExecutionConfig(
            multicast_group=self.config.multicast_group,
            multicast_port=self.config.multicast_port,
            command_timeout=self.config.connection_timeout,
            max_retries=self.config.max_retries,
            retry_delay=self.config.retry_delay
        )
        self._remote = UnrealRemoteExecution(remote_config)
        self._remote.start()
        
        # Try to connect to Unreal Engine
        self._connected = self._try_connect()
        
        if self._connected:
            logger.info("MCP server started and connected to Unreal Engine")
        else:
            logger.warning("MCP server started but not connected to Unreal Engine")
        
        return self._connected
    
    def stop(self) -> None:
        """Stop the MCP server and disconnect from Unreal Engine."""
        self._running = False
        
        if self._remote:
            self._remote.stop()
            self._remote = None
        
        self._connected = False
        
        logger.info("MCP server stopped")
    
    def _try_connect(self) -> bool:
        """Try to connect to a remote Unreal Engine node."""
        if not self._remote:
            return False
        
        for attempt in range(self.config.max_retries):
            try:
                logger.info(f"Attempting to connect to Unreal Engine (attempt {attempt + 1}/{self.config.max_retries})")
                
                node = self._remote.get_first_remote_node(
                    timeout=self.config.connection_timeout
                )
                
                if node:
                    success = self._remote.open_command_connection(node)
                    if success:
                        # Verify connection with a simple command
                        result = self._remote.run_command('print("MCP:connected")')
                        if result.success:
                            logger.info(f"Connected to Unreal Engine project: {node.project_name}")
                            return True
                
                if attempt < self.config.max_retries - 1:
                    logger.info(f"Retrying in {self.config.retry_delay}s...")
                    time.sleep(self.config.retry_delay)
                    
            except Exception as e:
                logger.error(f"Connection attempt failed: {e}")
        
        return False
    
    def is_connected(self) -> bool:
        """Check if connected to Unreal Engine."""
        return self._connected and self._remote and self._remote.is_connected()
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information for MCP initialization."""
        return {
            "name": self.config.name,
            "version": self.config.version,
            "description": self.config.description,
            "connected": self.is_connected()
        }
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all available MCP tools.
        
        Returns:
            List of tool definitions with name, description, and parameters.
        """
        tools = []
        for tool in get_all_tools():
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.get_schema()
            })
        return tools
    
    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a tool call from an MCP client.
        
        Args:
            tool_name: Name of the tool to execute.
            arguments: Tool arguments.
            
        Returns:
            Tool execution result.
        """
        if not self.is_connected():
            return {
                "isError": True,
                "content": [{
                    "type": "text",
                    "text": "Not connected to Unreal Engine. Please ensure Unreal Editor is running with Python Remote Execution enabled."
                }]
            }
        
        tool = get_tool(tool_name)
        if not tool:
            return {
                "isError": True,
                "content": [{
                    "type": "text",
                    "text": f"Unknown tool: {tool_name}"
                }]
            }
        
        try:
            result = tool.execute(self._remote, **arguments)
            return {
                "isError": not result.success,
                "content": result.content
            }
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {
                "isError": True,
                "content": [{
                    "type": "text",
                    "text": f"Error executing tool: {str(e)}"
                }]
            }
    
    def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an incoming MCP message.
        
        Args:
            message: The MCP message to handle.
            
        Returns:
            Response message.
        """
        msg_type = message.get("type", "")
        msg_id = message.get("id")
        
        response = {"id": msg_id}
        
        try:
            if msg_type == "initialize":
                response["result"] = {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": self.get_server_info(),
                    "capabilities": {
                        "tools": {"listChanged": False}
                    }
                }
            
            elif msg_type == "initialized":
                # Client acknowledged initialization
                response["result"] = {}
            
            elif msg_type == "tools/list":
                response["result"] = {
                    "tools": self.list_tools()
                }
            
            elif msg_type == "tools/call":
                params = message.get("params", {})
                tool_name = params.get("name", "")
                arguments = params.get("arguments", {})
                response["result"] = self.handle_tool_call(tool_name, arguments)
            
            else:
                response["error"] = {
                    "code": -32601,
                    "message": f"Unknown message type: {msg_type}"
                }
        
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            response["error"] = {
                "code": -32603,
                "message": str(e)
            }
        
        return response
    
    def run_stdio(self) -> None:
        """
        Run the MCP server using stdio transport.
        
        This is the standard way to run an MCP server when invoked by
        a client like Claude or Cursor.
        """
        self.start()
        
        logger.info("MCP server running in stdio mode")
        
        try:
            while self._running:
                # Read line from stdin
                line = sys.stdin.readline()
                if not line:
                    break
                
                try:
                    message = json.loads(line)
                    response = self.handle_message(message)
                    
                    # Write response to stdout
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON: {e}")
                    error_response = {
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        }
                    }
                    sys.stdout.write(json.dumps(error_response) + "\n")
                    sys.stdout.flush()
        
        except KeyboardInterrupt:
            logger.info("MCP server interrupted")
        finally:
            self.stop()
    
    def __enter__(self) -> "UnrealMCPServer":
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.stop()


def main():
    """Main entry point for the MCP server."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Adastrea Director MCP Server for Unreal Engine"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--host",
        default="239.0.0.1",
        help="Multicast group address"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=6766,
        help="Multicast port"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        stream=sys.stderr  # Log to stderr, MCP uses stdout
    )
    
    # Create and run server
    config = MCPServerConfig(
        multicast_group=args.host,
        multicast_port=args.port
    )
    
    server = UnrealMCPServer(config)
    server.run_stdio()


if __name__ == "__main__":
    main()
