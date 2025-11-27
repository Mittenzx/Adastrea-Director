#!/usr/bin/env python
"""
Adastrea Director - Unreal Engine MCP CLI.

A command-line interface for interacting with Unreal Engine through
the MCP server tools. No external MCP client required.

Usage:
    python unreal_mcp_cli.py                    # Interactive mode
    python unreal_mcp_cli.py list-tools         # List available tools
    python unreal_mcp_cli.py project-info       # Get project info
    python unreal_mcp_cli.py list-assets        # List project assets
    python unreal_mcp_cli.py run-python "code"  # Execute Python in UE
"""

import argparse
import json
import sys

try:
    from mcp_server import UnrealMCPServer
except ImportError:
    print("Error: mcp_server module not found.")
    print("Make sure you're running from the Adastrea-Director directory.")
    sys.exit(1)


def print_result(result: dict, pretty: bool = True) -> None:
    """Print a tool result."""
    if result.get("isError"):
        print("ERROR:", result["content"][0]["text"])
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


def interactive_mode(server: UnrealMCPServer) -> None:
    """Run in interactive mode."""
    print("\n" + "=" * 60)
    print("  Adastrea Director - Unreal Engine MCP CLI")
    print("=" * 60)
    print("\nConnected to Unreal Engine!" if server.is_connected() else "\nNot connected to Unreal Engine.")
    print("\nAvailable commands:")
    print("  help              - Show this help")
    print("  tools             - List available tools")
    print("  project           - Get project info")
    print("  map               - Get current map info")
    print("  assets            - List project assets")
    print("  search <term>     - Search for assets")
    print("  outliner          - Get world outliner (actors)")
    print("  python <code>     - Execute Python in Unreal")
    print("  console <cmd>     - Run console command")
    print("  quit              - Exit")
    print()
    
    while True:
        try:
            user_input = input("unreal> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        
        if not user_input:
            continue
        
        parts = user_input.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""
        
        if cmd in ("quit", "exit", "q"):
            print("Goodbye!")
            break
        elif cmd == "help":
            print("\nAvailable commands:")
            print("  help              - Show this help")
            print("  tools             - List available tools")
            print("  project           - Get project info")
            print("  map               - Get current map info")
            print("  assets            - List project assets")
            print("  search <term>     - Search for assets")
            print("  outliner          - Get world outliner (actors)")
            print("  python <code>     - Execute Python in Unreal")
            print("  console <cmd>     - Run console command")
            print("  quit              - Exit")
        elif cmd == "tools":
            tools = server.list_tools()
            print(f"\nAvailable tools ({len(tools)}):")
            for tool in tools:
                print(f"  {tool['name']}: {tool['description'][:60]}...")
        elif cmd == "project":
            result = server.handle_tool_call("editor_project_info", {})
            print_result(result)
        elif cmd == "map":
            result = server.handle_tool_call("editor_get_map_info", {})
            print_result(result)
        elif cmd == "assets":
            result = server.handle_tool_call("editor_list_assets", {})
            print_result(result)
        elif cmd == "search":
            if not arg:
                print("Usage: search <term>")
            else:
                result = server.handle_tool_call("editor_search_assets", {"search_term": arg})
                print_result(result)
        elif cmd == "outliner":
            result = server.handle_tool_call("editor_get_world_outliner", {})
            print_result(result)
        elif cmd == "python":
            if not arg:
                print("Usage: python <code>")
            else:
                result = server.handle_tool_call("editor_run_python", {"code": arg})
                print_result(result)
        elif cmd == "console":
            if not arg:
                print("Usage: console <command>")
            else:
                result = server.handle_tool_call("editor_console_command", {"command": arg})
                print_result(result)
        else:
            print(f"Unknown command: {cmd}. Type 'help' for available commands.")


def main():
    parser = argparse.ArgumentParser(
        description="Adastrea Director - Unreal Engine MCP CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python unreal_mcp_cli.py                         # Interactive mode
    python unreal_mcp_cli.py list-tools              # List available tools
    python unreal_mcp_cli.py project-info            # Get project info
    python unreal_mcp_cli.py list-assets             # List all assets
    python unreal_mcp_cli.py search-assets "player" # Search for assets
    python unreal_mcp_cli.py run-python "import unreal; print(unreal.SystemLibrary.get_engine_version())"
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
    
    # Global options
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Configure logging
    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    # Create and connect server
    print("Connecting to Unreal Engine...")
    
    try:
        with UnrealMCPServer() as server:
            if not server.is_connected():
                print("\nWarning: Not connected to Unreal Engine.")
                print("Make sure Unreal Editor is running with Python Remote Execution enabled.")
                print("See mcp_server/MCP_SERVER_GUIDE.md for setup instructions.\n")
            
            # No command = interactive mode
            if not args.command:
                interactive_mode(server)
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
                print_result(result, not args.json)
            
            elif args.command == "map-info":
                result = server.handle_tool_call("editor_get_map_info", {})
                print_result(result, not args.json)
            
            elif args.command == "list-assets":
                result = server.handle_tool_call("editor_list_assets", {})
                print_result(result, not args.json)
            
            elif args.command == "search-assets":
                params = {"search_term": args.term}
                if args.asset_class:
                    params["asset_class"] = args.asset_class
                result = server.handle_tool_call("editor_search_assets", params)
                print_result(result, not args.json)
            
            elif args.command == "world-outliner":
                result = server.handle_tool_call("editor_get_world_outliner", {})
                print_result(result, not args.json)
            
            elif args.command == "run-python":
                result = server.handle_tool_call("editor_run_python", {"code": args.code})
                print_result(result, not args.json)
            
            elif args.command == "console":
                result = server.handle_tool_call("editor_console_command", {"command": args.console_cmd})
                print_result(result, not args.json)
    
    except KeyboardInterrupt:
        print("\nInterrupted.")
    except Exception as e:
        if hasattr(args, "command") and args.command:
            print(f"Error while executing '{args.command}': {e}")
        else:
            print(f"Error during operation: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
