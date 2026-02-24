#!/usr/bin/env python3
"""
Enhanced Adastrea Director - Unreal Engine MCP CLI.

An enhanced command-line interface for interacting with Unreal Engine through
the MCP server tools. Includes better error handling, diagnostics, and
user-friendly messages.

Usage:
    python unreal_mcp_cli_enhanced.py                    # Interactive mode
    python unreal_mcp_cli_enhanced.py --diagnostics      # Show diagnostics
    python unreal_mcp_cli_enhanced.py project-info       # Get project info
    python unreal_mcp_cli_enhanced.py --setup-help       # Get setup instructions
"""

import argparse
import json
import sys
import os

try:
    from mcp_server.server_enhanced import EnhancedUnrealMCPServer, EnhancedMCPServerConfig
except ImportError:
    # Try to import the original if enhanced is not available
    try:
        from mcp_server import UnrealMCPServer as EnhancedUnrealMCPServer
        from mcp_server import MCPServerConfig as EnhancedMCPServerConfig
        print("[WARNING]  Using original MCP server (enhanced version not available)")
    except ImportError:
        # Only exit if this module is being run directly, not imported
        if __name__ == '__main__':
            print("Error: mcp_server module not found.")
            print("Make sure you're running from the Adastrea-Director directory.")
            sys.exit(1)
        else:
            # Re-raise the ImportError if imported as a module
            raise


def print_enhanced_result(result: dict, pretty: bool = True) -> None:
    """Print a tool result with enhanced formatting."""
    if result.get("isError"):
        print("\n" + "=" * 60)
        print("[ERROR] ERROR")
        print("=" * 60)
        for content in result.get("content", []):
            if content["type"] == "text":
                print(content["text"])
        print("=" * 60)
    else:
        for content in result.get("content", []):
            if content["type"] == "text":
                if pretty:
                    try:
                        # Try to parse as JSON for pretty printing
                        data = json.loads(content["text"])
                        print(json.dumps(data, indent=2))
                    except json.JSONDecodeError:
                        print(content["text"])
                else:
                    print(content["text"])
            elif content["type"] == "image":
                print(f"[Image: {content.get('mimeType', 'unknown')}]")


def show_setup_help():
    """Show setup help for Unreal Engine Python Remote Execution."""
    help_text = """
    [ROCKET] Adastrea Director - Unreal Engine Setup Help
    ==============================================

    The MCP server requires Unreal Engine Python Remote Execution to be enabled.

    QUICK SETUP:
    1. Launch Unreal Engine Editor
    2. Enable Python Plugin:
       - Edit -> Plugins -> Search "Python" -> Enable "Python Editor Script Plugin"
    3. Enable Remote Execution:
       - Edit -> Project Settings -> Search "Python" -> Check "Enable Remote Execution"
       - Set "Multicast Bind Address" to "0.0.0.0"
    4. Restart Unreal Editor

    DIAGNOSTIC TOOLS:
    - Check connection: python test_unreal_connection.py
    - Configure automatically: python configure_unreal_python.py --create-config
    - Get instructions: python configure_unreal_python.py --instructions

    TROUBLESHOOTING:
    - Ensure Unreal Editor is RUNNING (not just the project file)
    - Check firewall settings for ports 6766 and 6776
    - Verify Python plugin is installed (via Epic Games Launcher)
    - Try restarting Unreal Editor after configuration changes

    Once configured, run: python unreal_mcp_cli_enhanced.py
    """
    
    print(help_text)


def show_diagnostics(server: EnhancedUnrealMCPServer):
    """Show diagnostic information."""
    print("\n" + "=" * 60)
    print("[TOOL] MCP Server Diagnostics")
    print("=" * 60)
    
    # Get basic diagnostics
    if hasattr(server, 'get_diagnostics'):
        diag = server.get_diagnostics()
        print(f"Server running: {'[OK]' if diag['server_running'] else '[ERROR]'}")
        print(f"Connected to UE: {'[OK]' if diag['connected_to_ue'] else '[ERROR]'}")
        print(f"Connection errors: {diag['connection_errors']}")
        print(f"Multicast port: {diag['config']['multicast_port']}")
    else:
        print(f"Connected to UE: {'[OK]' if server.is_connected() else '[ERROR]'}")
    
    # List available tools
    tools = server.list_tools()
    print(f"\nAvailable tools: {len(tools)}")
    
    # Show connection test command
    print("\n" + "=" * 60)
    print("[IDEA] Quick Tests")
    print("=" * 60)
    print("Test connection: python test_unreal_connection.py")
    print("Get project info: python unreal_mcp_cli_enhanced.py project-info")
    print("List assets: python unreal_mcp_cli_enhanced.py list-assets")


