#!/usr/bin/env python3
"""
Enhanced Adastrea Director MCP Server.

This is an enhanced version of the MCP server with better error handling,
diagnostic information, and user-friendly error messages.

It wraps the original server.py to provide enhanced functionality.
"""

import json
import logging
import sys
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

# Import the original server
from .server import UnrealMCPServer as OriginalUnrealMCPServer
from .server import MCPServerConfig as OriginalMCPServerConfig
from .remote_execution import UnrealRemoteExecution, RemoteExecutionConfig
from .tools import get_tool, get_all_tools

logger = logging.getLogger(__name__)


@dataclass
class EnhancedMCPServerConfig(OriginalMCPServerConfig):
    """Enhanced configuration for the MCP server."""
    enable_diagnostics: bool = True
    show_connection_help: bool = True
    auto_check_configuration: bool = True
    connection_timeout: float = 45.0  # Longer timeout for better diagnostics


class EnhancedUnrealMCPServer(OriginalUnrealMCPServer):
    """
    Enhanced MCP Server for Unreal Engine integration.
    
    This enhanced version provides:
    - Better error messages with troubleshooting steps
    - Automatic configuration checking
    - Diagnostic information
    - User-friendly connection help
    """
    
    def __init__(self, config: Optional[EnhancedMCPServerConfig] = None):
        """Initialize the enhanced MCP server."""
        self.enhanced_config = config or EnhancedMCPServerConfig()
        super().__init__(self.enhanced_config)
        
        # Additional state for enhanced features
        self._last_connection_attempt = None
        self._connection_errors = []
        self._diagnostic_info = {}
        
        logger.info("Enhanced MCP server initialized")
    
    def start(self) -> bool:
        """
        Start the enhanced MCP server with diagnostics.
        
        Returns:
            True if server started successfully (even if not connected to UE)
        """
        logger.info("Starting enhanced MCP server...")
        
        # Run configuration check if enabled
        if self.enhanced_config.auto_check_configuration:
            self._run_configuration_check()
        
        # Start the original server
        result = super().start()
        
        if result:
            logger.info("Enhanced MCP server started successfully")
            
            # Log connection status
            if self.is_connected():
                logger.info("✅ Connected to Unreal Engine")
                self._log_connection_info()
            else:
                logger.warning("⚠️  MCP server started but not connected to Unreal Engine")
                if self.enhanced_config.show_connection_help:
                    self._show_connection_help()
        
        return result
    
    def _run_configuration_check(self):
        """Run configuration check and log results."""
        logger.info("Running configuration check...")
        
        # Check if test_unreal_connection.py exists
        try:
            import subprocess
            import os
            
            # Check if we can import the test module
            test_script = os.path.join(os.path.dirname(__file__), "..", "test_unreal_connection.py")
            if os.path.exists(test_script):
                logger.info("✅ Found connection test script")
                self._diagnostic_info["test_script"] = test_script
            else:
                logger.warning("⚠️  Connection test script not found")
                
        except Exception as e:
            logger.debug(f"Configuration check error: {e}")
    
    def _log_connection_info(self):
        """Log connection information when connected."""
        if self._remote and self._remote._connected_node:
            node = self._remote._connected_node
            logger.info(f"Connected to: {node.data.project_name}")
            logger.info(f"Engine: {node.data.engine_version}")
            logger.info(f"Project: {node.data.project_root}")
    
    def _show_connection_help(self):
        """Show helpful connection information."""
        help_text = """
        🔧 CONNECTION HELP 🔧
        
        The MCP server is running but not connected to Unreal Engine.
        
        QUICK SETUP:
        1. Ensure Unreal Engine Editor is running
        2. Enable Python Editor Script Plugin (Edit → Plugins)
        3. Enable Remote Execution (Edit → Project Settings → Python)
        4. Set Multicast Bind Address to "0.0.0.0"
        
        DIAGNOSE:
        Run: python test_unreal_connection.py
        
        CONFIGURE:
        Run: python configure_unreal_python.py --instructions
        
        The server will continue running and attempt to connect when
        Unreal Engine becomes available.
        """
        
        print(help_text)
        logger.info("Displayed connection help")
    
    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced tool call handling with better error messages.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool execution result with enhanced error handling
        """
        # Check connection first
        if not self.is_connected():
            return self._get_enhanced_connection_error()
        
        # Get the tool
        tool = get_tool(tool_name)
        if not tool:
            return {
                "isError": True,
                "content": [{
                    "type": "text",
                    "text": f"❓ Unknown tool: {tool_name}\n\nAvailable tools:\n" + 
                           "\n".join([f"  • {t.name}" for t in get_all_tools()])
                }]
            }
        
        try:
            # Execute the tool
            result = tool.execute(self._remote, **arguments)
            
            # Log successful execution
            logger.info(f"Tool executed: {tool_name}")
            
            return {
                "isError": not result.success,
                "content": result.content
            }
            
        except Exception as e:
            # Enhanced error handling
            logger.error(f"Error executing tool {tool_name}: {e}")
            self._connection_errors.append({
                "tool": tool_name,
                "error": str(e),
                "timestamp": time.time()
            })
            
            return self._get_enhanced_tool_error(tool_name, e)
    
    def _get_enhanced_connection_error(self) -> Dict[str, Any]:
        """Get enhanced connection error message."""
        error_text = """🚫 Not connected to Unreal Engine

The Adastrea Director MCP server cannot connect to Unreal Engine.

REQUIREMENTS:
• Unreal Engine 5.0+ must be RUNNING (not just the project file)
• Python Editor Script Plugin must be ENABLED
• Remote Execution must be ENABLED in Project Settings