def interactive_mode_enhanced(server: EnhancedUnrealMCPServer) -> None:
    """Run in enhanced interactive mode."""
    print("\n" + "=" * 60)
    print("  [ROCKET] Enhanced Adastrea Director - Unreal Engine MCP CLI")
    print("=" * 60)
    
    # Show connection status
    if server.is_connected():
        print("[OK] Connected to Unreal Engine!")
    else:
        print("[WARNING]  Not connected to Unreal Engine")
        print("   Type 'setup' for setup instructions")
        print("   Type 'diagnostics' for diagnostic information")
    
    print("\nEnhanced commands:")
    print("  help, ?        - Show this help")
    print("  setup          - Show setup instructions")
    print("  diagnostics    - Show diagnostic information")
    print("  tools          - List available tools")
    print("  project        - Get project info")
    print("  assets         - List project assets")
    print("  search <term>  - Search for assets")
    print("  python <code>  - Execute Python in Unreal")
    print("  quit, exit     - Exit")
    print()
    
    while True:
        try:
            user_input = input("unreal> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[WAVE] Goodbye!")
            break
        
        if not user_input:
            continue
        
        parts = user_input.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""
        
        if cmd in ("quit", "exit", "q"):
            print("[WAVE] Goodbye!")
            break
        elif cmd in ("help", "?"):
            print("\nEnhanced commands:")
            print("  help, ?        - Show this help")
            print("  setup          - Show setup instructions")
            print("  diagnostics    - Show diagnostic information")
            print("  tools          - List available tools")
            print("  project        - Get project info")
            print("  map            - Get current map info")
            print("  assets         - List project assets")
            print("  search <term>  - Search for assets")
            print("  outliner       - Get world outliner (actors)")
            print("  python <code>  - Execute Python in Unreal")
            print("  console <cmd>  - Run console command")
            print("  blueprint      - Create a new blueprint")
            print("  quit, exit     - Exit")
        elif cmd == "setup":
            show_setup_help()
        elif cmd == "diagnostics":
            show_diagnostics(server)
        elif cmd == "tools":
            tools = server.list_tools()
            print(f"\nAvailable tools ({len(tools)}):")
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description'][:60]}...")
        elif cmd == "project":
            result = server.handle_tool_call("editor_project_info", {})
            print_enhanced_result(result)
        elif cmd == "map":
            result = server.handle_tool_call("editor_get_map_info", {})
            print_enhanced_result(result)
        elif cmd == "assets":
            result = server.handle_tool_call("editor_list_assets", {})
            print_enhanced_result(result)
        elif cmd == "search":
            if not arg:
                print("Usage: search <term>")
            else:
                result = server.handle_tool_call("editor_search_assets", {"search_term": arg})
                print_enhanced_result(result)
        elif cmd == "outliner":
            result = server.handle_tool_call("editor_get_world_outliner", {})
            print_enhanced_result(result)
        elif cmd == "python":
            if not arg:
                print("Usage: python <code>")
                print("Example: python \"import unreal; print(unreal.SystemLibrary.get_engine_version())\"")
            else:
                result = server.handle_tool_call("editor_run_python", {"code": arg})
                print_enhanced_result(result)
        elif cmd == "console":
            if not arg:
                print("Usage: console <command>")
                print("Example: console stat fps")
            else:
                result = server.handle_tool_call("editor_console_command", {"command": arg})
                print_enhanced_result(result)
        elif cmd == "blueprint":
            if not arg:
                print("Usage: blueprint <name> [parent_class] [package_path]")
                print("Example: blueprint BP_MyActor Actor /Game/Blueprints")
            else:
                parts = arg.split()
                blueprint_name = parts[0]
                if " " in blueprint_name:
                    print("Error: Blueprint names cannot contain spaces.")
                else:
                    params = {"blueprint_name": blueprint_name}
                    if len(parts) > 1:
                        params["parent_class"] = parts[1]
                    if len(parts) > 2:
                        params["package_path"] = parts[2]
                    result = server.handle_tool_call("editor_create_blueprint", params)
                    print_enhanced_result(result)
        else:
            print(f"Unknown command: {cmd}. Type 'help' for available commands.")