QUICK FIX:
1. Launch Unreal Engine Editor
2. Open your project
3. Enable Python Remote Execution:
   • Edit → Plugins → Enable "Python Editor Script Plugin"
   • Edit → Project Settings → Python → Check "Enable Remote Execution"
   • Set "Multicast Bind Address" to "0.0.0.0"

DIAGNOSE:
Run: python test_unreal_connection.py

CONFIGURE:
Run: python configure_unreal_python.py --instructions

The server will automatically reconnect when Unreal Engine becomes available.
"""
        
        return {
            "isError": True,
            "content": [{
                "type": "text",
                "text": error_text
            }]
        }
    
    def _get_enhanced_tool_error(self, tool_name: str, error: Exception) -> Dict[str, Any]:
        """Get enhanced tool execution error message."""
        error_text = f"""🔧 Tool execution failed: {tool_name}

Error: {error}

POSSIBLE CAUSES:
1. Unreal Engine connection lost
2. Tool parameters incorrect
3. Unreal Engine is busy or frozen
4. Python script error in Unreal Engine

TROUBLESHOOTING:
1. Check if Unreal Engine is still running
2. Verify the connection: python test_unreal_connection.py
3. Check tool documentation for correct parameters
4. Restart Unreal Engine if needed

RECONNECT:
The server will attempt to reconnect automatically.
You can also restart the MCP server.
"""
        
        return {
            "isError": True,
            "content": [{
                "type": "text",
                "text": error_text
            }]
        }
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """
        Get diagnostic information about the server.
        
        Returns:
            Dictionary with diagnostic information
        """
        return {
            "server_running": self._running,
            "connected_to_ue": self.is_connected(),
            "connection_errors": len(self._connection_errors),
            "config": {
                "name": self.enhanced_config.name,
                "version": self.enhanced_config.version,
                "multicast_port": self.enhanced_config.multicast_port,
                "connection_timeout": self.enhanced_config.connection_timeout,
            },
            "last_connection_attempt": self._last_connection_attempt,
            "enhanced_features": {
                "diagnostics": self.enhanced_config.enable_diagnostics,
                "connection_help": self.enhanced_config.show_connection_help,
                "auto_config_check": self.enhanced_config.auto_check_configuration,
            }
        }
    
    def list_tools_enhanced(self) -> List[Dict[str, Any]]:
        """
        Get enhanced list of available tools.
        
        Returns:
            List of tools with additional information
        """
        tools = get_all_tools()
        
        enhanced_tools = []
        for tool in tools:
            enhanced_tool = {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
                "category": getattr(tool, "category", "general"),
                "requires_connection": getattr(tool, "requires_connection", True),
                "example": getattr(tool, "example", None),
            }
            enhanced_tools.append(enhanced_tool)
        
        return enhanced_tools


def main():
    """Enhanced main function for the MCP server."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Enhanced Adastrea Director MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m mcp_server.server_enhanced           # Start enhanced server
  python -m mcp_server.server_enhanced --debug   # With debug logging
  python -m mcp_server.server_enhanced --check   # Check configuration only
        
For Unreal Engine setup:
  python configure_unreal_python.py --instructions
  python test_unreal_connection.py
        """
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check configuration and exit"
    )
    
    parser.add_argument(
        "--no-diagnostics",
        action="store_true",
        help="Disable enhanced diagnostics"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=6766,
        help="Multicast port for discovery (default: 6766)"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    # Configuration check mode
    if args.check:
        print("🔧 Enhanced MCP Server Configuration Check")
        print("=" * 50)
        
        # Check for test script
        import os
        test_script = os.path.join(os.path.dirname(__file__), "..", "test_unreal_connection.py")
        if os.path.exists(test_script):
            print("✅ Connection test script: Found")
        else:
            print("⚠️  Connection test script: Not found")
        
        # Check for configuration helper
        config_script = os.path.join(os.path.dirname(__file__), "..", "configure_unreal_python.py")
        if os.path.exists(config_script):
            print("✅ Configuration helper: Found")
        else:
            print("⚠️  Configuration helper: Not found")
        
        print("\nRecommended next steps:")
        print("1. Run: python configure_unreal_python.py --check")
        print("2. Run: python test_unreal_connection.py")
        print("3. Start server: python -m mcp_server.server_enhanced")
        
        return
    
    # Create enhanced server configuration
    config = EnhancedMCPServerConfig(
        enable_diagnostics=not args.no_diagnostics,
        multicast_port=args.port,
    )
    
    # Create and start enhanced server
    print("🚀 Starting Enhanced Adastrea Director MCP Server")
    print("=" * 50)
    
    server = EnhancedUnrealMCPServer(config)
    
    try:
        if server.start():
            print("✅ Enhanced MCP server started")
            
            if server.is_connected():
                print("✅ Connected to Unreal Engine")
            else:
                print("⚠️  Not connected to Unreal Engine")
                print("   Run: python test_unreal_connection.py to diagnose")
                print("   Run: python configure_unreal_python.py --instructions for setup help")
            
            # Keep server running
            print("\n📡 Server is running. Press Ctrl+C to stop.")
            print("   Tools available:", len(server.list_tools_enhanced()))
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping server...")
        
        else:
            print("❌ Failed to start enhanced MCP server")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        
        print("\n💡 Troubleshooting:")
        print("1. Check if port", args.port, "is available")
        print("2. Run with --debug for more information")
        print("3. Check Unreal Engine Python configuration")
        
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())