def main():
    parser = argparse.ArgumentParser(
        description="Enhanced Adastrea Director - Unreal Engine MCP CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python unreal_mcp_cli_enhanced.py                         # Interactive mode
    python unreal_mcp_cli_enhanced.py --diagnostics           # Show diagnostics
    python unreal_mcp_cli_enhanced.py --setup-help            # Get setup instructions
    python unreal_mcp_cli_enhanced.py project-info            # Get project info
    python unreal_mcp_cli_enhanced.py list-assets             # List all assets
    python unreal_mcp_cli_enhanced.py search-assets "player"  # Search for assets
    python unreal_mcp_cli_enhanced.py run-python "import unreal; print(unreal.SystemLibrary.get_engine_version())"

Setup Tools:
    python test_unreal_connection.py                          # Test UE connection
    python configure_unreal_python.py --instructions          # Get setup instructions
    python configure_unreal_python.py --create-config         # Auto-configure UE
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # List tools
    subparsers.add_parser("list-tools", help="List available MCP tools")
    
    # Project info
    subparsers.add_parser("project-info", help="Get project information")
    
    # Map info
    subparsers.add_parser("map-info", help="Get current map information")
    
    # List assets
    subparsers.add_parser("list-assets", help="List project assets")
    
    # Search assets
    search_parser = subparsers.add_parser("search-assets", help="Search for assets")
    search_parser.add_argument("term", help="Search term")
    search_parser.add_argument("--class", dest="asset_class", help="Filter by asset class")
    
    # World outliner
    subparsers.add_parser("world-outliner", help="Get world outliner (all actors)")
    
    # Run Python
    python_parser = subparsers.add_parser("run-python", help="Execute Python in Unreal")
    python_parser.add_argument("code", help="Python code to execute")
    
    # Console command
    console_parser = subparsers.add_parser("console", help="Run console command")
    console_parser.add_argument("console_cmd", help="Console command to run")
    
    # Create blueprint
    blueprint_parser = subparsers.add_parser("create-blueprint", help="Create a new Blueprint asset")
    blueprint_parser.add_argument("name", help="Blueprint name (e.g., 'BP_MyActor')")
    blueprint_parser.add_argument("--parent", default="Actor", help="Parent class (default: Actor)")
    blueprint_parser.add_argument("--path", default="/Game/Blueprints", help="Package path (default: /Game/Blueprints)")
    
    # Global options
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--diagnostics", action="store_true", help="Show diagnostic information")
    parser.add_argument("--setup-help", action="store_true", help="Show setup instructions")
    
    args = parser.parse_args()
    
    # Show setup help if requested
    if args.setup_help:
        show_setup_help()
        return
    
    # Configure logging
    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    # Create and connect server
    print("[PLUG] Connecting to Unreal Engine...")
    
    try:
        config = EnhancedMCPServerConfig()
        with EnhancedUnrealMCPServer(config) as server:
            if not server.is_connected():
                print("\n[WARNING]  Warning: Not connected to Unreal Engine.")
                print("   Make sure Unreal Editor is running with Python Remote Execution enabled.")
                print("   Run with --setup-help for instructions.")
                print()
            
            # Show diagnostics if requested
            if args.diagnostics:
                show_diagnostics(server)
                return
            
            # No command = interactive mode
            if not args.command:
                interactive_mode_enhanced(server)
                return
            
            # Handle specific commands
            if args.command == "list-tools":
                tools = server.list_tools()
                if args.json:
                    print(json.dumps(tools, indent=2))
                else:
                    print(f"\nAvailable tools ({len(tools)}):\n")
                    for tool in tools:
                        print(f"  {tool['name']}")
                        print(f"    {tool['description']}\n")
            
            elif args.command == "project-info":
                result = server.handle_tool_call("editor_project_info", {})
                print_enhanced_result(result, not args.json)
            
            elif args.command == "map-info":
                result = server.handle_tool_call("editor_get_map_info", {})
                print_enhanced_result(result, not args.json)
            
            elif args.command == "list-assets":
                result = server.handle_tool_call("editor_list_assets", {})
                print_enhanced_result(result, not args.json)
            
            elif args.command == "search-assets":
                params = {"search_term": args.term}
                if args.asset_class:
                    params["asset_class"] = args.asset_class
                result = server.handle_tool_call("editor_search_assets", params)
                print_enhanced_result(result, not args.json)
            
            elif args.command == "world-outliner":
                result = server.handle_tool_call("editor_get_world_outliner", {})
                print_enhanced_result(result, not args.json)
            
            elif args.command == "run-python":
                result = server.handle_tool_call("editor_run_python", {"code": args.code})
                print_enhanced_result(result, not args.json)
            
            elif args.command == "console":
                result = server.handle_tool_call("editor_console_command", {"command": args.console_cmd})
                print_enhanced_result(result, not args.json)
            
            elif args.command == "create-blueprint":
                params = {
                    "blueprint_name": args.name,
                    "parent_class": args.parent,
                    "package_path": args.path
                }
                result = server.handle_tool_call("editor_create_blueprint", params)
                print_enhanced_result(result, not args.json)
    
    except KeyboardInterrupt:
        print("\n[STOP] Interrupted.")
    except Exception as e:
        if hasattr(args, "command") and args.command:
            print(f"[ERROR] Error while executing '{args.command}': {e}")
        else:
            print(f"[ERROR] Error during operation: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        
        print("\n[IDEA] Troubleshooting:")
        print("1. Run: python test_unreal_connection.py")
        print("2. Run: python configure_unreal_python.py --instructions")
        print("3. Check if Unreal Engine is running")
        
        sys.exit(1)


if __name__ == "__main__":
    main()